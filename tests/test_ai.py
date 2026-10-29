import random

import pytest

from briscola.ai import RandomStrategy
from briscola.core import Game


def test_random_strategy_returns_card_from_hand():
    game = Game(seed=1)
    view = game.view_for(0)
    assert RandomStrategy(random.Random(0)).choose_card(view) in view.hand


def test_random_strategy_is_reproducible_with_seed():
    view = Game(seed=1).view_for(0)
    a = [RandomStrategy(random.Random(5)).choose_card(view) for _ in range(5)]
    b = [RandomStrategy(random.Random(5)).choose_card(view) for _ in range(5)]
    assert a == b


@pytest.mark.parametrize("seed", range(50))
def test_two_random_strategies_complete_legal_games(seed):
    game = Game(seed=seed)
    bots = (RandomStrategy(random.Random(seed)), RandomStrategy(random.Random(seed + 1000)))
    while not game.is_over():
        idx = game.current_index
        game.play(bots[idx].choose_card(game.view_for(idx)))  # IllegalMoveError se scelta illegale
    assert sum(game.result().scores) == 120
