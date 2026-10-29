"""Mazzo da 40 carte con generatore casuale iniettabile (partite riproducibili)."""
from __future__ import annotations

import random
from collections import deque
from collections.abc import Iterable

from briscola.core.card import Card, Rank, Suit


class EmptyDeckError(IndexError):
    """Sollevata quando si pesca da un mazzo vuoto."""


class Deck:
    def __init__(self, cards: Iterable[Card] = ()) -> None:
        self._cards: deque[Card] = deque(cards)

    @classmethod
    def standard(cls, rng: random.Random | None = None) -> Deck:
        """Mazzo completo da 40 carte, mescolato con `rng` (default: nuovo Random)."""
        deck = cls(Card(suit, rank) for suit in Suit for rank in Rank)
        deck.shuffle(rng)
        return deck

    def shuffle(self, rng: random.Random | None = None) -> None:
        rng = rng or random.Random()
        cards = list(self._cards)
        rng.shuffle(cards)
        self._cards = deque(cards)

    def draw(self) -> Card:
        """Pesca la carta in cima al mazzo."""
        if not self._cards:
            raise EmptyDeckError("Il mazzo è vuoto")
        return self._cards.popleft()

    def put_bottom(self, card: Card) -> None:
        """Mette una carta in fondo al mazzo (usata per la briscola scoperta)."""
        self._cards.append(card)

    @property
    def cards(self) -> tuple[Card, ...]:
        """Copia di sola lettura, dalla cima al fondo."""
        return tuple(self._cards)

    def __len__(self) -> int:
        return len(self._cards)
