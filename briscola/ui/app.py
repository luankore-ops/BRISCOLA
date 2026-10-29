"""Applicazione Pygame: finestra, game loop e passaggio tra le schermate."""
from __future__ import annotations

import argparse
from pathlib import Path

import pygame

from briscola.ui.deck_styles import DeckStyle, available_styles
from briscola.ui.screens.game import GameScreen
from briscola.ui.screens.game_over import GameOverScreen
from briscola.ui.screens.menu import MenuScreen
from briscola.ui.settings import Settings
from briscola.ui.theme import H, W


class App:
    def __init__(self, seed: int | None = None, settings_file: Path | None = None) -> None:
        pygame.init()
        try:  # SCALED: coordinate logiche fisse 1280x720, finestra ridimensionabile
            self.display = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
        except pygame.error:
            self.display = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Briscola")
        self.clock = pygame.time.Clock()
        self.running = True
        self.seed = seed
        self.games_played = 0
        self.settings_file = settings_file
        self.settings = Settings.load(settings_file)
        self.styles: dict[str, DeckStyle] = available_styles()
        if self.settings.deck not in self.styles:
            self.settings.deck = next(iter(self.styles))
        self.screen = MenuScreen(self)

    @property
    def deck_style(self) -> DeckStyle:
        return self.styles[self.settings.deck]

    def set_deck(self, name: str) -> None:
        self.settings.deck = name
        self.settings.save(self.settings_file)

    # --- transizioni ---
    def show_menu(self) -> None:
        self.screen = MenuScreen(self)

    def new_game(self) -> None:
        first_leader = self.games_played % 2    # si alterna chi apre
        seed = self.seed if self.games_played == 0 else None
        self.games_played += 1
        self.screen = GameScreen(self, first_leader=first_leader, seed=seed)

    def show_game_over(self, game_screen: GameScreen) -> None:
        self.screen = GameOverScreen(self, self.display.copy(), game_screen.game.result())

    # --- ciclo ---
    def step(self, dt: float, events) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            else:
                self.screen.handle_event(event)
        self.screen.update(dt)
        self.screen.draw(self.display)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(60) / 1000, 0.05)
            self.step(dt, pygame.event.get())
        pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Briscola")
    parser.add_argument("--seed", type=int, default=None, help="prima partita riproducibile")
    App(seed=parser.parse_args().seed).run()
