import dataclasses

import pytest

from briscola.core import Card, Rank, Suit

ALL_CARDS = [Card(s, r) for s in Suit for r in Rank]


def test_forty_unique_cards():
    assert len(ALL_CARDS) == 40
    assert len(set(ALL_CARDS)) == 40


@pytest.mark.parametrize(
    "rank, points",
    [
        (Rank.ASSO, 11), (Rank.TRE, 10), (Rank.RE, 4), (Rank.CAVALLO, 3),
        (Rank.FANTE, 2), (Rank.SETTE, 0), (Rank.SEI, 0), (Rank.CINQUE, 0),
        (Rank.QUATTRO, 0), (Rank.DUE, 0),
    ],
)
def test_points(rank, points):
    assert Card(Suit.COPPE, rank).points == points


def test_total_points_is_120():
    assert sum(c.points for c in ALL_CARDS) == 120


def test_strength_order_is_not_numeric_order():
    order = [Rank.ASSO, Rank.TRE, Rank.RE, Rank.CAVALLO, Rank.FANTE,
             Rank.SETTE, Rank.SEI, Rank.CINQUE, Rank.QUATTRO, Rank.DUE]
    strengths = [Card(Suit.SPADE, r).strength for r in order]
    assert strengths == sorted(strengths, reverse=True)
    assert len(set(strengths)) == 10
    assert Card(Suit.SPADE, Rank.TRE).strength > Card(Suit.SPADE, Rank.RE).strength


def test_card_is_immutable_and_hashable():
    card = Card(Suit.DENARI, Rank.ASSO)
    with pytest.raises(dataclasses.FrozenInstanceError):
        card.rank = Rank.DUE
    assert {card: 1}[Card(Suit.DENARI, Rank.ASSO)] == 1


def test_str():
    assert str(Card(Suit.BASTONI, Rank.CAVALLO)) == "Cavallo di bastoni"
