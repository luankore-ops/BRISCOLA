"""Costanti grafiche, font e sfondo condivisi dalle schermate."""
from __future__ import annotations

import functools
import math

import pygame

W, H = 1280, 720
CARD_W, CARD_H = 120, 190

FELT_EDGE = (14, 62, 38)
FELT_LIGHT = (38, 128, 78)
TEXT = (240, 240, 232)
TEXT_DIM = (170, 198, 182)
GOLD = (236, 196, 88)
PANEL = (12, 46, 29)
BUTTON = (44, 112, 74)
BUTTON_HOVER = (64, 144, 96)


@functools.lru_cache(maxsize=None)
def font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("segoeui,arial,helvetica,dejavusans", size, bold=bold)


def draw_text(surface, text, size, color, bold=False, **anchor) -> pygame.Rect:
    """Disegna `text`; `anchor` è un argomento di Rect (center=, topleft=, midtop=...)."""
    image = font(size, bold).render(text, True, color)
    rect = image.get_rect(**anchor)
    surface.blit(image, rect)
    return rect


@functools.lru_cache(maxsize=1)
def felt_background() -> pygame.Surface:
    """Tappeto verde con una leggera luce al centro (gradiente scalato)."""
    small = pygame.Surface((64, 36))
    for y in range(36):
        for x in range(64):
            d = min(1.0, math.hypot((x - 31.5) / 32, (y - 17.5) / 18) / 1.15)
            t = 1 - d**1.6
            small.set_at((x, y), tuple(int(a + (b - a) * t) for a, b in zip(FELT_EDGE, FELT_LIGHT)))
    return pygame.transform.smoothscale(small, (W, H))


@functools.lru_cache(maxsize=None)
def shadow(size: tuple[int, int]) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 0, 0, 80), surf.get_rect(), border_radius=14)
    return surf
