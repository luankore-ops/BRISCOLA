import pytest

from briscola.core import Card, Rank, Suit, Trick

B = Suit.DENARI  # seme di briscola nei test


def c(suit, rank):
    return Card(suit, rank)


def test_same_suit_higher_strength_wins_when_leader():
    t = Trick(c(Suit.COPPE, Rank.ASSO), c(Suit.COPPE, Rank.RE), B)
    assert t.leader_wins()
    assert t.winner() == t.lead


def test_same_suit_higher_strength_wins_when_responder():
    t = Trick(c(Suit.COPPE, Rank.RE), c(Suit.COPPE, Rank.ASSO), B)
    assert not t.leader_wins()
    assert t.winner() == t.response


def test_tre_beats_re_same_suit():
    t = Trick(c(Suit.SPADE, Rank.RE), c(Suit.SPADE, Rank.TRE), B)
    assert t.winner() == c(Suit.SPADE, Rank.TRE)


def test_briscola_response_beats_non_briscola_lead():
    t = Trick(c(Suit.COPPE, Rank.ASSO), c(B, Rank.DUE), B)
    assert not t.leader_wins()


def test_non_briscola_response_loses_to_briscola_lead():
    t = Trick(c(B, Rank.DUE), c(Suit.COPPE, Rank.ASSO), B)
    assert t.leader_wins()


def test_different_non_briscola_suits_leader_wins():
    t = Trick(c(Suit.COPPE, Rank.DUE), c(Suit.SPADE, Rank.ASSO), B)
    assert t.leader_wins()


def test_two_briscole_higher_strength_wins():
    t = Trick(c(B, Rank.CAVALLO), c(B, Rank.FANTE), B)
    assert t.winner() == c(B, Rank.CAVALLO)
    t = Trick(c(B, Rank.SETTE), c(B, Rank.TRE), B)
    assert t.winner() == c(B, Rank.TRE)


def test_points_sum_of_both_cards():
    t = Trick(c(Suit.COPPE, Rank.ASSO), c(Suit.COPPE, Rank.TRE), B)
    assert t.points == 21
    t = Trick(c(Suit.COPPE, Rank.DUE), c(Suit.SPADE, Rank.QUATTRO), B)
    assert t.points == 0


def test_identical_cards_rejected():
    with pytest.raises(ValueError):
        Trick(c(Suit.COPPE, Rank.ASSO), c(Suit.COPPE, Rank.ASSO), B)


def test_winner_is_always_one_of_the_two_cards_exhaustive():
    cards = [c(s, r) for s in Suit for r in Rank]
    for lead in cards:
        for resp in cards:
            if lead == resp:
                continue
            for b in Suit:
                t = Trick(lead, resp, b)
                assert t.winner() in (lead, resp)
