from __future__ import annotations

import pygame

from briscola.core import Card, Rank, Suit
from briscola.ui.theme import GOLD, PANEL, TEXT, TEXT_DIM, W, draw_text, felt_background
from briscola.ui.widgets import Button

PREVIEW = (
    Card(Suit.DENARI, Rank.ASSO), Card(Suit.COPPE, Rank.SETTE),
    Card(Suit.SPADE, Rank.CAVALLO), Card(Suit.BASTONI, Rank.RE),
)
ANGLES = (-9, -3, 3, 9)


class MenuScreen:
    def __init__(self, app) -> None:
        self.app = app
        self.play_button = Button((W // 2 - 130, 585, 260, 62), "Gioca", 32)
        self.quit_button = Button((W // 2 - 70, 662, 140, 40), "Esci", 20)
        n = len(app.styles)
        gap = 40
        pw = min(400, (W - 120 - gap * (n - 1)) // n)
        left = (W - (n * pw + gap * (n - 1))) // 2
        self.panels = {
            name: pygame.Rect(left + i * (pw + gap), 175, pw, 350)
            for i, name in enumerate(app.styles)
        }

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.panels.items():
                if rect.collidepoint(event.pos):
                    self.app.set_deck(name)
        if self.play_button.clicked(event):
            self.app.new_game()
        elif self.quit_button.clicked(event):
            self.app.running = False

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(felt_background(), (0, 0))
        draw_text(surface, "Briscola", 88, GOLD, bold=True, center=(W // 2, 80))
        draw_text(surface, "Scegli il mazzo", 26, TEXT_DIM, center=(W // 2, 138))
        for name, rect in self.panels.items():
            style = self.app.styles[name]
            selected = name == self.app.settings.deck
            pygame.draw.rect(surface, (22, 78, 50) if selected else PANEL, rect, border_radius=18)
            pygame.draw.rect(surface, GOLD if selected else (36, 90, 62), rect,
                             width=4 if selected else 2, border_radius=18)
            draw_text(surface, style.label, 30, TEXT, bold=True, midtop=(rect.centerx, rect.top + 18))
            for i, (card, angle) in enumerate(zip(PREVIEW, ANGLES)):
                img = pygame.transform.rotozoom(style.face(card), angle, 1.0)
                x = rect.centerx + (i - 1.5) * 62
                surface.blit(img, img.get_rect(center=(x, rect.centery + 28)))
        mouse = pygame.mouse.get_pos()
        self.play_button.draw(surface, mouse)
        self.quit_button.draw(surface, mouse)
