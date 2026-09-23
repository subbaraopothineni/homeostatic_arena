"""Design check for Study 2b: does the world make the agent's own action necessary?

Two scripted robots with privileged knowledge (lamp state, positions) live in a
candidate world:
- WAITER: goes to the charger when the lamp is off; otherwise waits at a safe
  spot next to it until someone or something else turns the lamp off.
- SWITCHER: whenever the lamp is on, walks to the switch pad and toggles it off
  itself; otherwise goes to the charger.

If the SWITCHER does not survive clearly better, the world does not make agency
necessary (as in Study 2, where the agents learned to wait).

Usage (from the repository root):
    python -m experiments.necessity_check
"""
from __future__ import annotations

import math
from multiprocessing import get_context

import numpy as np

from arena.agency import AgencyArena, agency
from experiments.markers import bootstrap_diff, wilson

SPEED = 0.8
WAIT_SPOT = (3.0, 1.3)          # 1.7 m from the lamp: ambient ~26.8 C
EPISODES = 100
CANDIDATES = {   # name: (other_pad_prob, spontaneous_rate_hz, start_energy_range)
    "A study2 (0.5, 1/20s, E 0.4-1.0)": (0.5, 1 / 20, (0.4, 1.0)),
    "B (0.1, 1/60s, E 0.4-1.0)": (0.1, 1 / 60, (0.4, 1.0)),
    "C (0.1, 1/60s, E 0.2-0.6)": (0.1, 1 / 60, (0.2, 0.6)),
    "D (0.05, 1/120s, E 0.2-0.6)": (0.05, 1 / 120, (0.2, 0.6)),
    "E = C + lamp on at start": (0.1, 1 / 60, (0.2, 0.6), 1.0),
    "F = D + lamp on at start": (0.05, 1 / 120, (0.2, 0.6), 1.0),
}
HOT_SPOT = (-2.0, 2.0)
AVOID_M = 1.8


def _toward(xy, target) -> np.ndarray:
    """Head for `target`, steering around the static hot spot."""
    d = np.subtract(target, xy)
    n = float(np.linalg.norm(d))
    if n < 0.05:
        return np.zeros(2, np.float32)
    v = d / n
    away = np.subtract(xy, HOT_SPOT)
    dist = float(np.linalg.norm(away))
    if dist < AVOID_M:
        v = v + 2.0 * (AVOID_M - dist) / AVOID_M * away / max(dist, 1e-6)
    return (SPEED * v / np.linalg.norm(v)).astype(np.float32)


def policy(kind: str, env: AgencyArena) -> np.ndarray:
    """Both robots charge only when below 90% energy and otherwise wait at a safe spot
    (parking on the charger would expose them to the lamp switching on)."""
    xy = env.xy
    if env.body.energy >= 0.9:
        return _toward(xy, WAIT_SPOT)
    if not env.lamp_on:
        return _toward(xy, env.scenario.charger_xy)
    if kind == "WAITER":
        return _toward(xy, WAIT_SPOT)
    if env._in_pad(xy):                     # on the pad but the lamp is on: step out, re-enter
        return _toward(xy, (0.9, 0.9))
    return _toward(xy, env.pad_xy)


def run(args) -> dict:
    name, kind = args
    pad_prob, spont, energy_range, *lamp = CANDIDATES[name]
    survived, self_toggles, energies, causes = [], [], [], {"energy": 0, "damage": 0}
    for ep in range(EPISODES):
        env = AgencyArena(agency(pad_prob, spont, energy_range, *lamp), seed=500_000 + ep)
        env.reset()
        done, term, info = False, False, {}
        n_self = 0
        while not done:
            _, _, term, trunc, info = env.step(policy(kind, env))
            n_self += sum(e["cause"] == "self" for e in info["events"])
            done = term or trunc
        survived.append(0.0 if term else 1.0)
        if term:
            causes["energy" if info["energy"] <= 0 else "damage"] += 1
        self_toggles.append(n_self)
        energies.append(info["energy"])
    return {"world": name, "policy": kind, "survived": survived, "causes": causes,
            "self_toggles": float(np.mean(self_toggles)), "final_energy": float(np.mean(energies))}


def main() -> None:
    jobs = [(w, k) for w in CANDIDATES for k in ("WAITER", "SWITCHER")]
    with get_context("fork").Pool(len(jobs)) as pool:
        res = {(r["world"], r["policy"]): r for r in pool.map(run, jobs)}
    print(f"{'world (other pad prob, spont rate)':34s} {'policy':9s} {'survived [95% CI]':24s} "
          f"{'self toggles/ep':>15s} {'final energy':>12s} {'deaths: energy/damage':>22s}")
    for w in CANDIDATES:
        for k in ("WAITER", "SWITCHER"):
            r = res[(w, k)]
            m = wilson(int(sum(r["survived"])), len(r["survived"]))
            print(f"{w:34s} {k:9s} {m.mean:.2f} [{m.ci_low:.2f}, {m.ci_high:.2f}]        "
                  f"{r['self_toggles']:15.2f} {r['final_energy']:12.3f} "
                  f"{r['causes']['energy']:>13d}/{r['causes']['damage']}")
        d = bootstrap_diff(res[(w, "SWITCHER")]["survived"], res[(w, "WAITER")]["survived"])
        print(f"{'':34s} SWITCHER − WAITER survival: {d.mean:+.2f} [{d.ci_low:+.2f}, {d.ci_high:+.2f}]")


if __name__ == "__main__":
    main()
