"""Pre-registered v0.2 tests (docs/preregistration_v0.2.md, section 5).

A "predictor" is anything that, step by step, observes and predicts the next
observation: the trained agents (through their forward model), UNTRAINED
networks, and two hand-built controls:
- NO-CHANGE predicts o(t+1) = o(t);
- COMPARATOR predicts a lamp toggle exactly when its own motion carries it into
  the pad (a mechanism known to be present: the positive control).

T2 trials drive both robots with scripted actions, so each condition presents
the same sensory situation; only the cause of the lamp change differs.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import torch

from agents.recurrent import RecurrentAgent, RecurrentActorCritic
from arena.agency import (
    OBS_INDEX,
    OTHER_CHANNELS,
    SELF_MOTION_CHANNELS,
    THERMAL_SLICE,
    AgencyArena,
)
from arena.env import AGENT_MASS_KG, MOTOR_GEAR, SLIDE_DAMPING, VEL_SCALE
from experiments.markers import Metric, bootstrap_diff, bootstrap_mean

WARMUP_STEPS = 20              # 1 s stationary before motion
MOTION_ACTION = 0.8
MAX_MOTION_STEPS = 60
POST_EVENT_STEPS = 41          # long enough for the lag-40 memory probe
TRIALS_PER_CONDITION = 40      # 20 with the lamp on, 20 off
JITTER_M = 0.1
T2_CONDITIONS = ("SELF", "OTHER", "SPONT", "NOEVENT", "SELF-OMIT", "OTHER-ONPAD",
                 "SPONT-ONPAD")
ABLATED_CONDITIONS = ("SELF", "OTHER", "SPONT")
ABLATIONS = ("none", "self-blind", "other-blind")
INTERO_CHANNELS = (OBS_INDEX["energy"], OBS_INDEX["damage"])

# Start positions (agent, other) and forced x-actions (agent, other) per condition.
_GEOMETRY = {
    "SELF":        ((-1.0, 0.0), (1.0, -0.9), MOTION_ACTION, -MOTION_ACTION),
    "OTHER":       ((-1.0, 0.9), (1.0, 0.0), MOTION_ACTION, -MOTION_ACTION),
    "SPONT":       ((-1.0, 0.9), (1.0, -0.9), MOTION_ACTION, -MOTION_ACTION),
    "NOEVENT":     ((-1.0, 0.9), (1.0, -0.9), MOTION_ACTION, -MOTION_ACTION),
    "SELF-OMIT":   ((-1.0, 0.0), (1.0, -0.9), MOTION_ACTION, -MOTION_ACTION),
    "OTHER-ONPAD": ((-0.2, 0.0), (1.0, 0.0), 0.0, -MOTION_ACTION),
    "SPONT-ONPAD": ((-0.2, 0.0), (1.0, -0.9), 0.0, -MOTION_ACTION),
}


# ==========================================================================
# Predictors
# ==========================================================================

class Predictor:
    """Interface: reset(); observe(obs); predict_next(action) -> o(t+1); state()."""
    name = "predictor"

    def reset(self) -> None: ...
    def bind(self, env: AgencyArena) -> None: ...
    def observe(self, obs: np.ndarray) -> None: ...
    def predict_next(self, action: np.ndarray) -> np.ndarray: ...
    def state(self) -> np.ndarray | None:
        return None


class NetworkPredictor(Predictor):
    """A (trained or untrained) recurrent agent's forward model and memory."""

    def __init__(self, net: RecurrentActorCritic, name: str):
        self.agent = RecurrentAgent(net)
        self.name = name

    def reset(self) -> None:
        self.agent.reset()

    def observe(self, obs):
        self._h = self.agent.observe(obs)

    def predict_next(self, action):
        return self.agent.predict_next(action)

    def state(self):
        return self._h


class NoChangePredictor(Predictor):
    name = "NO-CHANGE"

    def observe(self, obs):
        self._obs = np.asarray(obs, dtype=np.float32)

    def predict_next(self, action):
        return self._obs.copy()


