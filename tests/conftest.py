import os

# Pygame senza finestra né audio: i test della UI girano anche su server/CI.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
