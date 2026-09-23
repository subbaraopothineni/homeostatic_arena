"""Train the v0.2 recurrent agent with PPO on the drive-reduction reward.

Usage (from the repository root):
    python -m experiments.train_agent --variant FULL --seed 0 --out results/v02/models

The only learning signals are (1) the homeostatic drive-reduction reward
(v0.1 definition) and, unless the variant is NOFWD, (2) a self-supervised loss
for predicting the next observation. Hyperparameters are fixed in
docs/preregistration_v0.2.md, section 4.
"""
from __future__ import annotations

import argparse
import csv
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch

from agents.recurrent import VARIANTS, NetConfig, RecurrentActorCritic, save_model
from arena.agency import AgencyArena


@dataclass
class TrainConfig:
    total_steps: int = 3_000_000
    n_envs: int = 16
    rollout: int = 128
    gamma: float = 0.99
    gae_lambda: float = 0.95
    lr: float = 3e-4
    clip: float = 0.2
    epochs: int = 4
    minibatches: int = 4
    value_coef: float = 0.5
    entropy_coef: float = 0.001
    max_grad_norm: float = 0.5
    reward_scale: float = 10.0
    fwd_coef: float = 1.0


def make_net(variant: str, seed: int) -> RecurrentActorCritic:
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    torch.manual_seed(seed)
    return RecurrentActorCritic(NetConfig(efference=(variant != "NOEFF")))


def train(variant: str, seed: int, config: TrainConfig, out_path: Path | None = None,
          verbose: bool = True) -> tuple[RecurrentActorCritic, list[dict]]:
    """Train one run. UNTRAINED returns the initial network without training."""
    net = make_net(variant, seed)
    if variant == "NOFWD":
        config.fwd_coef = 0.0
    log: list[dict] = []
    if variant != "UNTRAINED":
        log = _ppo(net, seed, config, verbose)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        save_model(net, out_path, variant, seed, log, asdict(config))
        if log:
            with out_path.with_suffix(".csv").open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(log[0]), lineterminator="\n")
                writer.writeheader()
                writer.writerows(log)
    return net, log


