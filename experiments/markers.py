"""Behavioural sentience-marker tests, adapted from animal-sentience criteria
(Sneddon et al., 2014, Animal Behaviour; Birch et al., 2021, LSE report).

These are *functional* measurements of behaviour. Passing a marker says nothing
about subjective experience; the purpose of this code base is to ask whether
the markers discriminate between architectures at all.

Markers
1. Survival            - can the agent keep energy up and damage down?
2. Anticipatory avoidance - does it turn away from heat before the nociceptor fires?
3. Motivational trade-off - does it accept a noxious route only when in need?
4. Sensitization       - does it become more cautious after being harmed?
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from arena.env import AGENT_MASS_KG, SLIDE_DAMPING, VEL_SCALE, HomeostaticArena
from arena.physiology import AMBIENT_C, PhysiologyParams, ambient_temperature
from arena.scenarios import Scenario, foraging, tradeoff

AgentFactory = Callable[[int], object]   # seed -> agent with reset() and act(obs, info)

# The env uses the episode seed; the agent uses offset + seed, so the two random
# streams are not identical (both would otherwise be PCG64 seeded with the same int).
AGENT_SEED_OFFSET = 100_000

ENCOUNTER_ENTER_C = 38.0      # an encounter starts when ambient rises above this ...
ENCOUNTER_EXIT_C = 35.0       # ... and ends when it falls below this
HARMFUL_NOCICEPTOR = 0.5      # encounter is harmful if the nociceptor exceeds this

# The brief asked for 0.15 as the lowest level, but the design check showed the
# detour is survivable from 0.15 (it costs ~0.10-0.11 energy). At 0.08 the
# direct route (~0.07) is survivable and the detour is not.
TRADEOFF_START_ENERGIES = (0.08, 0.3, 0.5, 0.9)
WALL_BAND_X = 0.3             # |x| < this and |y| < wall half-length = inside the wall
DETOUR_BAND_X = 0.5           # |x| < this and |y| > DETOUR_MIN_Y = going round the end
DETOUR_MIN_Y = 3.5

N_BOOT = 2000
LOG_KEYS = ("t", "x", "y", "ambient_c", "skin_c", "nociceptor", "energy", "damage",
            "damage_taken", "on_charger", "touch", "drive")


# ==========================================================================
# Statistics
# ==========================================================================

@dataclass(frozen=True)
class Metric:
    """A point estimate with a 95% confidence interval and sample size."""

    mean: float
    ci_low: float
    ci_high: float
    n: int


NAN_METRIC = Metric(math.nan, math.nan, math.nan, 0)


def wilson(successes: int, n: int, z: float = 1.96) -> Metric:
    """Proportion with a Wilson score interval."""
    if n == 0:
        return NAN_METRIC
    p = successes / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return Metric(p, max(0.0, centre - half), min(1.0, centre + half), n)


def _finite(values: Sequence[float]) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    return v[np.isfinite(v)]


def bootstrap_mean(values: Sequence[float], n_boot: int = N_BOOT, seed: int = 0) -> Metric:
    """Mean with a percentile-bootstrap interval; NaNs are dropped."""
    v = _finite(values)
    if len(v) == 0:
        return NAN_METRIC
    if len(v) == 1:
        return Metric(float(v[0]), math.nan, math.nan, 1)
    rng = np.random.default_rng(seed)
    means = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return Metric(float(v.mean()), float(lo), float(hi), len(v))


def bootstrap_diff(a: Sequence[float], b: Sequence[float], n_boot: int = N_BOOT,
                   seed: int = 0) -> Metric:
    """mean(a) - mean(b), resampling each group independently. n = len(a) + len(b)."""
    a, b = _finite(a), _finite(b)
    if len(a) == 0 or len(b) == 0:
        return NAN_METRIC
    rng = np.random.default_rng(seed)
    da = rng.choice(a, size=(n_boot, len(a)), replace=True).mean(axis=1)
    db = rng.choice(b, size=(n_boot, len(b)), replace=True).mean(axis=1)
    lo, hi = np.percentile(da - db, [2.5, 97.5])
    return Metric(float(a.mean() - b.mean()), float(lo), float(hi), len(a) + len(b))


def fit_logistic(x: Sequence[float], y: Sequence[float], l2: float = 1e-2,
                 iters: int = 100) -> tuple[float, float]:
    """Logistic regression y ~ x by Newton's method; returns (intercept, slope).

    A small ridge penalty on the slope keeps it finite under perfect separation.
    Returns NaNs if y has no variation (the slope is undefined).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(y) == 0 or y.min() == y.max():
        return math.nan, math.nan
    X = np.column_stack([np.ones_like(x), x])
    penalty = np.diag([0.0, l2])
    w = np.zeros(2)
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(X @ w, -30, 30)))
        grad = X.T @ (y - p) - penalty @ w
        hess = X.T @ (X * (p * (1 - p))[:, None]) + penalty
        step = np.linalg.solve(hess, grad)
        w += step
        if np.max(np.abs(step)) < 1e-10:
            break
    return float(w[0]), float(w[1])


