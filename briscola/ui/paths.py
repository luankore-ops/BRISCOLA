"""Percorsi di risorse e impostazioni, validi sia da script sia dentro l'.exe PyInstaller."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """Risorsa di sola lettura (asset). In un .exe `--onefile` vive in sys._MEIPASS."""
    base = getattr(sys, "_MEIPASS", None)
    root = Path(base) if base else Path(__file__).resolve().parents[2]
    return root / relative


def settings_path() -> Path:
    """File delle impostazioni utente (scrivibile, fuori dall'eseguibile)."""
    appdata = os.environ.get("APPDATA")
    folder = Path(appdata) / "Briscola" if appdata else Path.home() / ".briscola"
    return folder / "settings.json"
