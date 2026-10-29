from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from briscola.ui.paths import settings_path


@dataclass
class Settings:
    deck: str = "napoletano"

    @classmethod
    def load(cls, path: Path | None = None) -> Settings:
        """Legge le impostazioni; file mancante o corrotto -> valori di default."""
        path = path or settings_path()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(deck=str(data.get("deck", cls.deck)))
        except (OSError, ValueError, AttributeError):
            return cls()

    def save(self, path: Path | None = None) -> None:
        path = path or settings_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        except OSError:
            pass  # impostazioni non salvabili: il gioco continua comunque