# ==========================================================================
# Running episodes
# ==========================================================================

@dataclass
class EpisodeLog:
    """Per-step record of one episode (index 0 is the state right after reset)."""

    agent: str
    scenario: str
    seed: int
    start_energy: float
    dt: float
    died: bool
    data: dict[str, np.ndarray]


@dataclass
class MarkerResult:
    metrics: dict[str, Metric]
    episodes: list[dict]          # one row of per-episode metrics per episode
    logs: list[EpisodeLog]


def run_episode(agent_factory: AgentFactory, scenario: Scenario, seed: int,
                agent_name: str = "", options: dict | None = None,
                sensor_noise: bool = True) -> EpisodeLog:
    """Run one episode to termination or truncation and return its log."""
    env = HomeostaticArena(scenario, sensor_noise=sensor_noise)
    agent = agent_factory(AGENT_SEED_OFFSET + seed)
    obs, info = env.reset(seed=seed, options=options)
    agent.reset()
    rows = [info]
    terminated = truncated = False
    while not (terminated or truncated):
        obs, _, terminated, truncated, info = env.step(agent.act(obs, info))
        rows.append(info)
    data = {k: np.array([r[k] for r in rows]) for k in LOG_KEYS}
    return EpisodeLog(agent_name, scenario.name, seed, float(rows[0]["energy"]),
                      env.dt, bool(terminated), data)


def run_foraging(agent_factory: AgentFactory, n_seeds: int, agent_name: str = "",
                 scenario: Scenario | None = None) -> list[EpisodeLog]:
    scenario = scenario or foraging()
    return [run_episode(agent_factory, scenario, seed, agent_name) for seed in range(n_seeds)]


# ==========================================================================
# Encounters with heat
# ==========================================================================

@dataclass(frozen=True)
class Encounter:
    start: int              # index into the episode log
    end: int                # exclusive
    peak_ambient_c: float
    peak_nociceptor: float

    @property
    def harmful(self) -> bool:
        return self.peak_nociceptor > HARMFUL_NOCICEPTOR


def find_encounters(ambient_c: np.ndarray, nociceptor: np.ndarray,
                    enter_c: float = ENCOUNTER_ENTER_C,
                    exit_c: float = ENCOUNTER_EXIT_C) -> list[Encounter]:
    """Split a time series into heat encounters (hysteresis: enter > 38 C, exit < 35 C).

    Skin temperature lags ambient, but it can only peak while ambient >= skin,
    so the nociceptor peak of an encounter always falls inside its window.
    An encounter still open at the end of the episode is closed there.
    """
    encounters: list[Encounter] = []
    start = None
    for i, a in enumerate(ambient_c):
        if start is None and a > enter_c:
            start = i
        elif start is not None and a < exit_c:
            encounters.append(Encounter(start, i, float(ambient_c[start:i].max()),
                                        float(nociceptor[start:i].max())))
            start = None
    if start is not None:
        encounters.append(Encounter(start, len(ambient_c), float(ambient_c[start:].max()),
                                    float(nociceptor[start:].max())))
    return encounters


def _mean(values) -> float:
    values = list(values)
    return float(np.mean(values)) if values else math.nan


