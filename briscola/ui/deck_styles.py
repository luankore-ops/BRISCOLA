"""Mazzi di carte: stili disegnati via codice e stili PNG caricati da cartella.

Convenzione PNG (cartella `assets/decks/<nome>/`): `<seme>_<valore>.png` con seme
in {denari, coppe, spade, bastoni} e valore 1-10 (8 fante, 9 cavallo, 10 re),
più `back.png` per il dorso.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from briscola.core import Card, Rank, Suit
from briscola.ui.paths import resource_path
from briscola.ui.theme import CARD_H, CARD_W, font

SS = 3  # supersampling: si disegna a 3x e si riduce, per bordi lisci


class DeckStyle:
    name: str
    label: str

    def face(self, card: Card) -> pygame.Surface:
        raise NotImplementedError

    def back(self) -> pygame.Surface:
        raise NotImplementedError


# --- simboli dei semi -----------------------------------------------------------
def _darker(c, f=0.65):
    return tuple(int(v * f) for v in c[:3])


def _lighter(c, f=0.4):
    return tuple(int(v + (255 - v) * f) for v in c[:3])


def _poly(cx, cy, r, shape):
    return [(cx + x * r, cy + y * r) for x, y in shape]


_CUP = [(-1, -.9), (1, -.9), (.88, -.25), (.5, .15), (.16, .32), (.16, .68), (.62, .82),
        (.62, .95), (-.62, .95), (-.62, .82), (-.16, .68), (-.16, .32), (-.5, .15), (-.88, -.25)]
_BLADE = [(0, -1), (.17, -.8), (.17, .36), (-.17, .36), (-.17, -.8)]
_CROSS = [(-.52, .36), (.52, .36), (.52, .48), (-.52, .48)]
_GRIP = [(-.08, .48), (.08, .48), (.08, .82), (-.08, .82)]


def _denaro(s, cx, cy, r, color):
    rr = int(r * 0.92)
    pygame.draw.circle(s, color, (cx, cy), rr)
    pygame.draw.circle(s, _darker(color), (cx, cy), rr, max(2, rr // 9))
    pygame.draw.circle(s, _darker(color, 0.8), (cx, cy), int(rr * 0.58), max(2, rr // 14))
    pygame.draw.circle(s, _lighter(color, 0.6), (cx - rr // 4, cy - rr // 4), max(2, rr // 6))


def _coppa(s, cx, cy, r, color):
    pts = _poly(cx, cy, r, _CUP)
    pygame.draw.polygon(s, color, pts)
    pygame.draw.polygon(s, _darker(color), pts, max(2, r // 9))
    pygame.draw.line(s, _lighter(color, 0.55), (cx - r * .55, cy - r * .62), (cx - r * .3, cy - r * .05), max(2, r // 9))


def _spada(s, cx, cy, r, color):
    for shape, col in ((_BLADE, _lighter(color, 0.15)), (_CROSS, color), (_GRIP, _darker(color, 0.8))):
        pts = _poly(cx, cy, r, shape)
        pygame.draw.polygon(s, col, pts)
        pygame.draw.polygon(s, _darker(color, 0.55), pts, max(1, r // 14))
    pygame.draw.circle(s, color, (cx, int(cy + r * .9)), max(2, int(r * .13)))


def _bastone(s, cx, cy, r, color):
    w = max(4, int(r * .42))
    pygame.draw.line(s, color, (cx, cy - r * .85), (cx, cy + r * .85), w)
    for y in (-.85, .85):
        pygame.draw.circle(s, color, (cx, int(cy + y * r)), w // 2)
    pygame.draw.line(s, _lighter(color, 0.45), (cx - w // 4, cy - r * .7), (cx - w // 4, cy + r * .7), max(1, w // 6))
    for y in (-.35, .3):
        pygame.draw.circle(s, _darker(color), (cx + w // 6, int(cy + y * r)), max(2, w // 5))


_DRAW = {Suit.DENARI: _denaro, Suit.COPPE: _coppa, Suit.SPADE: _spada, Suit.BASTONI: _bastone}

# posizioni dei simboli (frazioni dell'area centrale) e loro raggio (px a 1x)
_LAYOUT = {
    1: [(.5, .5)],
    2: [(.5, .25), (.5, .75)],
    3: [(.5, .2), (.5, .5), (.5, .8)],
    4: [(.3, .28), (.7, .28), (.3, .72), (.7, .72)],
    5: [(.3, .22), (.7, .22), (.5, .5), (.3, .78), (.7, .78)],
    6: [(.3, .2), (.7, .2), (.3, .5), (.7, .5), (.3, .8), (.7, .8)],
    7: [(.3, .2), (.7, .2), (.5, .35), (.3, .5), (.7, .5), (.3, .8), (.7, .8)],
}
_PIP_R = {1: 34, 2: 17, 3: 15, 4: 12, 5: 12, 6: 12, 7: 10}
_FIG_LETTER = {Rank.FANTE: "F", Rank.CAVALLO: "C", Rank.RE: "R"}


@dataclass(frozen=True)
class Palette:
    paper: tuple
    border: tuple
    inner_border: tuple | None
    ink: tuple
    suits: dict
    back_a: tuple
    back_b: tuple


class ProceduralStyle(DeckStyle):
    def __init__(self, name: str, label: str, palette: Palette, rank_labels: dict) -> None:
        self.name, self.label = name, label
        self.palette = palette
        self.rank_labels = rank_labels
        self._faces: dict[Card, pygame.Surface] = {}
        self._back: pygame.Surface | None = None

    def face(self, card: Card) -> pygame.Surface:
        if card not in self._faces:
            self._faces[card] = self._render_face(card)
        return self._faces[card]

    def back(self) -> pygame.Surface:
        if self._back is None:
            self._back = self._render_back()
        return self._back

    # --- rendering ---
    def _frame(self, fill, border, inner) -> pygame.Surface:
        surf = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
        rect, radius = surf.get_rect(), 12 * SS
        pygame.draw.rect(surf, fill, rect, border_radius=radius)
        pygame.draw.rect(surf, border, rect, width=3 * SS, border_radius=radius)
        if inner:
            pygame.draw.rect(surf, inner, rect.inflate(-12 * SS, -12 * SS), width=SS, border_radius=radius - 3 * SS)
        return surf

    def _render_face(self, card: Card) -> pygame.Surface:
        p = self.palette
        surf = self._frame(p.paper, p.border, p.inner_border)
        color = p.suits[card.suit]
        corner = self._corner(card, color)
        m = 9 * SS
        surf.blit(corner, (m, 7 * SS))
        surf.blit(pygame.transform.rotate(corner, 180),
                  (surf.get_width() - m - corner.get_width(), surf.get_height() - 7 * SS - corner.get_height()))
        if card.rank <= Rank.SETTE:
            self._pips(surf, card, color)
        else:
            self._figure(surf, card, color)
        return pygame.transform.smoothscale(surf, (CARD_W, CARD_H))

    def _corner(self, card: Card, color) -> pygame.Surface:
        txt = font(17 * SS, True).render(self.rank_labels[card.rank], True, self.palette.ink)
        sr = 6 * SS
        w, h = max(txt.get_width(), 2 * sr) + 2, txt.get_height() + 2 * sr + 2 * SS
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(txt, ((w - txt.get_width()) // 2, 0))
        _DRAW[card.suit](surf, w // 2, txt.get_height() + SS + sr, sr, color)
        return surf

    def _pips(self, surf, card: Card, color) -> None:
        n = int(card.rank)
        w, h = surf.get_size()
        x0, y0, aw, ah = 0.25 * w, 0.14 * h, 0.5 * w, 0.72 * h
        for fx, fy in _LAYOUT[n]:
            _DRAW[card.suit](surf, int(x0 + fx * aw), int(y0 + fy * ah), _PIP_R[n] * SS, color)

    def _figure(self, surf, card: Card, color) -> None:
        p = self.palette
        w, h = surf.get_size()
        cx, cy = w // 2, h // 2
        frame = pygame.Rect(0, 0, int(0.52 * w), int(0.62 * h))
        frame.center = (cx, cy)
        pygame.draw.rect(surf, _lighter(color, 0.8), frame, border_radius=10 * SS)
        pygame.draw.rect(surf, color, frame, width=2 * SS, border_radius=10 * SS)
        txt = font(34 * SS, True).render(_FIG_LETTER[card.rank], True, p.ink)
        surf.blit(txt, txt.get_rect(center=(cx, cy - 4 * SS)))
        _DRAW[card.suit](surf, cx, cy + 34 * SS, 12 * SS, color)
        if card.rank == Rank.RE:
            base = (cx, frame.top + 22 * SS)
            crown = _poly(*base, SS, [(-18, 14), (-18, -4), (-9, 5), (0, -8), (9, 5), (18, -4), (18, 14)])
            pygame.draw.polygon(surf, (232, 184, 56), crown)
            pygame.draw.polygon(surf, (120, 84, 16), crown, SS)

    def _render_back(self) -> pygame.Surface:
        p = self.palette
        surf = self._frame(p.back_a, p.paper, None)
        w, h = surf.get_size()
        inner = surf.get_rect().inflate(-16 * SS, -16 * SS)
        pattern = pygame.Surface((w, h), pygame.SRCALPHA)
        step = 16 * SS
        for i in range(-h, w, step):
            pygame.draw.line(pattern, p.back_b, (i, 0), (i + h, h), SS)
            pygame.draw.line(pattern, p.back_b, (i + h, 0), (i, h), SS)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), inner, border_radius=6 * SS)
        pattern.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(pattern, (0, 0))
        pygame.draw.rect(surf, p.paper, inner, width=2 * SS, border_radius=6 * SS)
        return pygame.transform.smoothscale(surf, (CARD_W, CARD_H))


class PngDeckStyle(DeckStyle):
    def __init__(self, folder: Path) -> None:
        self.name = folder.name
        self.label = folder.name.replace("_", " ").capitalize()
        self._faces = {
            Card(suit, rank): self._load(folder / f"{suit.value}_{int(rank)}.png")
            for suit in Suit for rank in Rank
        }
        self._back = self._load(folder / "back.png")

    @staticmethod
    def _load(path: Path) -> pygame.Surface:
        if not path.is_file():
            raise FileNotFoundError(path)
        return pygame.transform.smoothscale(pygame.image.load(str(path)).convert_alpha(), (CARD_W, CARD_H))

    def face(self, card: Card) -> pygame.Surface:
        return self._faces[card]

    def back(self) -> pygame.Surface:
        return self._back


# --- stili predefiniti ------------------------------------------------------------
def _napoletano() -> ProceduralStyle:
    palette = Palette(
        paper=(247, 238, 216), border=(92, 58, 30), inner_border=None, ink=(58, 36, 20),
        suits={Suit.DENARI: (214, 164, 36), Suit.COPPE: (186, 38, 38),
               Suit.SPADE: (40, 72, 150), Suit.BASTONI: (46, 112, 60)},
        back_a=(150, 28, 36), back_b=(210, 120, 110),
    )
    return ProceduralStyle("napoletano", "Napoletano", palette, {r: str(int(r)) for r in Rank})


def _piacentino() -> ProceduralStyle:
    palette = Palette(
        paper=(252, 252, 246), border=(24, 44, 92), inner_border=(150, 164, 200), ink=(24, 32, 56),
        suits={Suit.DENARI: (232, 148, 20), Suit.COPPE: (206, 30, 66),
               Suit.SPADE: (52, 60, 96), Suit.BASTONI: (120, 78, 38)},
        back_a=(26, 52, 112), back_b=(120, 150, 214),
    )
    labels = {r: str(int(r)) for r in Rank}
    labels.update({Rank.ASSO: "A", Rank.FANTE: "F", Rank.CAVALLO: "C", Rank.RE: "R"})
    return ProceduralStyle("piacentino", "Piacentino", palette, labels)


def available_styles(root: Path | None = None) -> dict[str, DeckStyle]:
    """Mazzi predefiniti + ogni cartella valida di PNG in `assets/decks`."""
    styles: dict[str, DeckStyle] = {s.name: s for s in (_napoletano(), _piacentino())}
    root = root or resource_path("assets/decks")
    if root.is_dir():
        for folder in sorted(p for p in root.iterdir() if p.is_dir()):
            try:
                styles[folder.name] = PngDeckStyle(folder)
            except (FileNotFoundError, pygame.error):
                continue  # cartella incompleta: ignorata
    return styles
