"""Stato e regole di una partita di Briscola a 2 giocatori.

Il gioco avanza a passi (`play`), senza chiamate bloccanti: l'interfaccia
(terminale, Pygame) decide quando e con quale carta giocare.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from briscola.core.card import Card, Suit
from briscola.core.deck import Deck
from briscola.core.player import Player
from briscola.core.trick import Trick
from briscola.core.view import GameView

HAND_SIZE = 3


class IllegalMoveError(ValueError):
    """Mossa o operazione non consentita nello stato attuale della partita."""


@dataclass(frozen=True, slots=True)
class GameResult:
    scores: tuple[int, int]

    @property
    def winner(self) -> int | None:
        """Indice del vincitore, oppure None in caso di pareggio (60-60)."""
        a, b = self.scores
        if a == b:
            return None
        return 0 if a > b else 1


class Game:
    def __init__(
        self,
        player_names: tuple[str, str] = ("Giocatore", "CPU"),
        seed: int | None = None,
        first_leader: int = 0,
        deck: Deck | None = None,
    ) -> None:
        if first_leader not in (0, 1):
            raise ValueError("first_leader deve essere 0 o 1")
        self._players = (Player(player_names[0]), Player(player_names[1]))
        # `deck` iniettabile: permette test deterministici con mazzi truccati.
        self._deck = deck if deck is not None else Deck.standard(random.Random(seed))

        for _ in range(HAND_SIZE):
            for player in self._players:
                player.hand.append(self._deck.draw())
        self._briscola_card = self._deck.draw()
        self._deck.put_bottom(self._briscola_card)  # sarà l'ultima carta pescata

        self._leader = first_leader
        self._lead_card: Card | None = None
        self._last_trick: Trick | None = None

    # --- stato osservabile ---------------------------------------------------
    @property
    def players(self) -> tuple[Player, Player]:
        return self._players

    @property
    def briscola_card(self) -> Card:
        """La carta scoperta all'inizio (finisce in fondo al mazzo)."""
        return self._briscola_card

    @property
    def briscola(self) -> Suit:
        return self._briscola_card.suit

    @property
    def deck_size(self) -> int:
        return len(self._deck)

    @property
    def lead_card(self) -> Card | None:
        """Carta giocata da chi ha aperto la mano in corso, se già giocata."""
        return self._lead_card

    @property
    def last_trick(self) -> Trick | None:
        """Ultima mano conclusa (utile alla UI per mostrarla)."""
        return self._last_trick

    @property
    def current_index(self) -> int:
        return self._leader if self._lead_card is None else 1 - self._leader

    @property
    def current_player(self) -> Player:
        return self._players[self.current_index]

    # --- regole --------------------------------------------------------------
    def is_over(self) -> bool:
        return not any(player.hand for player in self._players)

    def legal_moves(self) -> tuple[Card, ...]:
        if self.is_over():
            return ()
        return tuple(self.current_player.hand)

    def play(self, card: Card) -> Trick | None:
        """Gioca `card` per il giocatore di turno.

        Restituisce la `Trick` conclusa se questa era la seconda carta della
        mano, altrimenti None.
        """
        if self.is_over():
            raise IllegalMoveError("La partita è finita")
        player = self.current_player
        if card not in player.hand:
            raise IllegalMoveError(f"{card} non è nella mano di {player.name}")

        player.hand.remove(card)
        if self._lead_card is None:
            self._lead_card = card
            return None
        return self._resolve_trick(card)

    def view_for(self, index: int) -> GameView:
        """Vista dello stato per il giocatore `index`: nessuna informazione nascosta."""
        if index not in (0, 1):
            raise ValueError("index deve essere 0 o 1")
        me, opponent = self._players[index], self._players[1 - index]
        # La carta in tavolo interessa solo a chi deve ancora rispondere.
        lead = self._lead_card if index != self._leader else None
        return GameView(
            hand=tuple(me.hand),
            lead_card=lead,
            briscola_card=self._briscola_card,
            deck_size=len(self._deck),
            opponent_hand_size=len(opponent.hand),
            my_score=me.score,
            opponent_score=opponent.score,
            played=tuple(card for p in self._players for card in p.captured),
        )

    def result(self) -> GameResult:
        if not self.is_over():
            raise IllegalMoveError("La partita non è ancora finita")
        return GameResult((self._players[0].score, self._players[1].score))

    # --- interni -------------------------------------------------------------
    def _resolve_trick(self, response: Card) -> Trick:
        assert self._lead_card is not None
        trick = Trick(self._lead_card, response, self.briscola)
        winner_idx = self._leader if trick.leader_wins() else 1 - self._leader
        winner, loser = self._players[winner_idx], self._players[1 - winner_idx]

        winner.captured.extend((trick.lead, trick.response))
        if len(self._deck) > 0:  # chi prende pesca per primo
            winner.hand.append(self._deck.draw())
            loser.hand.append(self._deck.draw())

        self._leader = winner_idx
        self._lead_card = None
        self._last_trick = trick
        return trick