class ComparatorPredictor(Predictor):
    """Hand-built positive control: predicts its own next position from position,
    velocity and motor command (exact first-order body dynamics), and predicts a
    lamp toggle exactly when that motion carries it into the pad. It is given
    privileged access to the lamp's appearance (via `env`), which the learning
    agent must learn."""
    name = "COMPARATOR"

    def bind(self, env: AgencyArena) -> None:
        self.env = env

    def observe(self, obs):
        self._obs = np.asarray(obs, dtype=np.float32)

    def predict_next(self, action):
        pred = self._obs.copy()
        h = self.env.scenario.half_size
        pos = np.array([self._obs[OBS_INDEX["pos_x"]], self._obs[OBS_INDEX["pos_y"]]]) * h
        vel = np.array([self._obs[OBS_INDEX["vel_x"]], self._obs[OBS_INDEX["vel_y"]]]) * VEL_SCALE
        tau = AGENT_MASS_KG / SLIDE_DAMPING
        v_term = MOTOR_GEAR / SLIDE_DAMPING * np.clip(np.asarray(action, float), -1, 1)
        decay = math.exp(-self.env.dt / tau)
        next_pos = pos + v_term * self.env.dt + (vel - v_term) * tau * (1 - decay)
        r = self.env.pad_radius
        entering = math.dist(pos, self.env.pad_xy) >= r > math.dist(next_pos, self.env.pad_xy)
        env = self.env
        # It does not know whether the switch works: an entry always predicts a toggle.
        if entering:
            env._set_lamp(not env.lamp_on)            # look up the toggled appearance ...
            pred[THERMAL_SLICE] = env.thermal_vision(next_pos)
            env._set_lamp(not env.lamp_on)            # ... and restore it
        else:
            pred[THERMAL_SLICE] = env.thermal_vision(next_pos)
        return pred


# ==========================================================================
# Trials
# ==========================================================================

@dataclass
class Trial:
    condition: str
    ablation: str
    lamp_on: bool
    index: int
    event_step: int | None = None        # step k: o(k+1) first shows the change
    rel_pe: float = math.nan
    abs_pe: float = math.nan
    agent_on_pad_after: bool = False
    causes: list = field(default_factory=list)
    states: dict = field(default_factory=dict)      # lag -> memory state
    raw_windows: dict = field(default_factory=dict)  # lag -> last 5 observations


def _thermal_pe(pred, actual, prev) -> tuple[float, float]:
    err = float(np.sum((pred[THERMAL_SLICE] - actual[THERMAL_SLICE]) ** 2))
    change = float(np.sum((prev[THERMAL_SLICE] - actual[THERMAL_SLICE]) ** 2))
    return err / change if change > 0 else math.nan, err


def _freeze(obs: np.ndarray, frozen: np.ndarray | None, channels: tuple[str, ...]):
    if frozen is None:
        return obs
    out = obs.copy()
    idx = [OBS_INDEX[c] for c in channels]
    out[idx] = frozen[idx]
    return out