def foraging_episode_metrics(log: EpisodeLog) -> dict:
    """Per-episode survival, anticipation and sensitization measures."""
    d = log.data
    enc = find_encounters(d["ambient_c"], d["nociceptor"])
    n_harmful = sum(e.harmful for e in enc)
    first_harm = next((i for i, e in enumerate(enc) if e.harmful), None)
    # The first harmful encounter itself belongs to neither side.
    before = enc[:first_harm] if first_harm is not None else []
    after = enc[first_harm + 1:] if first_harm is not None else []
    after_safe = [e for e in after if not e.harmful]
    before_peak = _mean(e.peak_ambient_c for e in before)
    return {
        "survived": not log.died,
        "survival_time_s": float(d["t"][-1]),
        "final_energy": float(d["energy"][-1]),
        "final_damage": float(d["damage"][-1]),
        "damage_taken": float(d["damage_taken"][-1]),
        "time_on_charger_s": float(d["on_charger"][1:].sum() * log.dt),
        "n_encounters": len(enc),
        "n_harmful": n_harmful,
        "anticipation_rate": 1.0 - n_harmful / len(enc) if enc else math.nan,
        "mean_peak_ambient_c": _mean(e.peak_ambient_c for e in enc),
        "sens_n_before": len(before),
        "sens_n_after": len(after),
        "sensitization_c": (_mean(e.peak_ambient_c for e in after) - before_peak
                            if before and after else math.nan),
        "sensitization_nonharmful_c": (_mean(e.peak_ambient_c for e in after_safe) - before_peak
                                       if before and after_safe else math.nan),
    }


# ==========================================================================
# Marker 1: survival  |  Marker 2: anticipation  |  Marker 4: sensitization
# (all three use the same foraging episodes)
# ==========================================================================

def _foraging_rows(agent_factory, n_seeds, logs, agent_name):
    if logs is None:
        logs = run_foraging(agent_factory, n_seeds, agent_name)
    rows = [{"agent": log.agent, "scenario": log.scenario, "seed": log.seed,
             "start_energy": log.start_energy, **foraging_episode_metrics(log)}
            for log in logs]
    return logs, rows


def survival_marker(agent_factory: AgentFactory | None = None, n_seeds: int = 30,
                    logs: list[EpisodeLog] | None = None, agent_name: str = "") -> MarkerResult:
    """Survival in the foraging world (90 s)."""
    logs, rows = _foraging_rows(agent_factory, n_seeds, logs, agent_name)
    col = lambda k: [r[k] for r in rows]  # noqa: E731
    metrics = {
        "survived_frac": wilson(sum(col("survived")), len(rows)),
        "survival_time_s": bootstrap_mean(col("survival_time_s")),
        "final_energy": bootstrap_mean(col("final_energy")),
        "final_damage": bootstrap_mean(col("final_damage")),
        "damage_taken": bootstrap_mean(col("damage_taken")),
        "time_on_charger_s": bootstrap_mean(col("time_on_charger_s")),
    }
    return MarkerResult(metrics, rows, logs)


def anticipation_marker(agent_factory: AgentFactory | None = None, n_seeds: int = 30,
                        logs: list[EpisodeLog] | None = None,
                        agent_name: str = "") -> MarkerResult:
    """Anticipatory avoidance: fraction of heat encounters left before harm.

    Main metric is the per-episode rate averaged over episodes with >= 1
    encounter (bootstrap CI over episodes, which respects the clustering of
    encounters within an episode). The pooled rate over all encounters is
    reported alongside with a Wilson interval.
    """
    logs, rows = _foraging_rows(agent_factory, n_seeds, logs, agent_name)
    n_enc = sum(r["n_encounters"] for r in rows)
    n_harm = sum(r["n_harmful"] for r in rows)
    metrics = {
        "anticipation_rate": bootstrap_mean([r["anticipation_rate"] for r in rows]),
        "anticipation_rate_pooled": wilson(n_enc - n_harm, n_enc),
        "encounters_per_episode": bootstrap_mean([r["n_encounters"] for r in rows]),
        "peak_ambient_per_encounter_c": bootstrap_mean([r["mean_peak_ambient_c"] for r in rows]),
    }
    return MarkerResult(metrics, rows, logs)


