"""Giocatore: mano e carte prese. Il punteggio è derivato, mai salvato a parte."""
from __future__ import annotations

from dataclasses import dataclass, field

from briscola.core.card import Card


@dataclass(eq=False)
class Player:
    name: str
    hand: list[Card] = field(default_factory=list)
    captured: list[Card] = field(default_factory=list)

    @property
    def score(self) -> int:
        return sum(card.points for card in self.captured)