def _ppo(net: RecurrentActorCritic, seed: int, cfg: TrainConfig, verbose: bool) -> list[dict]:
    n, T = cfg.n_envs, cfg.rollout
    D = net.config.obs_dim
    opt = torch.optim.Adam(net.parameters(), lr=cfg.lr)
    envs = [AgencyArena(seed=seed * 1000 + i) for i in range(n)]
    obs = np.stack([env.reset()[0] for env in envs])
    starts = np.ones(n, dtype=np.float32)          # 1 = first step of an episode
    h = net.initial_state(n)
    ep_return = np.zeros(n)
    ep_len = np.zeros(n, dtype=int)
    finished: list[tuple[float, float, bool]] = []  # (return, seconds, died)
    log: list[dict] = []
    steps, t0 = 0, time.perf_counter()
    n_updates = cfg.total_steps // (n * T)

    for update in range(1, n_updates + 1):
        b_obs = np.zeros((T, n, D), np.float32)
        b_next = np.zeros((T, n, D), np.float32)
        b_act = np.zeros((T, n, 2), np.float32)
        b_logp = np.zeros((T, n), np.float32)
        b_val = np.zeros((T, n), np.float32)
        b_rew = np.zeros((T, n), np.float32)
        b_done = np.zeros((T, n), np.float32)
        b_starts = np.zeros((T, n), np.float32)
        h0 = h.clone()

        # ------------------------------------------------------------ rollout
        for t in range(T):
            b_obs[t], b_starts[t] = obs, starts
            with torch.no_grad():
                h = net.step(torch.from_numpy(obs), h * (1.0 - torch.from_numpy(starts))[:, None])
                dist = net.policy(h)
                action = dist.sample()
                b_logp[t] = dist.log_prob(action).sum(-1).numpy()
                b_val[t] = net.value(h).numpy()
            b_act[t] = action.numpy()
            next_obs = np.empty_like(obs)
            for i, env in enumerate(envs):
                o2, r, term, trunc, _ = env.step(b_act[t, i])
                b_next[t, i] = o2
                reward = r * cfg.reward_scale
                if trunc and not term:            # bootstrap the value beyond the time limit
                    with torch.no_grad():
                        reward += cfg.gamma * float(net.value(net.step(
                            torch.from_numpy(o2)[None], h[i:i + 1])))
                b_rew[t, i] = reward
                ep_return[i] += r
                ep_len[i] += 1
                if term or trunc:
                    finished.append((ep_return[i], ep_len[i] * env.dt, bool(term)))
                    ep_return[i], ep_len[i] = 0.0, 0
                    b_done[t, i] = 1.0
                    o2 = env.reset()[0]
                next_obs[i] = o2
            obs = next_obs
            starts = b_done[t].copy()
            steps += n

        with torch.no_grad():
            h_last = net.step(torch.from_numpy(obs), h * (1.0 - torch.from_numpy(starts))[:, None])
            last_val = net.value(h_last).numpy()

        # ------------------------------------------------------------ GAE
        adv = np.zeros((T, n), np.float32)
        gae = np.zeros(n, np.float32)
        for t in reversed(range(T)):
            next_val = last_val if t == T - 1 else b_val[t + 1]
            nonterminal = 1.0 - b_done[t]
            delta = b_rew[t] + cfg.gamma * next_val * nonterminal - b_val[t]
            gae = delta + cfg.gamma * cfg.gae_lambda * nonterminal * gae
            adv[t] = gae
        ret = adv + b_val

        # ------------------------------------------------------------ update
        tt = lambda x: torch.from_numpy(x)  # noqa: E731
        o_all, next_all, a_all = tt(b_obs), tt(b_next), tt(b_act)
        a_clipped = a_all.clamp(-1.0, 1.0)             # the executed motor command
        stats = {"pg": [], "v": [], "fwd": [], "ent": [], "max_ratio_dev_first": None}
        for epoch in range(cfg.epochs):
            perm = np.random.default_rng(seed * 100_003 + update * 17 + epoch).permutation(n)
            for mb in np.array_split(perm, cfg.minibatches):
                hs = net.unroll(o_all[:, mb], h0[mb], tt(b_starts[:, mb]))
                dist = net.policy(hs)
                logp = dist.log_prob(a_all[:, mb]).sum(-1)
                ratio = torch.exp(logp - tt(b_logp[:, mb]))
                if stats["max_ratio_dev_first"] is None:   # sanity: must be ~0
                    stats["max_ratio_dev_first"] = float((ratio - 1).abs().max().detach())
                a_mb = tt(adv[:, mb])
                a_mb = (a_mb - a_mb.mean()) / (a_mb.std() + 1e-8)
                pg_loss = -torch.min(ratio * a_mb,
                                     ratio.clamp(1 - cfg.clip, 1 + cfg.clip) * a_mb).mean()
                v_loss = ((net.value(hs) - tt(ret[:, mb])) ** 2).mean()
                entropy = dist.entropy().sum(-1).mean()
                pred = net.predict_delta(hs, a_clipped[:, mb])
                fwd_loss = ((pred - (next_all[:, mb] - o_all[:, mb])) ** 2).mean()
                loss = (pg_loss + cfg.value_coef * v_loss - cfg.entropy_coef * entropy
                        + cfg.fwd_coef * fwd_loss)
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(net.parameters(), cfg.max_grad_norm)
                opt.step()
                for k, v in (("pg", pg_loss), ("v", v_loss), ("fwd", fwd_loss), ("ent", entropy)):
                    stats[k].append(float(v))

        recent = finished[-50:]
        row = {
            "update": update,
            "steps": steps,
            "fps": round(steps / (time.perf_counter() - t0)),
            "episodes": len(finished),
            "mean_return": float(np.mean([r for r, _, _ in recent])) if recent else float("nan"),
            "mean_seconds": float(np.mean([s for _, s, _ in recent])) if recent else float("nan"),
            "death_rate": float(np.mean([d for _, _, d in recent])) if recent else float("nan"),
            "pg_loss": float(np.mean(stats["pg"])),
            "value_loss": float(np.mean(stats["v"])),
            "fwd_loss": float(np.mean(stats["fwd"])),
            "no_change_mse": float(((b_next - b_obs) ** 2).mean()),
            "entropy": float(np.mean(stats["ent"])),
            "ratio_check": stats["max_ratio_dev_first"],
        }
        log.append(row)
        if verbose and (update % 20 == 0 or update == 1 or update == n_updates):
            print(f"[{update}/{n_updates}] steps={steps} fps={row['fps']} "
                  f"return={row['mean_return']:.3f} survive_s={row['mean_seconds']:.1f} "
                  f"death={row['death_rate']:.2f} fwd={row['fwd_loss']:.5f} "
                  f"nochange={row['no_change_mse']:.5f} ratio_check={row['ratio_check']:.1e}",
                  flush=True)
    return log


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--variant", choices=VARIANTS, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--steps", type=int, default=TrainConfig.total_steps)
    p.add_argument("--out", type=Path, default=Path("results/v02/models"))
    p.add_argument("--threads", type=int, default=1)
    args = p.parse_args()
    torch.set_num_threads(args.threads)
    cfg = TrainConfig(total_steps=args.steps)
    path = args.out / f"{args.variant}_seed{args.seed}.pt"
    t0 = time.perf_counter()
    train(args.variant, args.seed, cfg, path)
    print(f"saved {path} in {time.perf_counter() - t0:.0f} s")


if __name__ == "__main__":
    main()
