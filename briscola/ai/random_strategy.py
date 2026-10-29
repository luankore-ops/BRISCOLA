from __future__ import annotations

import random

from briscola.core import Card, GameView


class RandomStrategy:
    """Baseline: gioca una carta a caso. Serve da riferimento per le IA migliori."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def choose_card(self, view: GameView) -> Card:
        return self._rng.choice(view.hand)
