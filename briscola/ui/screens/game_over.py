from __future__ import annotations

import pygame

from briscola.ui.theme import GOLD, H, PANEL, TEXT, TEXT_DIM, W, draw_text
from briscola.ui.widgets import Button


class GameOverScreen:
    def __init__(self, app, background: pygame.Surface, result) -> None:
        self.app = app
        self.result = result
        self.background = background
        self.dim = pygame.Surface((W, H), pygame.SRCALPHA)
        self.dim.fill((0, 0, 0, 150))
        self.panel = pygame.Rect(0, 0, 560, 330)
        self.panel.center = (W // 2, H // 2)
        self.rematch_button = Button((self.panel.centerx - 230, self.panel.bottom - 90, 210, 56), "Rivincita", 26)
        self.menu_button = Button((self.panel.centerx + 20, self.panel.bottom - 90, 210, 56), "Menu", 26)

    @property
    def title(self) -> str:
        return {None: "Pareggio!", 0: "Hai vinto!", 1: "Ha vinto la CPU"}[self.result.winner]

    def handle_event(self, event) -> None:
        if self.rematch_button.clicked(event):
            self.app.new_game()
        elif self.menu_button.clicked(event):
            self.app.show_menu()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        surface.blit(self.dim, (0, 0))
        pygame.draw.rect(surface, PANEL, self.panel, border_radius=20)
        pygame.draw.rect(surface, GOLD, self.panel, width=3, border_radius=20)
        draw_text(surface, self.title, 54, GOLD, bold=True, center=(self.panel.centerx, self.panel.top + 70))
        a, b = self.result.scores
        draw_text(surface, f"Tu  {a}   -   {b}  CPU", 38, TEXT, bold=True,
                  center=(self.panel.centerx, self.panel.top + 148))
        draw_text(surface, "Per vincere servono almeno 61 punti su 120", 20, TEXT_DIM,
                  center=(self.panel.centerx, self.panel.top + 192))
        mouse = pygame.mouse.get_pos()
        self.rematch_button.draw(surface, mouse)
        self.menu_button.draw(surface, mouse)