def run_t2_trial(predictor: Predictor, condition: str, ablation: str, lamp_on: bool,
                 index: int, spont_step: int | None = None) -> Trial:
    """One scripted agency trial; returns prediction errors at the lamp change."""
    seed = 1_000_000 + 1000 * T2_CONDITIONS.index(condition) + index
    rng = np.random.default_rng(seed)
    agent_xy, other_xy, agent_ax, other_ax = _GEOMETRY[condition]
    agent_xy = tuple(np.add(agent_xy, rng.uniform(-JITTER_M, JITTER_M, 2)))
    other_xy = tuple(np.add(other_xy, rng.uniform(-JITTER_M, JITTER_M, 2)))
    if condition in ("SELF", "SELF-OMIT"):
        agent_xy = (agent_xy[0], float(np.clip(agent_xy[1], -0.1, 0.1)))
    env = AgencyArena(seed=seed)
    obs, _ = env.reset(options={"start_xy": agent_xy, "other_xy": other_xy, "lamp_on": lamp_on,
                                "start_energy": 0.9, "random_events": False,
                                "switch_enabled": condition != "SELF-OMIT"})
    predictor.bind(env)
    trial = Trial(condition, ablation, lamp_on, index)
    predictor.reset()
    frozen = None
    channels = SELF_MOTION_CHANNELS if ablation == "self-blind" else OTHER_CHANNELS
    window = [obs] * 5
    predictor.observe(obs)

    total = WARMUP_STEPS + MAX_MOTION_STEPS + POST_EVENT_STEPS
    for step in range(total):
        moving = step >= WARMUP_STEPS and (trial.event_step is None
                                           or step <= trial.event_step)
        action = np.array([agent_ax if moving else 0.0, 0.0], dtype=np.float32)
        env.set_other_action([other_ax if moving else 0.0, 0.0])
        if step == WARMUP_STEPS and ablation != "none":
            frozen = obs.copy()                        # freeze at the start of motion
        if spont_step is not None and step == spont_step and condition in ("SPONT", "SPONT-ONPAD"):
            env.schedule_toggle("spontaneous")
        pred = predictor.predict_next(action)
        prev = obs
        obs, _, _, _, info = env.step(action)
        seen = _freeze(obs, frozen, channels) if frozen is not None else obs

        if trial.event_step is None:
            toggled = [e for e in info["events"] if e["type"] == "lamp_toggle"]
            omitted = condition == "SELF-OMIT" and info["agent_on_pad"]
            no_event = condition == "NOEVENT" and spont_step is not None and step == spont_step
            if toggled or omitted or no_event:
                trial.event_step = step
                trial.causes = [e["cause"] for e in toggled]
                trial.rel_pe, trial.abs_pe = _thermal_pe(pred, obs, prev)
                trial.agent_on_pad_after = bool(info["agent_on_pad"])
        predictor.observe(seen)
        window = window[1:] + [seen]
        if trial.event_step is not None:
            lag = step - trial.event_step + 1
            if lag in (1, 10, 40):
                trial.states[lag] = predictor.state()
                trial.raw_windows[lag] = np.concatenate(window)
            if lag >= POST_EVENT_STEPS:
                break
        elif step >= WARMUP_STEPS + MAX_MOTION_STEPS:
            break
    return trial


def self_event_step(n: int = 20) -> int:
    """Median step at which the agent enters the pad in SELF trials (for SPONT timing)."""
    steps = [run_t2_trial(NoChangePredictor(), "SELF", "none", i % 2 == 0, i).event_step
             for i in range(n)]
    return int(np.median([s for s in steps if s is not None]))


def run_t2(predictor_factory, spont_step: int,
           trials: int = TRIALS_PER_CONDITION) -> list[Trial]:
    """All T2 conditions (and ablations) for one predictor."""
    out = []
    for condition in T2_CONDITIONS:
        ablations = ABLATIONS if condition in ABLATED_CONDITIONS else ("none",)
        for ablation in ablations:
            for i in range(trials):
                predictor = predictor_factory()
                out.append(run_t2_trial(predictor, condition, ablation, lamp_on=i % 2 == 0,
                                        index=i, spont_step=spont_step))
    return out


# ==========================================================================
# Hypotheses
# ==========================================================================

def _values(trials: list[Trial], condition: str, ablation: str = "none", key: str = "rel_pe"):
    return [getattr(t, key) for t in sorted(trials, key=lambda t: t.index)
            if t.condition == condition and t.ablation == ablation]


def _paired_increase(trials, condition, ablation):
    base = _values(trials, condition)
    ablated = _values(trials, condition, ablation)
    return [a - b for a, b in zip(ablated, base)]


def hypothesis_effects(trials: list[Trial]) -> dict[str, Metric]:
    """Effects for H1-H3 and secondary contrasts (positive = predicted direction)."""
    rel = lambda c, a="none": _values(trials, c, a)              # noqa: E731
    return {
        "H1_spont_minus_self": bootstrap_diff(rel("SPONT"), rel("SELF")),
        "H2_omit_minus_noevent": bootstrap_diff(_values(trials, "SELF-OMIT", key="abs_pe"),
                                                _values(trials, "NOEVENT", key="abs_pe")),
        "H3a_selfblind_interaction": bootstrap_diff(
            _paired_increase(trials, "SELF", "self-blind"),
            _paired_increase(trials, "OTHER", "self-blind")),
        "H3b_otherblind_interaction": bootstrap_diff(
            _paired_increase(trials, "OTHER", "other-blind"),
            _paired_increase(trials, "SELF", "other-blind")),
        "H3b_applicable_spont_minus_other": bootstrap_diff(rel("SPONT"), rel("OTHER")),
        "S1_other_minus_self": bootstrap_diff(rel("OTHER"), rel("SELF")),
    }