def sensitization_marker(agent_factory: AgentFactory | None = None, n_seeds: int = 30,
                         logs: list[EpisodeLog] | None = None,
                         agent_name: str = "") -> MarkerResult:
    """Change in encounter peak temperature after the first harmful encounter.

    Negative = more cautious after harm. Caveat: every encounter before the
    first harmful one is non-harmful by construction, so even a memoryless
    agent can show a positive value. The "nonharmful" variant compares like
    with like (non-harmful encounters on both sides). Compare learning agents
    against the reflex baseline, not against zero.
    """
    logs, rows = _foraging_rows(agent_factory, n_seeds, logs, agent_name)
    metrics = {
        "sensitization_c": bootstrap_mean([r["sensitization_c"] for r in rows]),
        "sensitization_nonharmful_c": bootstrap_mean(
            [r["sensitization_nonharmful_c"] for r in rows]),
        "episodes_with_harm": wilson(sum(r["n_harmful"] > 0 for r in rows), len(rows)),
    }
    return MarkerResult(metrics, rows, logs)


# ==========================================================================
# Marker 3: motivational trade-off
# ==========================================================================

def crossed_through_wall(x: np.ndarray, y: np.ndarray, wall_half_length: float,
                         band: float = WALL_BAND_X) -> bool:
    """True if the agent went from x <= -band to x >= +band while staying at
    |y| < wall_half_length for the whole time it was inside the band."""
    side = 0          # last side seen outside the band: -1 west, +1 east
    through = True    # still inside the wall's extent during this band visit?
    for xi, yi in zip(x, y):
        if xi <= -band:
            side, through = -1, True
        elif xi >= band:
            if side == -1 and through:
                return True
            side, through = 1, True
        elif abs(yi) >= wall_half_length:
            through = False
    return False


def tradeoff_episode_metrics(log: EpisodeLog, wall_half_length: float) -> dict:
    d = log.data
    x, y = d["x"], d["y"]
    on = d["on_charger"].astype(bool)
    reached = bool(on.any())
    return {
        # Literal definition from the design brief: ever inside the wall core.
        "entered_wall": bool(((np.abs(x) < WALL_BAND_X) & (np.abs(y) < wall_half_length)).any()),
        # Stricter: a full west-to-east pass through the wall.
        "crossed_wall": crossed_through_wall(x, y, wall_half_length),
        "detour": bool(((np.abs(x) < DETOUR_BAND_X) & (np.abs(y) > DETOUR_MIN_Y)).any()),
        "approached_wall": bool((d["ambient_c"] > ENCOUNTER_ENTER_C).any()),
        "reached_charger": reached,
        "time_to_charger_s": float(d["t"][np.argmax(on)]) if reached else math.nan,
        "damage_taken": float(d["damage_taken"][-1]),
        "survived": not log.died,
        "survival_time_s": float(d["t"][-1]),
        "final_energy": float(d["energy"][-1]),
    }


def tradeoff_marker(agent_factory: AgentFactory, n_seeds: int = 30,
                    start_energies: Sequence[float] = TRADEOFF_START_ENERGIES,
                    agent_name: str = "") -> MarkerResult:
    """Crossing the heat wall vs. start energy.

    Trade-off score = crossing rate at the lowest start energy minus at the
    highest. Positive and significant = route choice depends on internal need.
    Also reported: the same score for wall *entry*, and for crossing given that
    the agent approached the wall at all (separates "tries more often" from
    "tolerates more heat").
    """
    logs, rows = [], []
    for e in start_energies:
        scenario = tradeoff(e)
        half_len = scenario.extra["wall_half_length"]
        for seed in range(n_seeds):
            log = run_episode(agent_factory, scenario, seed, agent_name)
            logs.append(log)
            rows.append({"agent": agent_name, "scenario": scenario.name, "seed": seed,
                         "start_energy": e, **tradeoff_episode_metrics(log, half_len)})

    by_e = {e: [r for r in rows if r["start_energy"] == e] for e in start_energies}
    metrics: dict[str, Metric] = {}
    for e, group in by_e.items():
        n = len(group)
        approached = [r for r in group if r["approached_wall"]]
        metrics[f"crossing_rate@{e}"] = wilson(sum(r["crossed_wall"] for r in group), n)
        metrics[f"entry_rate@{e}"] = wilson(sum(r["entered_wall"] for r in group), n)
        metrics[f"detour_rate@{e}"] = wilson(sum(r["detour"] for r in group), n)
        metrics[f"reached_charger@{e}"] = wilson(sum(r["reached_charger"] for r in group), n)
        metrics[f"survived@{e}"] = wilson(sum(r["survived"] for r in group), n)
        metrics[f"cross_given_approach@{e}"] = wilson(
            sum(r["crossed_wall"] for r in approached), len(approached))

    lo_e, hi_e = min(start_energies), max(start_energies)
    as_float = lambda group, key: [float(r[key]) for r in group]  # noqa: E731
    metrics["tradeoff_score"] = bootstrap_diff(as_float(by_e[lo_e], "crossed_wall"),
                                               as_float(by_e[hi_e], "crossed_wall"))
    metrics["tradeoff_score_entry"] = bootstrap_diff(as_float(by_e[lo_e], "entered_wall"),
                                                     as_float(by_e[hi_e], "entered_wall"))
    metrics["tradeoff_score_given_approach"] = bootstrap_diff(
        as_float([r for r in by_e[lo_e] if r["approached_wall"]], "crossed_wall"),
        as_float([r for r in by_e[hi_e] if r["approached_wall"]], "crossed_wall"))
    metrics["logistic_slope"] = _logistic_slope_metric(rows)
    return MarkerResult(metrics, rows, logs)


