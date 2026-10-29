"""Carte della Briscola: semi, valori, punti e forza di presa.

Il core non conosce mazzi regionali né asset grafici: napoletano e piacentino
condividono semi e regole e differiscono solo per la grafica (livello UI).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum


class Suit(Enum):
    DENARI = "denari"
    COPPE = "coppe"
    SPADE = "spade"
    BASTONI = "bastoni"


class Rank(IntEnum):
    ASSO = 1
    DUE = 2
    TRE = 3
    QUATTRO = 4
    CINQUE = 5
    SEI = 6
    SETTE = 7
    FANTE = 8
    CAVALLO = 9
    RE = 10


# Punti validi in Briscola; i valori non elencati valgono 0 (totale mazzo: 120).
_POINTS: dict[Rank, int] = {
    Rank.ASSO: 11,
    Rank.TRE: 10,
    Rank.RE: 4,
    Rank.CAVALLO: 3,
    Rank.FANTE: 2,
}

# Dal più forte al più debole: l'ordine di presa NON coincide con il valore numerico.
_STRENGTH_ORDER: tuple[Rank, ...] = (
    Rank.ASSO,
    Rank.TRE,
    Rank.RE,
    Rank.CAVALLO,
    Rank.FANTE,
    Rank.SETTE,
    Rank.SEI,
    Rank.CINQUE,
    Rank.QUATTRO,
    Rank.DUE,
)
_STRENGTH: dict[Rank, int] = {
    rank: len(_STRENGTH_ORDER) - i for i, rank in enumerate(_STRENGTH_ORDER)
}


@dataclass(frozen=True, slots=True)
class Card:
    """Carta immutabile e hashable (utilizzabile in set e come chiave di dict)."""

    suit: Suit
    rank: Rank

    @property
    def points(self) -> int:
        return _POINTS.get(self.rank, 0)

    @property
    def strength(self) -> int:
        """Forza di presa tra carte dello stesso seme: più alto = più forte (1-10)."""
        return _STRENGTH[self.rank]

    def __str__(self) -> str:
        return f"{self.rank.name.capitalize()} di {self.suit.value}"