def passes(m: Metric) -> bool:
    """CI excludes 0 in the predicted (positive) direction."""
    return not math.isnan(m.ci_low) and m.ci_low > 0


def relpe_by_condition(trials: list[Trial]) -> dict[str, Metric]:
    out = {}
    for c in T2_CONDITIONS:
        for a in ABLATIONS:
            vals = _values(trials, c, a)
            if vals:
                key = c if a == "none" else f"{c}|{a}"
                out[key] = bootstrap_mean(vals)
    return out


def attribution_accuracy(trials: list[Trial]) -> dict[str, float]:
    """Self-attribution by two rules, on unablated trials with a lamp change:
    PE rule ("self" if relPE < 0.5) and POSITION RULE ("self" if on the pad)."""
    out = {}
    for rule in ("pe", "position"):
        for c in ("SELF", "OTHER", "SPONT", "OTHER-ONPAD", "SPONT-ONPAD"):
            ts = [t for t in trials if t.condition == c and t.ablation == "none"
                  and not math.isnan(t.rel_pe)]
            if not ts:
                continue
            says_self = [(t.rel_pe < 0.5) if rule == "pe" else t.agent_on_pad_after for t in ts]
            truth = c == "SELF"
            out[f"{rule}:{c}"] = float(np.mean([s == truth for s in says_self]))
    return out


# ==========================================================================
# T1: body vs world
# ==========================================================================

T1_CONDITIONS = ("WORLD", "BODY", "NONE")
T1_EVENT_STEP = 30


def run_t1_trial(predictor: Predictor, condition: str, lamp_on: bool, index: int) -> dict:
    seed = 2_000_000 + 1000 * T1_CONDITIONS.index(condition) + index
    rng = np.random.default_rng(seed)
    env = AgencyArena(seed=seed)
    obs, _ = env.reset(options={
        "start_xy": tuple(np.add((-2.5, -2.5), rng.uniform(-JITTER_M, JITTER_M, 2))),
        "other_xy": (-4.0, 4.0), "lamp_on": lamp_on, "start_energy": 0.9,
        "random_events": False})
    env.set_other_action([0.0, 0.0])
    predictor.bind(env)
    predictor.reset()
    predictor.observe(obs)
    zero = np.zeros(2, dtype=np.float32)
    row = {"condition": condition, "lamp_on": lamp_on, "index": index,
           "states": {}, "raw_windows": {}}
    window = [obs] * 5
    for step in range(T1_EVENT_STEP + 10):
        if step == T1_EVENT_STEP:
            if condition == "WORLD":
                env.schedule_toggle("spontaneous")
            elif condition == "BODY":
                env.schedule_shock()
        pred = predictor.predict_next(zero)
        prev = obs
        obs, _, _, _, info = env.step(zero)
        if step == T1_EVENT_STEP:
            err = (pred - obs) ** 2
            row["pe_intero"] = float(err[list(INTERO_CHANNELS)].sum())
            row["pe_extero"] = float(err[THERMAL_SLICE].sum())
            row["intero_share"] = row["pe_intero"] / (row["pe_intero"] + row["pe_extero"])
            row["body_affected"] = any(e["body_affected"] for e in info["events"])
            row["raw_change_intero"] = float(((obs - prev)[list(INTERO_CHANNELS)] ** 2).sum())
        predictor.observe(obs)
        window = window[1:] + [obs]
        lag = step - T1_EVENT_STEP + 1
        if lag in (1, 9):                    # memory for the exploratory probes
            row["states"][lag] = predictor.state()
            row["raw_windows"][lag] = np.concatenate(window)
    return row