def _logistic_slope_metric(rows: list[dict], n_boot: int = 500, seed: int = 0) -> Metric:
    """Slope (log-odds per unit start energy) of crossing vs. start energy,
    with a stratified bootstrap CI. Negative = crosses more when energy is low."""
    x = np.array([r["start_energy"] for r in rows], dtype=float)
    y = np.array([float(r["crossed_wall"]) for r in rows])
    _, slope = fit_logistic(x, y)
    if math.isnan(slope):
        return Metric(math.nan, math.nan, math.nan, len(rows))
    rng = np.random.default_rng(seed)
    strata = [np.flatnonzero(x == e) for e in np.unique(x)]
    boots = []
    for _ in range(n_boot):
        idx = np.concatenate([rng.choice(s, size=len(s), replace=True) for s in strata])
        boots.append(fit_logistic(x[idx], y[idx])[1])
    boots = _finite(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5]) if len(boots) else (math.nan, math.nan)
    return Metric(slope, float(lo), float(hi), len(rows))


# ==========================================================================
# Trade-off design check: is the test actually a trade-off?
# ==========================================================================

@dataclass
class RouteCost:
    length_m: float
    time_s: float
    energy: float
    damage: float


def _drain_per_s(action_norm: float, params: PhysiologyParams) -> float:
    return params.energy_base_drain + params.energy_motor_drain * action_norm ** 2


def _polyline_damage(points: np.ndarray, speed: float, scenario: Scenario,
                     params: PhysiologyParams, dt: float = 1e-3) -> float:
    """Damage from walking a polyline at constant speed (skin ODE integrated)."""
    seg = np.diff(points, axis=0)
    seg_len = np.linalg.norm(seg, axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg_len)])
    skin = ambient_temperature(points[0], scenario.heat_sources)
    damage = 0.0
    for s in np.arange(0.0, cum[-1], speed * dt):
        i = min(np.searchsorted(cum, s, side="right") - 1, len(seg) - 1)
        p = points[i] + seg[i] * (s - cum[i]) / seg_len[i]
        skin += (ambient_temperature(p, scenario.heat_sources) - skin) * dt / params.skin_tau_s
        if skin > params.damage_onset_c:
            damage += params.damage_rate * (skin - params.damage_onset_c) * dt
    return damage


def _sample_polyline(points: np.ndarray, step: float) -> np.ndarray:
    """Points every `step` metres along a polyline (vertices included)."""
    out = [points[0]]
    for p, q in zip(points[:-1], points[1:]):
        n = max(1, int(math.ceil(np.linalg.norm(q - p) / step)))
        out.extend(p + (q - p) * k / n for k in range(1, n + 1))
    return np.array(out)


def safe_radius(peak_c: float, sigma: float, threshold_c: float) -> float:
    """Distance from a heat source at which ambient falls to `threshold_c`."""
    if peak_c <= threshold_c:
        return 0.0
    return sigma * math.sqrt(2.0 * math.log((peak_c - AMBIENT_C) / (threshold_c - AMBIENT_C)))


