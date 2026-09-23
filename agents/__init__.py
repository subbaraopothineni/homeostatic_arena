"""Agents share one interface: reset() and act(obs, info) -> action.

Agents decide from the observation vector only; `info` is for logging.
"""
from __future__ import annotations

from agents.random_agent import RandomAgent
from agents.reflex import ReflexAgent

# Default baseline set.
AGENT_NAMES = ("random", "reflex_nociceptive", "reflex_thermotactic")
# Reflexes with the withdrawal rule exactly as first specified (see agents/reflex.py).
LITERAL_REFLEX_NAMES = ("reflex_nociceptive_literal", "reflex_thermotactic_literal")
ALL_AGENT_NAMES = AGENT_NAMES + LITERAL_REFLEX_NAMES


def make_agent(name: str, seed: int | None = None):
    """Build a fresh agent by name."""
    if name == "random":
        return RandomAgent(seed)
    for mode in ("nociceptive", "thermotactic"):
        if name == f"reflex_{mode}":
            return ReflexAgent(mode, seed)
        if name == f"reflex_{mode}_literal":
            return ReflexAgent(mode, seed, withdrawal="literal")
    raise ValueError(f"unknown agent {name!r}; choose from {ALL_AGENT_NAMES}")


__all__ = ["AGENT_NAMES", "ALL_AGENT_NAMES", "LITERAL_REFLEX_NAMES", "RandomAgent",
           "ReflexAgent", "make_agent"]
