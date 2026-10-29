import dataclasses
import random

import pytest

from briscola.core import Game


def test_view_hides_opponent_hand_and_reports_sizes():
    game = Game(seed=1)
    view = game.view_for(0)
    assert view.hand == tuple(game.players[0].hand)
    assert view.opponent_hand_size == 3
    assert view.deck_size == 34
    assert view.briscola == game.briscola
    assert view.played == ()
    assert not hasattr(view, "opponent_hand")


def test_lead_card_visible_only_to_responder():
    game = Game(seed=1)
    lead = game.players[0].hand[0]
    assert game.view_for(0).lead_card is None
    game.play(lead)
    assert game.view_for(0).lead_card is None      # chi ha aperto non la vede come "da rispondere"
    assert game.view_for(1).lead_card == lead
    assert game.view_for(1).opponent_hand_size == 2


def test_played_and_scores_after_a_trick():
    game = Game(seed=2)
    game.play(game.players[0].hand[0])
    trick = game.play(game.players[1].hand[0])
    assert set(game.view_for(0).played) == {trick.lead, trick.response}
    assert game.view_for(0).my_score == game.players[0].score
    assert game.view_for(0).opponent_score == game.players[1].score
    assert game.view_for(1).my_score == game.players[1].score


def test_view_is_immutable_snapshot():
    game = Game(seed=1)
    view = game.view_for(0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        view.deck_size = 0
    game.play(game.players[0].hand[0])
    assert len(view.hand) == 3  # lo snapshot non cambia con la partita


def test_invalid_index_rejected():
    with pytest.raises(ValueError):
        Game(seed=1).view_for(2)


@pytest.mark.parametrize("seed", range(50))
def test_view_consistent_over_full_game(seed):
    game = Game(seed=seed)
    rng = random.Random(seed)
    while not game.is_over():
        idx = game.current_index
        view = game.view_for(idx)
        assert view.hand == tuple(game.legal_moves())
        assert len(view.played) % 2 == 0
        assert view.deck_size == game.deck_size
        game.play(rng.choice(view.hand))
