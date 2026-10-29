"""Interfaccia a terminale: Tu contro la CPU."""
from __future__ import annotations

import argparse
import random
from collections.abc import Callable

from briscola.ai import RandomStrategy, Strategy
from briscola.core import Card, Game

HUMAN = 0


def _ask_card(
    game: Game, read: Callable[[str], str], write: Callable[[str], None]
) -> Card | None:
    """Mostra stato e mano, chiede la carta. None se l'utente esce (q o EOF)."""
    view = game.view_for(HUMAN)
    write(
        f"\nBriscola: {view.briscola_card} | Mazzo: {view.deck_size} | "
        f"Punti: tu {view.my_score} - CPU {view.opponent_score}"
    )
    for i, card in enumerate(view.hand, start=1):
        tag = " (briscola)" if card.suit == view.briscola else ""
        write(f"  {i}) {card}{tag}")

    while True:
        try:
            raw = read(f"Scegli la carta (1-{len(view.hand)}, q per uscire): ")
        except EOFError:
            return None
        raw = raw.strip().lower()
        if raw == "q":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(view.hand):
            return view.hand[int(raw) - 1]
        write("Scelta non valida.")


def play_cli(
    game: Game,
    cpu: Strategy,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> None:
    write(f"Briscola in tavola: {game.briscola_card}")
    while not game.is_over():
        index = game.current_index
        name = game.current_player.name
        if index == HUMAN:
            card = _ask_card(game, read, write)
            if card is None:
                write("Partita interrotta.")
                return
        else:
            card = cpu.choose_card(game.view_for(index))

        write(f"Tu giochi: {card}" if index == HUMAN else f"{name} gioca: {card}")
        trick = game.play(card)
        if trick is not None:
            # Chi prende apre la mano successiva, quindi è il giocatore di turno.
            taker = "Prendi tu" if game.current_index == HUMAN else "Prende la CPU"
            write(f"{taker} ({trick.points} punti)")

    result = game.result()
    me, cpu_name = game.players[HUMAN].name, game.players[1 - HUMAN].name
    a, b = result.scores
    write(f"\nPunteggio finale: {me} {a} - {cpu_name} {b}")
    if result.winner is None:
        write("Pareggio!")
    elif result.winner == HUMAN:
        write("Hai vinto!")
    else:
        write("Ha vinto la CPU.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Briscola: tu contro la CPU")
    parser.add_argument("--seed", type=int, default=None, help="partita riproducibile")
    args = parser.parse_args()

    game = Game(player_names=("Tu", "CPU"), seed=args.seed)
    cpu_seed = None if args.seed is None else args.seed + 1
    play_cli(game, RandomStrategy(random.Random(cpu_seed)))
