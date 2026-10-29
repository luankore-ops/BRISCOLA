import itertools
import random

from briscola.ai import RandomStrategy
from briscola.cli import play_cli
from briscola.core import Game


def run(inputs, seed=1):
    out = []
    feed = iter(inputs)
    game = Game(player_names=("Tu", "CPU"), seed=seed)
    play_cli(game, RandomStrategy(random.Random(seed)),
             read=lambda prompt: next(feed), write=out.append)
    return game, "\n".join(out)


def test_full_game_with_valid_inputs():
    game, text = run(itertools.repeat("1"))
    assert game.is_over()
    assert "Punteggio finale" in text
    assert any(w in text for w in ("Hai vinto!", "Ha vinto la CPU.", "Pareggio!"))


def test_invalid_input_is_rejected_and_reprompted():
    game, text = run(itertools.chain(["x", "0", "9", ""], itertools.repeat("1")))
    assert text.count("Scelta non valida.") == 4
    assert game.is_over()


def test_quit_stops_the_game():
    game, text = run(["q"])
    assert "Partita interrotta." in text
    assert not game.is_over()


def test_eof_stops_the_game():
    def eof(prompt):
        raise EOFError
    out = []
    game = Game(seed=1)
    play_cli(game, RandomStrategy(random.Random(1)), read=eof, write=out.append)
    assert "Partita interrotta." in out
    assert not game.is_over()
