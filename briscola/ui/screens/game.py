"""Schermata di gioco: anima lo stato di `Game`; non contiene regole."""
from __future__ import annotations

import math

import pygame
from pygame import Vector2

from briscola.ai import RandomStrategy
from briscola.core import Card, Game
from briscola.ui.theme import (
    CARD_H, CARD_W, GOLD, H, TEXT, TEXT_DIM, W, draw_text, felt_background, shadow,
)
from briscola.ui.widgets import Button

HUMAN, CPU = 0, 1
PH_HUMAN, PH_CPU, PH_RESOLVE, PH_OVER = "human", "cpu", "resolve", "over"

CPU_DELAY = 0.8       # "pensiero" della CPU
RESOLVE_HOLD = 1.1    # tempo per leggere la mano prima di raccoglierla
SPEED = 14.0          # rapidità dell'animazione (smorzamento esponenziale)
FACE_UP_DISTANCE = 220  # la carta si scopre quando è abbastanza vicina alla meta

DECK_POS = Vector2(130, H / 2)
BRISCOLA_POS = Vector2(192, H / 2)
HAND_Y = {HUMAN: H - CARD_H / 2 - 20, CPU: CARD_H / 2 + 20}
HAND_SPACING = CARD_W + 22
TABLE_POS = {HUMAN: Vector2(W / 2 - 72, H / 2 + 22), CPU: Vector2(W / 2 + 72, H / 2 - 22)}
PILE_POS = {HUMAN: Vector2(W - 110, H - 150), CPU: Vector2(W - 110, 150)}
HOVER_LIFT = 26


class Sprite:
    __slots__ = ("card", "pos", "target", "angle", "target_angle", "face_up", "z", "pile")

    def __init__(self, card: Card, pos: Vector2, angle: float = 0.0) -> None:
        self.card = card
        self.pos = Vector2(pos)
        self.target = Vector2(pos)
        self.angle = angle
        self.target_angle = angle
        self.face_up = False
        self.z = 1.0
        self.pile: int | None = None   # pila di destinazione, per le carte in volo

    def update(self, dt: float) -> None:
        k = 1 - math.exp(-SPEED * dt)
        self.pos += (self.target - self.pos) * k
        self.angle += (self.target_angle - self.angle) * k

    @property
    def settled(self) -> bool:
        return self.pos.distance_to(self.target) < 1.5


