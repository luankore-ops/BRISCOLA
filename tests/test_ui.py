import json

import pytest

pygame = pytest.importorskip("pygame")

from briscola.core import Card, Rank, Suit  # noqa: E402
from briscola.ui.app import App  # noqa: E402
from briscola.ui.deck_styles import PngDeckStyle, available_styles  # noqa: E402
from briscola.ui.screens.game import GameScreen  # noqa: E402
from briscola.ui.screens.game_over import GameOverScreen  # noqa: E402
from briscola.ui.screens.menu import MenuScreen  # noqa: E402
from briscola.ui.settings import Settings  # noqa: E402
from briscola.ui.theme import CARD_H, CARD_W  # noqa: E402

ALL = [Card(s, r) for s in Suit for r in Rank]


@pytest.fixture(scope="module", autouse=True)
def display():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    yield


def click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=tuple(pos), button=1)


def pixels(surface):
    return pygame.image.tobytes(surface, "RGBA")


# --- mazzi ---------------------------------------------------------------------
@pytest.mark.parametrize("name", ["napoletano", "piacentino"])
def test_builtin_styles_render_40_distinct_faces(name):
    style = available_styles()[name]
    faces = [style.face(c) for c in ALL]
    assert all(f.get_size() == (CARD_W, CARD_H) for f in faces)
    assert len({pixels(f) for f in faces}) == 40
    assert pixels(style.back()) not in {pixels(f) for f in faces}
    assert style.back().get_size() == (CARD_W, CARD_H)


def test_styles_look_different():
    styles = available_styles()
    card = Card(Suit.COPPE, Rank.RE)
    assert pixels(styles["napoletano"].face(card)) != pixels(styles["piacentino"].face(card))


def _make_png_deck(folder):
    folder.mkdir(parents=True)
    for i, card in enumerate(ALL):
        surf = pygame.Surface((60, 95))
        surf.fill((i * 6, 10, 200 - i * 4))
        pygame.image.save(surf, str(folder / f"{card.suit.value}_{int(card.rank)}.png"))
    back = pygame.Surface((60, 95))
    back.fill((1, 2, 3))
    pygame.image.save(back, str(folder / "back.png"))


def test_png_style_loads_and_scales(tmp_path):
    _make_png_deck(tmp_path / "mio")
    style = PngDeckStyle(tmp_path / "mio")
    assert style.name == "mio"
    assert style.face(ALL[0]).get_size() == (CARD_W, CARD_H)
    assert pixels(style.face(ALL[0])) != pixels(style.face(ALL[1]))


def test_registry_includes_valid_png_decks_and_skips_incomplete(tmp_path):
    _make_png_deck(tmp_path / "completo")
    (tmp_path / "incompleto").mkdir()
    (tmp_path / "incompleto" / "back.png").write_bytes(b"x")
    styles = available_styles(tmp_path)
    assert {"napoletano", "piacentino", "completo"} <= set(styles)
    assert "incompleto" not in styles


def test_png_style_missing_file(tmp_path):
    (tmp_path / "vuoto").mkdir()
    with pytest.raises(FileNotFoundError):
        PngDeckStyle(tmp_path / "vuoto")


# --- impostazioni -----------------------------------------------------------------
def test_settings_roundtrip(tmp_path):
    path = tmp_path / "sub" / "settings.json"
    Settings(deck="piacentino").save(path)
    assert Settings.load(path).deck == "piacentino"


@pytest.mark.parametrize("content", ["{non json", "[]", '"stringa"'])
def test_settings_corrupted_falls_back_to_default(tmp_path, content):
    path = tmp_path / "settings.json"
    path.write_text(content, encoding="utf-8")
    assert Settings.load(path).deck == "napoletano"


def test_settings_missing_file(tmp_path):
    assert Settings.load(tmp_path / "non_esiste.json").deck == "napoletano"


# --- applicazione -----------------------------------------------------------------
def drive_to_game_over(app, max_steps=8000):
    for _ in range(max_steps):
        events = []
        screen = app.screen
        if isinstance(screen, GameScreen) and screen.phase == "human":
            events.append(click(screen.hand_slot(0, 0)))
        app.step(0.05, events)
        if isinstance(app.screen, GameOverScreen):
            return app.screen
    raise AssertionError("la partita non è terminata")


def test_menu_selects_deck_and_persists(tmp_path):
    file = tmp_path / "settings.json"
    app = App(seed=1, settings_file=file)
    assert isinstance(app.screen, MenuScreen)
    app.step(0.016, [click(app.screen.panels["piacentino"].center)])
    assert app.settings.deck == "piacentino"
    assert json.loads(file.read_text())["deck"] == "piacentino"
    assert App(settings_file=file).deck_style.name == "piacentino"


def test_unknown_saved_deck_falls_back(tmp_path):
    file = tmp_path / "settings.json"
    file.write_text('{"deck": "inesistente"}')
    assert App(settings_file=file).deck_style.name in {"napoletano", "piacentino"}


def test_full_game_through_ui_then_rematch_and_menu(tmp_path):
    app = App(seed=3, settings_file=tmp_path / "s.json")
    app.step(0.016, [click(app.screen.play_button.rect.center)])
    assert isinstance(app.screen, GameScreen)
    assert app.screen.game.current_index == 0   # prima partita: apri tu

    over = drive_to_game_over(app)
    assert sum(over.result.scores) == 120
    assert over.title in {"Hai vinto!", "Ha vinto la CPU", "Pareggio!"}

    app.step(0.016, [click(over.rematch_button.rect.center)])
    assert isinstance(app.screen, GameScreen)
    assert app.games_played == 2
    assert app.screen.game.current_index == 1   # rivincita: apre la CPU

    over = drive_to_game_over(app)
    app.step(0.016, [click(over.menu_button.rect.center)])
    assert isinstance(app.screen, MenuScreen)


def test_clicking_outside_hand_does_nothing(tmp_path):
    app = App(seed=3, settings_file=tmp_path / "s.json")
    app.new_game()
    screen = app.screen
    before = len(screen.game.players[0].hand)
    app.step(0.016, [click((5, 400))])
    assert len(screen.game.players[0].hand) == before
    assert not screen.table


def test_clicks_ignored_while_cpu_plays(tmp_path):
    app = App(seed=3, settings_file=tmp_path / "s.json")
    app.new_game()
    screen = app.screen
    screen._play(screen.game.players[0].hand[0])
    assert screen.phase == "cpu"
    hand = list(screen.game.players[0].hand)
    app.step(0.016, [click(screen.hand_slot(0, 0))])
    assert screen.game.players[0].hand == hand


def test_escape_returns_to_menu(tmp_path):
    app = App(settings_file=tmp_path / "s.json")
    app.new_game()
    app.step(0.016, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
    assert isinstance(app.screen, MenuScreen)


def test_quit_event_stops_app(tmp_path):
    app = App(settings_file=tmp_path / "s.json")
    app.step(0.016, [pygame.event.Event(pygame.QUIT)])
    assert not app.running


def test_displayed_scores_match_final_result(tmp_path):
    app = App(seed=9, settings_file=tmp_path / "s.json")
    app.new_game()
    screen = app.screen
    over = drive_to_game_over(app)
    assert tuple(screen.shown) == over.result.scores
    assert sum(screen.pile_cards) == 40
