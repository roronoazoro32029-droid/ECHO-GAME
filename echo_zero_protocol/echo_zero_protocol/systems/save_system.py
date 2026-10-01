"""
Save System — serialize/deserialize full game state to JSON.
"""
import json
import os
from pathlib import Path

SAVE_DIR = Path("saves")
SAVE_FILE = SAVE_DIR / "savegame.json"
AUTOSAVE_FILE = SAVE_DIR / "autosave.json"


def ensure_save_dir():
    SAVE_DIR.mkdir(exist_ok=True)


def save_game(game, filepath=None):
    """Serialize the game state to a JSON file."""
    if filepath is None:
        filepath = SAVE_FILE
    ensure_save_dir()

    player = game.player
    data = {
        "version": 1,
        "player": {
            "x": round(player.pos.x, 1),
            "y": round(player.pos.y, 1),
            "health": round(player.health, 1),
            "max_health": player.max_health,
            "stamina": round(player.stamina, 1),
            "energy": round(player.energy, 1),
            "ammo": player.ammo,
            "max_ammo": player.max_ammo,
            "flashlight_on": player.flashlight_on,
        },
        "weapon": game.current_weapon.get("name", "PULSE PISTOL"),
        "inventory": game.inventory.to_dict(),
        "behavior": game.behavior.to_dict(),
        "echo": game.echo_ai.to_dict(),
        "story_flags": dict(game.story_flags),
        "story": game.story.to_dict(),
        "world": {
            "open_doors": [
                (obj["row"], obj["col"])
                for obj in game.world.interactables
                if obj["type"] == "door" and obj.get("open")
            ],
            "used_terminals": [
                (obj["row"], obj["col"])
                for obj in game.world.interactables
                if obj["type"] == "terminal" and obj.get("used")
            ],
            "used_recordings": [
                (obj["row"], obj["col"])
                for obj in game.world.interactables
                if obj["type"] == "recording" and obj.get("used")
            ],
        },
        "objective": game.hud.objective,
        "enemies_killed": sum(1 for _ in []),  # placeholder
    }

    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False


def load_game(game, filepath=None) -> bool:
    """Deserialize game state from JSON. Returns True on success."""
    if filepath is None:
        filepath = SAVE_FILE

    if not os.path.exists(filepath):
        return False

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Load error: {e}")
        return False

    # rebuild world — use chapter from story data
    from game.world import World
    from entities.player import Player
    from systems.story_manager import StoryManager
    from game.settings import WEAPONS, SCREEN_WIDTH, SCREEN_HEIGHT

    # restore story first (need chapter number for world)
    game.story = StoryManager()
    if "story" in data:
        game.story.from_dict(data["story"])

    game.world = World(chapter=game.story.current_chapter)
    px = data["player"]["x"]
    py = data["player"]["y"]
    game.player = Player(px, py)

    # restore player stats
    p = game.player
    pd = data["player"]
    p.health = pd.get("health", p.max_health)
    p.max_health = pd.get("max_health", p.max_health)
    p.stamina = pd.get("stamina", p.max_stamina)
    p.energy = pd.get("energy", p.max_energy)
    p.ammo = pd.get("ammo", 24)
    p.max_ammo = pd.get("max_ammo", 48)
    p.flashlight_on = pd.get("flashlight_on", False)

    # weapon
    weapon_name = data.get("weapon", "PULSE PISTOL")
    for wkey, wdata in WEAPONS.items():
        if wdata["name"] == weapon_name:
            game.current_weapon = wdata
            break

    # inventory
    game.inventory.from_dict(data.get("inventory", {}))

    # behavior
    game.behavior.from_dict(data.get("behavior", {}))

    # echo AI
    game.echo_ai.from_dict(data.get("echo", {}))

    # story flags
    game.story_flags = data.get("story_flags", {})

    # world state
    world_data = data.get("world", {})
    for r, c in world_data.get("open_doors", []):
        for obj in game.world.interactables:
            if obj["type"] == "door" and obj["row"] == r and obj["col"] == c:
                game.world.open_door(obj)
    for r, c in world_data.get("used_terminals", []):
        for obj in game.world.interactables:
            if obj["type"] == "terminal" and obj["row"] == r and obj["col"] == c:
                obj["used"] = True
    for r, c in world_data.get("used_recordings", []):
        for obj in game.world.interactables:
            if obj["type"] == "recording" and obj["row"] == r and obj["col"] == c:
                obj["used"] = True

    # camera
    game.camera.offset.x = px - SCREEN_WIDTH / 2
    game.camera.offset.y = py - SCREEN_HEIGHT / 2

    # objective
    game.hud.objective = data.get("objective", "Explore the facility.")

    # respawn enemies
    game._spawn_enemies()

    # clear combat state
    game.projectiles.clear()
    game.particles.particles.clear()
    game._damage_flash = 0
    game._echo_intro_done = True  # skip intro on load

    return True


def has_save(filepath=None) -> bool:
    if filepath is None:
        filepath = SAVE_FILE
    return os.path.exists(filepath)


def autosave(game):
    return save_game(game, AUTOSAVE_FILE)
