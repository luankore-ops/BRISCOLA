"""Vista parziale dello stato: ciò che un giocatore può legittimamente sapere."""
from __future__ import annotations

from dataclasses import dataclass

from briscola.core.card import Card, Suit


@dataclass(frozen=True, slots=True)
class GameView:
    hand: tuple[Card, ...]           # la mia mano
    lead_card: Card | None           # carta dell'avversario da rispondere, se ha aperto lui
    briscola_card: Card              # carta scoperta a inizio partita
    deck_size: int
    opponent_hand_size: int          # solo quante carte ha, mai quali
    my_score: int
    opponent_score: int
    played: tuple[Card, ...]         # carte delle mani già concluse (informazione pubblica)

    @property
    def briscola(self) -> Suit:
        return self.briscola_card.suit