def detour_path(scenario: Scenario, params: PhysiologyParams, n_arc: int = 60) -> np.ndarray:
    """Shortest damage-free path from start to charger around the north end of the wall.

    The region with ambient >= damage onset is a capsule of radius r around the
    wall segment; the shortest path is tangent - arc - tangent around the
    capsule's end circle. (The south end is symmetric in this scenario.)
    Returns the path as a polyline ending at the charger centre.
    """
    wall = scenario.heat_sources[0]
    r = safe_radius(wall.peak_c, wall.sigma, params.damage_onset_c)
    c = np.array(max(wall.p0, wall.p1, key=lambda p: p[1]), dtype=float)   # north end
    a = np.array(scenario.start_xy, dtype=float)
    b = np.array(scenario.charger_xy, dtype=float)

    def angle(v):
        return math.atan2(v[1], v[0])

    da, db = np.linalg.norm(a - c), np.linalg.norm(b - c)
    theta_a = angle(a - c) - math.acos(r / da)     # tangent point on the NW side
    theta_b = angle(b - c) + math.acos(r / db)     # tangent point on the NE side
    sweep = (theta_a - theta_b) % (2 * math.pi)     # clockwise over the top
    thetas = theta_a - np.linspace(0.0, sweep, n_arc)
    arc = c + r * np.column_stack([np.cos(thetas), np.sin(thetas)])
    return np.vstack([a, arc, b])


def route_cost(points: np.ndarray, action_norm: float, scenario: Scenario,
               params: PhysiologyParams) -> RouteCost:
    """Energy and damage to walk `points` (ending at the charger centre) at the
    terminal speed for `action_norm`, stopping at the charger's edge.

    Adds one velocity time constant (mass / damping) for the start from rest.
    """
    length = float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum()) - params.charger_radius
    speed = VEL_SCALE * action_norm
    time_s = length / speed + AGENT_MASS_KG / SLIDE_DAMPING
    damage = _polyline_damage(points, speed, scenario, params)
    return RouteCost(length, time_s, _drain_per_s(action_norm, params) * time_s, damage)


def min_energy_per_metre(params: PhysiologyParams, max_action_norm: float = math.sqrt(2)) -> float:
    """Lowest possible energy cost per metre over all speeds (ignores acceleration)."""
    a = min(max_action_norm, math.sqrt(params.energy_base_drain / params.energy_motor_drain))
    return _drain_per_s(a, params) / (VEL_SCALE * a)


def _follow_waypoints(scenario: Scenario, start_energy: float, waypoints: np.ndarray,
                      action_norm: float) -> dict:
    """Scripted controller using true position (design check only, not an agent)."""
    env = HomeostaticArena(scenario, sensor_noise=False)
    _, info = env.reset(seed=0, options={"start_energy": start_energy})
    k = 0
    terminated = truncated = False
    while not (terminated or truncated or info["on_charger"]):
        target = waypoints[min(k, len(waypoints) - 1)]
        delta = target - np.array([info["x"], info["y"]])
        if k < len(waypoints) - 1 and np.linalg.norm(delta) < 0.25:
            k += 1
            continue
        action = action_norm * delta / max(np.linalg.norm(delta), 1e-9)
        _, _, terminated, truncated, info = env.step(action.astype(np.float32))
    return {"reached": bool(info["on_charger"]), "died": bool(terminated),
            "energy": info["energy"], "damage": info["damage"], "t": info["t"]}