class GameScreen:
    def __init__(self, app, first_leader: int = 0, seed: int | None = None) -> None:
        self.app = app
        self.style = app.deck_style
        self.game = Game(("Tu", "CPU"), seed=seed, first_leader=first_leader)
        self.cpu = RandomStrategy()
        self.sprites: dict[Card, Sprite] = {}
        self.flying: list[Sprite] = []
        self.table: list[tuple[int, Card]] = []   # (giocatore, carta) in ordine di gioco
        self.shown = [0, 0]                        # punteggi mostrati (aggiornati alla raccolta)
        self.pile_cards = [0, 0]
        self.last_trick = None
        self.menu_button = Button((20, 20, 110, 42), "Menu", 22)
        self.mouse = (0, 0)

        briscola = Sprite(self.game.briscola_card, BRISCOLA_POS, angle=90)
        self.sprites[briscola.card] = briscola
        self._sync()
        self._next_phase(extra=0.6)

    # --- geometria -----------------------------------------------------------
    def hand_slot(self, player: int, index: int) -> Vector2:
        n = len(self.game.players[player].hand)
        return Vector2(W / 2 + (index - (n - 1) / 2) * HAND_SPACING, HAND_Y[player])

    def _card_at(self, pos) -> Card | None:
        hand = self.game.players[HUMAN].hand
        for index in reversed(range(len(hand))):
            rect = pygame.Rect(0, 0, CARD_W, CARD_H + HOVER_LIFT)
            slot = self.hand_slot(HUMAN, index)
            rect.midbottom = (slot.x, slot.y + CARD_H / 2)
            if rect.collidepoint(pos):
                return hand[index]
        return None

    # --- stato -------------------------------------------------------------
    def _next_phase(self, extra: float = 0.0) -> None:
        if self.game.current_index == HUMAN:
            self.phase, self.timer = PH_HUMAN, 0.0
        else:
            self.phase, self.timer = PH_CPU, CPU_DELAY + extra

    def _sync(self) -> None:
        """Crea gli sprite delle carte appena pescate (partono dal mazzo)."""
        for player in self.game.players:
            for card in player.hand:
                if card not in self.sprites:
                    self.sprites[card] = Sprite(card, DECK_POS)

    def _zone(self, card: Card) -> tuple[str, int]:
        for index, player in enumerate(self.game.players):
            if card in player.hand:
                return "hand", index
        for owner, table_card in self.table:
            if table_card == card:
                return "table", owner
        return "briscola", 0

    def _layout(self) -> None:
        hover = self._card_at(self.mouse) if self.phase == PH_HUMAN else None
        for card, sprite in self.sprites.items():
            kind, owner = self._zone(card)
            if kind == "hand":
                hand = self.game.players[owner].hand
                target = Vector2(self.hand_slot(owner, hand.index(card)))
                if owner == HUMAN and card == hover:
                    target.y -= HOVER_LIFT
                sprite.z = 1.5 if card == hover else (2.0 if owner == HUMAN else 1.0)
                sprite.target, sprite.target_angle = target, 0
                shown_face = owner == HUMAN
            elif kind == "table":
                sprite.target, sprite.target_angle, sprite.z = Vector2(TABLE_POS[owner]), 0, 3.0
                shown_face = True
            else:
                sprite.target, sprite.target_angle, sprite.z = Vector2(BRISCOLA_POS), 90, 0.0
                shown_face = True
            sprite.face_up = shown_face and sprite.pos.distance_to(sprite.target) < FACE_UP_DISTANCE

    def _play(self, card: Card) -> None:
        owner = self.game.current_index
        self.table.append((owner, card))
        trick = self.game.play(card)
        if trick is None:
            self._next_phase()
        else:
            self.last_trick = trick
            self.phase, self.timer = PH_RESOLVE, RESOLVE_HOLD

    def _collect(self) -> None:
        winner = self.game.current_index   # chi prende apre la mano successiva
        for _, card in self.table:
            sprite = self.sprites.pop(card)
            sprite.target, sprite.target_angle = Vector2(PILE_POS[winner]), 0
            sprite.pile, sprite.z, sprite.face_up = winner, 5.0, False
            self.flying.append(sprite)
        self.table.clear()
        self.shown[winner] += self.last_trick.points
        if self.game.is_over():
            self.phase, self.timer = PH_OVER, 0.5
        else:
            self._next_phase()

    # --- ciclo --------------------------------------------------------------
    def handle_event(self, event) -> None:
        if self.menu_button.clicked(event) or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            self.app.show_menu()
        elif (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            and self.phase == PH_HUMAN
        ):
            card = self._card_at(event.pos)
            if card is not None:
                self._play(card)

    def update(self, dt: float) -> None:
        self.mouse = pygame.mouse.get_pos()
        if self.phase == PH_CPU:
            self.timer -= dt
            if self.timer <= 0:
                self._play(self.cpu.choose_card(self.game.view_for(CPU)))
        elif self.phase == PH_RESOLVE:
            self.timer -= dt
            if self.timer <= 0:
                self._collect()
        elif self.phase == PH_OVER:
            self.timer -= dt
            if self.timer <= 0 and not self.flying:
                self.app.show_game_over(self)
                return

        self._sync()
        self._layout()
        for sprite in self.sprites.values():
            sprite.update(dt)
        for sprite in self.flying:
            sprite.update(dt)
        for sprite in [s for s in self.flying if s.settled]:
            self.pile_cards[sprite.pile] += 1
            self.flying.remove(sprite)

    # --- disegno -------------------------------------------------------------
    def _blit_card(self, surface, sprite: Sprite) -> None:
        image = self.style.face(sprite.card) if sprite.face_up else self.style.back()
        if abs(sprite.angle) > 0.5:
            image = pygame.transform.rotate(image, sprite.angle)
        rect = image.get_rect(center=(round(sprite.pos.x), round(sprite.pos.y)))
        surface.blit(shadow(rect.size), rect.move(4, 6))
        surface.blit(image, rect)

    def _draw_stack(self, surface, center, count: int) -> None:
        layers = min(4, 1 + count // 8)
        back = self.style.back()
        for i in range(layers):
            rect = back.get_rect(center=(center[0] - i * 2, center[1] - i * 2))
            if i == 0:
                surface.blit(shadow(rect.size), rect.move(4, 6))
            surface.blit(back, rect)

    def _status(self) -> str:
        if self.phase == PH_HUMAN:
            return "Tocca a te: scegli una carta"
        if self.phase == PH_CPU:
            return "La CPU sta giocando..."
        trick = self.last_trick
        who = "Prendi tu" if self.game.current_index == HUMAN else "Prende la CPU"
        return f"{who} (+{trick.points})" if self.phase == PH_RESOLVE else "Fine partita"

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(felt_background(), (0, 0))
        ordered = sorted(self.sprites.values(), key=lambda s: s.z)
        for sprite in (s for s in ordered if s.z == 0):
            self._blit_card(surface, sprite)

        deck = self.game.deck_size
        if deck > 1:
            self._draw_stack(surface, DECK_POS, deck)
        if deck > 0:
            draw_text(surface, f"Mazzo: {deck}", 20, TEXT_DIM, midtop=(DECK_POS.x, DECK_POS.y + 106))
            draw_text(surface, "Briscola", 20, TEXT_DIM, midbottom=(BRISCOLA_POS.x + 64, BRISCOLA_POS.y - 64))
        for player in (HUMAN, CPU):
            if self.pile_cards[player]:
                self._draw_stack(surface, PILE_POS[player], self.pile_cards[player] * 3)
        label = {HUMAN: "Tu", CPU: "CPU"}
        draw_text(surface, f"{label[CPU]}: {self.shown[CPU]} punti", 26, TEXT, bold=True,
                  midtop=(PILE_POS[CPU].x, PILE_POS[CPU].y + CARD_H / 2 + 14))
        draw_text(surface, f"{label[HUMAN]}: {self.shown[HUMAN]} punti", 26, GOLD, bold=True,
                  midbottom=(PILE_POS[HUMAN].x, PILE_POS[HUMAN].y - CARD_H / 2 - 14))

        for sprite in (s for s in ordered if s.z > 0):
            self._blit_card(surface, sprite)
        for sprite in self.flying:
            self._blit_card(surface, sprite)

        draw_text(surface, self._status(), 24, TEXT, midleft=(40, H - 38))
        self.menu_button.draw(surface, self.mouse)
