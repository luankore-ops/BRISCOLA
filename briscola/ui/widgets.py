from __future__ import annotations

import pygame

from briscola.ui.theme import BUTTON, BUTTON_HOVER, GOLD, TEXT, draw_text


class Button:
    def __init__(self, rect, text: str, size: int = 26) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.size = size

    def clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface: pygame.Surface, mouse_pos) -> None:
        hover = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, BUTTON_HOVER if hover else BUTTON, self.rect, border_radius=12)
        pygame.draw.rect(surface, GOLD if hover else (30, 80, 52), self.rect, width=2, border_radius=12)
        draw_text(surface, self.text, self.size, TEXT, bold=True, center=self.rect.center)
