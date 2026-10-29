import random

import pytest

from briscola.core import Card, Deck, EmptyDeckError, Rank, Suit


def test_standard_deck_has_40_unique_cards():
    deck = Deck.standard(random.Random(0))
    assert len(deck) == 40
    assert len(set(deck.cards)) == 40


def test_same_seed_same_order():
    a = Deck.standard(random.Random(42))
    b = Deck.standard(random.Random(42))
    assert a.cards == b.cards


def test_different_seed_different_order():
    a = Deck.standard(random.Random(1))
    b = Deck.standard(random.Random(2))
    assert a.cards != b.cards


def test_shuffle_preserves_cards():
    deck = Deck.standard(random.Random(0))
    before = set(deck.cards)
    deck.shuffle(random.Random(7))
    assert set(deck.cards) == before
    assert len(deck) == 40


def test_draw_takes_from_top_and_shrinks_deck():
    deck = Deck.standard(random.Random(0))
    top = deck.cards[0]
    assert deck.draw() == top
    assert len(deck) == 39
    assert top not in deck.cards


def test_draw_from_empty_raises():
    with pytest.raises(EmptyDeckError):
        Deck().draw()


def test_put_bottom_is_drawn_last():
    deck = Deck([Card(Suit.COPPE, Rank.DUE), Card(Suit.COPPE, Rank.TRE)])
    briscola = Card(Suit.SPADE, Rank.ASSO)
    deck.put_bottom(briscola)
    deck.draw()
    deck.draw()
    assert deck.draw() == briscola
    assert len(deck) == 0
