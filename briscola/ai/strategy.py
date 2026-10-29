"""Interfaccia comune delle IA: scelgono una carta vedendo solo una `GameView`."""
from __future__ import annotations

from typing import Protocol

from briscola.core import Card, GameView


class Strategy(Protocol):
    def choose_card(self, view: GameView) -> Card:
        """Restituisce una carta tra quelle di `view.hand`."""
        ...
