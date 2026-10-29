import random

import pytest

from briscola.core import Card, Deck, Game, GameResult, IllegalMoveError, Rank, Suit


def c(suit, rank):
    return Card(suit, rank)


def rigged_game():
    """Partita da 10 carte con ordine noto. Briscola: denari.

    Distribuzione alternata: p0 = carte 0,2,4 - p1 = carte 1,3,5 - briscola = carta 6.
    Mazzo residuo (cima -> fondo): carte 7, 8, 9, briscola.
    """
    cards = [
        c(Suit.COPPE, Rank.ASSO),     # 0 -> p0
        c(Suit.COPPE, Rank.RE),       # 1 -> p1
        c(Suit.SPADE, Rank.DUE),      # 2 -> p0
        c(Suit.SPADE, Rank.TRE),      # 3 -> p1
        c(Suit.BASTONI, Rank.DUE),    # 4 -> p0
        c(Suit.BASTONI, Rank.TRE),    # 5 -> p1
        c(Suit.DENARI, Rank.SETTE),   # 6 -> briscola
        c(Suit.COPPE, Rank.DUE),      # 7
        c(Suit.COPPE, Rank.TRE),      # 8
        c(Suit.COPPE, Rank.QUATTRO),  # 9
    ]
    return Game(deck=Deck(cards)), cards


# --- avvio -------------------------------------------------------------------
def test_initial_deal_standard_game():
    game = Game(seed=1)
    assert [len(p.hand) for p in game.players] == [3, 3]
    assert game.deck_size == 34  # 40 - 6 in mano - 1 briscola + 1 rimessa in fondo
    assert game.current_index == 0
    assert not game.is_over()
    all_cards = [*game.players[0].hand, *game.players[1].hand]
    assert len(set(all_cards)) == 6


def test_same_seed_same_game():
    a, b = Game(seed=5), Game(seed=5)
    assert a.players[0].hand == b.players[0].hand
    assert a.briscola_card == b.briscola_card


def test_first_leader_option():
    assert Game(seed=1, first_leader=1).current_index == 1
    with pytest.raises(ValueError):
        Game(first_leader=2)


# --- mosse illegali ----------------------------------------------------------
def test_card_not_in_hand_rejected():
    game, cards = rigged_game()
    with pytest.raises(IllegalMoveError):
        game.play(cards[1])  # carta di p1, ma tocca a p0
    assert len(game.players[0].hand) == 3  # stato invariato


def test_play_after_game_over_rejected():
    game = Game(seed=3)
    rng = random.Random(3)
    while not game.is_over():
        game.play(rng.choice(game.legal_moves()))
    with pytest.raises(IllegalMoveError):
        game.play(c(Suit.COPPE, Rank.ASSO))
    assert game.legal_moves() == ()


def test_result_before_end_rejected():
    with pytest.raises(IllegalMoveError):
        Game(seed=1).result()


# --- flusso di mano e pesca (mazzo truccato) ----------------------------------
def test_turn_alternates_within_trick():
    game, cards = rigged_game()
    assert game.current_index == 0
    assert game.play(cards[0]) is None
    assert game.lead_card == cards[0]
    assert game.current_index == 1


def test_winner_draws_first_and_leads_next():
    game, cards = rigged_game()
    game.play(cards[0])                 # p0: asso di coppe
    trick = game.play(cards[1])         # p1: re di coppe -> prende p0
    assert trick.winner() == cards[0]
    assert game.players[0].score == 15  # 11 + 4
    assert cards[7] in game.players[0].hand  # p0 pesca per primo
    assert cards[8] in game.players[1].hand
    assert game.deck_size == 2
    assert game.current_index == 0      # chi prende apre
    assert game.last_trick == trick


def test_last_draw_is_the_briscola_card():
    game, cards = rigged_game()
    game.play(cards[0]); game.play(cards[1])    # prende p0
    game.play(cards[2])                          # p0: due di spade
    game.play(cards[3])                          # p1: tre di spade -> prende p1
    assert cards[9] in game.players[1].hand      # p1 pesca per primo
    assert game.briscola_card in game.players[0].hand  # p0 pesca la briscola
    assert game.deck_size == 0
    assert game.current_index == 1


def test_no_draw_when_deck_empty_and_game_ends():
    game, _ = rigged_game()
    rng = random.Random(0)
    while not game.is_over():
        game.play(rng.choice(game.legal_moves()))
    assert all(len(p.hand) == 0 for p in game.players)
    assert sum(len(p.captured) for p in game.players) == 10


# --- risultato ---------------------------------------------------------------
def test_result_winner_and_draw():
    assert GameResult((61, 59)).winner == 0
    assert GameResult((50, 70)).winner == 1
    assert GameResult((60, 60)).winner is None


# --- invarianti su partite complete ------------------------------------------
@pytest.mark.parametrize("seed", range(300))
def test_full_random_game_invariants(seed):
    game = Game(seed=seed)
    rng = random.Random(seed)
    tricks = 0
    while not game.is_over():
        if game.play(rng.choice(game.legal_moves())) is not None:
            tricks += 1

    captured = [card for p in game.players for card in p.captured]
    assert tricks == 20
    assert len(captured) == 40 and len(set(captured)) == 40
    assert game.deck_size == 0
    result = game.result()
    assert sum(result.scores) == 120
    assert result.scores == (game.players[0].score, game.players[1].score)
