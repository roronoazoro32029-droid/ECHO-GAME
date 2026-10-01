# ECHO: ZERO PROTOCOL

A 2D top-down sci-fi thriller built with Python and Pygame.

> *The game watches how the player behaves, remembers it, and changes how the world responds.*

## Quick Start

### 1. Prerequisites
- Python 3.10 or newer — [python.org](https://www.python.org/downloads/)
- pip (included with Python)

### 2. Setup (one-time)

Open a terminal in the project folder and run:

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the game

```bash
python main.py
```

## Controls

| Key | Action |
|---|---|
| W/A/S/D | Move |
| Mouse | Aim |
| E | Interact |
| F | Flashlight |
| Shift | Sprint |
| Esc | Pause |
| Tab | Inventory (coming soon) |
| M | Map (coming soon) |

## Project Structure

```
echo_zero_protocol/
├── main.py              # Entry point
├── game/
│   ├── game.py          # Main game loop & state management
│   ├── camera.py        # Smooth-follow camera with shake
│   ├── settings.py      # All constants & configuration
│   └── world.py         # Tile-based level, collision, interactables
├── entities/
│   └── player.py        # Player movement, stamina, flashlight
├── ui/
│   ├── main_menu.py     # Animated sci-fi main menu
│   ├── hud.py           # Health/energy/stamina bars, objectives
│   └── pause_menu.py    # Pause overlay
└── requirements.txt
```

## Development Roadmap

- [x] Phase 1 — Foundation (movement, camera, collision, menu, HUD)
- [ ] Phase 2 — Combat & enemies (FSM AI, pathfinding, weapons)
- [ ] Phase 3 — Systems (inventory, dialogue, save/load, behavior tracking)
- [ ] Phase 4 — Story (chapters, ECHO personality, endings)
- [ ] Phase 5 — Polish (audio, particles, transitions, balancing)
