"""Una mano (presa): la carta di chi apre, la risposta e il seme di briscola."""
from __future__ import annotations

from dataclasses import dataclass

from briscola.core.card import Card, Suit


@dataclass(frozen=True, slots=True)
class Trick:
    lead: Card        # carta del giocatore di mano
    response: Card    # carta di risposta
    briscola: Suit    # seme di briscola della partita

    def __post_init__(self) -> None:
        if self.lead == self.response:
            raise ValueError("Le due carte di una mano devono essere diverse")

    def leader_wins(self) -> bool:
        """True se prende chi ha aperto la mano."""
        if self.lead.suit == self.response.suit:
            # Stesso seme: carte distinte hanno forza distinta, nessun pareggio.
            return self.lead.strength > self.response.strength
        # Semi diversi: la risposta prende solo se è briscola.
        return self.response.suit != self.briscola

    def winner(self) -> Card:
        return self.lead if self.leader_wins() else self.response

    @property
    def points(self) -> int:
        """Punti della mano, assegnati a chi prende."""
        return self.lead.points + self.response.points