def run_t1_behaviour(agent, condition: str, index: int, seconds: float = 5.0) -> dict:
    """Start energy 0.65; after the event the agent's own policy controls it."""
    seed = 3_000_000 + 1000 * T1_CONDITIONS.index(condition) + index
    rng = np.random.default_rng(seed)
    env = AgencyArena(seed=seed)
    obs, info = env.reset(options={
        "start_xy": tuple(np.add((-2.5, -2.5), rng.uniform(-JITTER_M, JITTER_M, 2))),
        "other_xy": (-4.0, 4.0), "lamp_on": index % 2 == 0, "start_energy": 0.65,
        "random_events": False})
    env.set_other_action([0.0, 0.0])
    agent.reset()
    zero = np.zeros(2, dtype=np.float32)
    for step in range(T1_EVENT_STEP + 1):
        agent.act(obs, info)                               # keeps its memory up to date
        if step == T1_EVENT_STEP:
            if condition == "WORLD":
                env.schedule_toggle("spontaneous")
            elif condition == "BODY":
                env.schedule_shock()
        obs, _, _, _, info = env.step(zero)
    start = math.dist(env.xy, env.scenario.charger_xy)
    for _ in range(int(seconds / env.dt)):
        obs, _, term, _, info = env.step(agent.act(obs, info))
        if term:
            break
    return {"condition": condition, "index": index,
            "toward_charger_m": start - math.dist(env.xy, env.scenario.charger_xy)}


# ==========================================================================
# Free-running episodes: competence gate and ecological check
# ==========================================================================

def free_running(net: RecurrentActorCritic, n_episodes: int, seed0: int) -> dict:
    """Agent's own deterministic policy with random events on. Returns forward-model
    error vs NO-CHANGE, survival, and relPE of naturally occurring lamp toggles."""
    agent = RecurrentAgent(net)
    fwd_err, nochange_err, survived, seconds = [], [], [], []
    natural = []                                   # (cause, relPE)
    for ep in range(n_episodes):
        env = AgencyArena(seed=seed0 + ep)
        obs, info = env.reset()
        agent.reset()
        done = False
        while not done:
            action = agent.act(obs, info)
            pred = agent.predict_next(action)
            prev = obs
            obs, _, term, trunc, info = env.step(action)
            fwd_err.append(float(np.mean((pred - obs) ** 2)))
            nochange_err.append(float(np.mean((prev - obs) ** 2)))
            for e in info["events"]:
                if e["type"] == "lamp_toggle" and len(info["events"]) == 1:
                    natural.append((e["cause"], _thermal_pe(pred, obs, prev)[0]))
            done = term or trunc
        survived.append(not term)
        seconds.append(info["t"])
    return {
        "fwd_mse": float(np.mean(fwd_err)),
        "nochange_mse": float(np.mean(nochange_err)),
        "survived_frac": float(np.mean(survived)),
        "survival_s": float(np.mean(seconds)),
        "natural": natural,
    }


@torch.no_grad()
def probe_accuracy(features: np.ndarray, labels: np.ndarray, folds: int = 5,
                   seed: int = 0, l2: float = 1e-3) -> float:
    """Cross-validated multinomial logistic regression accuracy (exploratory probes)."""
    rng = np.random.default_rng(seed)
    classes = {c: i for i, c in enumerate(sorted(set(labels)))}
    y = np.array([classes[c] for c in labels])
    order = rng.permutation(len(y))
    correct = 0
    for k in range(folds):
        test = order[k::folds]
        train = np.setdiff1d(order, test)
        mu, sd = features[train].mean(0), features[train].std(0) + 1e-6
        xtr = torch.tensor((features[train] - mu) / sd, dtype=torch.float32)
        xte = torch.tensor((features[test] - mu) / sd, dtype=torch.float32)
        ytr = torch.tensor(y[train])
        model = torch.nn.Linear(xtr.shape[1], len(classes))
        opt = torch.optim.LBFGS(model.parameters(), max_iter=200)

        def closure():
            opt.zero_grad()
            loss = torch.nn.functional.cross_entropy(model(xtr), ytr) + \
                l2 * (model.weight ** 2).sum()
            loss.backward()
            return loss

        with torch.enable_grad():
            opt.step(closure)
        correct += int((model(xte).argmax(1).numpy() == y[test]).sum())
    return correct / len(y)
