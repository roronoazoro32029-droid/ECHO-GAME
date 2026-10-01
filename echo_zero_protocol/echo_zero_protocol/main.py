#!/usr/bin/env python3
"""
ECHO: ZERO PROTOCOL — Entry point.
Run:  python main.py
"""

from pathlib import Path
from game.game import Game


def main():
    Path("saves").mkdir(exist_ok=True)
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
