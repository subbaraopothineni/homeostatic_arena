"""Agents share one interface: reset() and act(obs, info) -> action.

Agents decide from the observation vector only; `info` is for logging.
"""
from __future__ import annotations

from agents.random_agent import RandomAgent
from agents.reflex import ReflexAgent

AGENT_NAMES = ("random", "reflex_nociceptive", "reflex_thermotactic")


def make_agent(name: str, seed: int | None = None):
    """Build a fresh agent by name."""
    if name == "random":
        return RandomAgent(seed)
    if name == "reflex_nociceptive":
        return ReflexAgent("nociceptive", seed)
    if name == "reflex_thermotactic":
        return ReflexAgent("thermotactic", seed)
    raise ValueError(f"unknown agent {name!r}; choose from {AGENT_NAMES}")


__all__ = ["AGENT_NAMES", "RandomAgent", "ReflexAgent", "make_agent"]