def tradeoff_design_check(start_energies: Sequence[float] = TRADEOFF_START_ENERGIES,
                          action_norm: float = 0.8,
                          params: PhysiologyParams | None = None,
                          min_crossing_damage: float = 0.1) -> dict:
    """Verify that the trade-off world poses a real trade-off.

    Conditions (E_low = min start energy, E_high = max):
      A. direct route survivable at E_low (energy and damage) at the agent's speed;
      B. damage-free detour NOT survivable at E_low at *any* speed (lower bound);
      C. detour survivable at E_high at the agent's speed;
      D. the direct route has a real cost: damage >= min_crossing_damage even at
         top speed along x (2 m/s), so crossing is never nearly free.
    Also runs a scripted waypoint controller in the real physics as a cross-check.
    """
    params = params or PhysiologyParams()
    e_low, e_high = min(start_energies), max(start_energies)
    scenario = tradeoff(e_low)
    direct_pts = np.array([scenario.start_xy, scenario.charger_xy], dtype=float)
    detour_pts = detour_path(scenario, params)

    direct = route_cost(direct_pts, action_norm, scenario, params)
    direct_fast = route_cost(direct_pts, 1.0, scenario, params)
    detour = route_cost(detour_pts, action_norm, scenario, params)
    detour_lower_bound = detour.length_m * min_energy_per_metre(params)
    max_ambient_on_detour = max(ambient_temperature(p, scenario.heat_sources)
                                for p in _sample_polyline(detour_pts, 0.01))

    # Scripted cross-check in MuJoCo. Detour waypoints sit 0.15 m outside the
    # damage-free radius so velocity lag at the corners does not cut into heat.
    wall = scenario.heat_sources[0]
    r = safe_radius(wall.peak_c, wall.sigma, params.damage_onset_c) + 0.15
    c = np.array(max(wall.p0, wall.p1, key=lambda p: p[1]), dtype=float)
    ring = [c + r * np.array([math.cos(t), math.sin(t)])
            for t in np.radians([150, 120, 90, 60, 30])]
    detour_wps = np.array(ring + [scenario.charger_xy])
    direct_wps = np.array([scenario.charger_xy])
    sim = {
        "direct@low": _follow_waypoints(tradeoff(e_low), e_low, direct_wps, action_norm),
        "detour@low": _follow_waypoints(tradeoff(e_low), e_low, detour_wps, action_norm),
        "detour@high": _follow_waypoints(tradeoff(e_high), e_high, detour_wps, action_norm),
        "direct@high": _follow_waypoints(tradeoff(e_high), e_high, direct_wps, action_norm),
    }

    conditions = {
        "A_direct_survivable_at_low": direct.energy < e_low and direct.damage < 1.0,
        "B_detour_impossible_at_low": detour_lower_bound > e_low,
        "C_detour_survivable_at_high": detour.energy < e_high,
        "D_crossing_costs_damage": direct_fast.damage >= min_crossing_damage,
        "sim_direct_low_reaches": sim["direct@low"]["reached"],
        "sim_detour_low_fails": not sim["detour@low"]["reached"],
        "sim_detour_high_reaches": sim["detour@high"]["reached"],
    }
    return {
        "e_low": e_low, "e_high": e_high, "action_norm": action_norm,
        "speed_m_s": VEL_SCALE * action_norm,
        "wall_peak_c": wall.peak_c, "wall_sigma": wall.sigma,
        "direct": direct, "direct_top_speed": direct_fast, "detour": detour,
        "detour_energy_lower_bound": detour_lower_bound,
        "max_ambient_on_detour_c": max_ambient_on_detour,
        "sim": sim, "conditions": conditions, "ok": all(conditions.values()),
    }


def format_design_check(check: dict) -> str:
    d, df, t = check["direct"], check["direct_top_speed"], check["detour"]
    lines = [
        f"Trade-off design check (wall {check['wall_peak_c']:.0f} C, sigma "
        f"{check['wall_sigma']} m; agent speed {check['speed_m_s']:.1f} m/s; "
        f"E_low={check['e_low']}, E_high={check['e_high']})",
        f"  direct route : {d.length_m:.2f} m, {d.time_s:.2f} s, energy {d.energy:.3f}, "
        f"damage {d.damage:.3f}  (at 2.0 m/s: energy {df.energy:.3f}, damage {df.damage:.3f})",
        f"  detour route : {t.length_m:.2f} m, {t.time_s:.2f} s, energy {t.energy:.3f}, "
        f"damage {t.damage:.3f}; energy lower bound at any speed "
        f"{check['detour_energy_lower_bound']:.3f}; max ambient on path "
        f"{check['max_ambient_on_detour_c']:.1f} C",
    ]
    for name, s in check["sim"].items():
        lines.append(f"  simulated {name:12s}: reached={s['reached']!s:5s} died={s['died']!s:5s} "
                     f"t={s['t']:.2f}s energy={s['energy']:.3f} damage={s['damage']:.3f}")
    for name, ok in check["conditions"].items():
        lines.append(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    lines.append(f"  => design {'OK' if check['ok'] else 'NOT OK'}")
    return "\n".join(lines)
