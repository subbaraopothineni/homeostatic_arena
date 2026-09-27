"""Minimal controls for the two markers that the plain reflexes did not pass.

POST-HOC (added after the pre-registered studies, in response to the objection
that the plain reflexes were never designed to attempt these markers). Each
control is a reflex from agents/reflex.py plus exactly one extra element:

- MotivationalReflex ("reflex_motivational"): the thermotactic reflex with its
  withdrawal suppressed while energy is critically low (< 0.2). One extra
  threshold on an interoceptive channel; still no memory. Target marker:
  motivational trade-off.
- SensitizingReflex ("reflex_sensitizing"): the nociceptive reflex plus one bit
  of state, set by the first harmful stimulus (nociceptor > 0.5) and never
  reset within the episode. While set, the agent also withdraws when the
  ambient temperature is above 35 C and rising, i.e. harm lowers its
  withdrawal threshold (non-associative sensitization). Target marker:
  sensitization.
"""
from __future__ import annotations

import numpy as np

from agents.reflex import _I, ReflexAgent


class MotivationalReflex(ReflexAgent):
    """Thermotactic reflex whose withdrawal is vetoed by critically low energy."""

    NEED_ENERGY = 0.2

    def __init__(self, seed: int | None = None):
        super().__init__("thermotactic", seed)

    def act(self, obs: np.ndarray, info: dict | None = None) -> np.ndarray:
        self._energy = float(obs[_I["energy"]])
        return super().act(obs, info)

    def withdrawal_triggered(self, nociceptor: float, ambient_c: float) -> bool:
        if self._energy < self.NEED_ENERGY:
            return False
        return super().withdrawal_triggered(nociceptor, ambient_c)


class SensitizingReflex(ReflexAgent):
    """Nociceptive reflex with one bit of state that lowers its withdrawal threshold after harm."""

    HARM_NOCICEPTOR = 0.5         # same threshold that defines a harmful encounter

    def __init__(self, seed: int | None = None):
        super().__init__("nociceptive", seed)

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self.sensitized = False

    def withdrawal_triggered(self, nociceptor: float, ambient_c: float) -> bool:
        if nociceptor > self.HARM_NOCICEPTOR:
            self.sensitized = True
        if super().withdrawal_triggered(nociceptor, ambient_c):
            return True
        return self.sensitized and self._heat_rising(ambient_c) and ambient_c > self.THERMAL_TRIGGER_C
