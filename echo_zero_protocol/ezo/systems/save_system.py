
import json,os
from pathlib import Path
SAVE_DIR=Path("saves"); SAVE_FILE=SAVE_DIR/"savegame.json"; AUTOSAVE_FILE=SAVE_DIR/"autosave.json"
def ensure_save_dir(): SAVE_DIR.mkdir(exist_ok=True)
def save_game(game,fp=None):
    if fp is None: fp=SAVE_FILE
    ensure_save_dir(); p=game.player
    data={"version":1,"player":{"x":round(p.pos.x,1),"y":round(p.pos.y,1),"health":round(p.health,1),"max_health":p.max_health,
        "stamina":round(p.stamina,1),"energy":round(p.energy,1),"ammo":p.ammo,"max_ammo":p.max_ammo,"flashlight_on":p.flashlight_on},
        "weapon":game.current_weapon.get("name","PULSE PISTOL"),"inventory":game.inventory.to_dict(),
        "behavior":game.behavior.to_dict(),"echo":game.echo_ai.to_dict(),"story_flags":dict(game.story_flags),
        "story":game.story.to_dict(),
        "world":{"open_doors":[(o["row"],o["col"]) for o in game.world.interactables if o["type"]=="door" and o.get("open")],
            "used_terminals":[(o["row"],o["col"]) for o in game.world.interactables if o["type"]=="terminal" and o.get("used")],
            "used_recordings":[(o["row"],o["col"]) for o in game.world.interactables if o["type"]=="recording" and o.get("used")]},
        "objective":game.hud.objective}
    try:
        with open(fp,"w") as f: json.dump(data,f,indent=2)
        return True
    except: return False
def load_game(game,fp=None):
    if fp is None: fp=SAVE_FILE
    if not os.path.exists(fp): return False
    try:
        with open(fp,"r") as f: data=json.load(f)
    except: return False
    from game.world import World; from entities.player import Player
    from systems.story_manager import StoryManager; from game.settings import WEAPONS,SCREEN_WIDTH,SCREEN_HEIGHT
    game.story=StoryManager()
    if "story" in data: game.story.from_dict(data["story"])
    game.world=World(chapter=game.story.current_chapter)
    px,py=data["player"]["x"],data["player"]["y"]; game.player=Player(px,py)
    pd=data["player"]; game.player.health=pd.get("health",100); game.player.stamina=pd.get("stamina",100)
    game.player.energy=pd.get("energy",100); game.player.ammo=pd.get("ammo",24); game.player.max_ammo=pd.get("max_ammo",48)
    game.player.flashlight_on=pd.get("flashlight_on",False)
    wn=data.get("weapon","PULSE PISTOL")
    for wk,wd in WEAPONS.items():
        if wd["name"]==wn: game.current_weapon=wd; break
    game.inventory.from_dict(data.get("inventory",{})); game.behavior.from_dict(data.get("behavior",{}))
    game.echo_ai.from_dict(data.get("echo",{})); game.story_flags=data.get("story_flags",{})
    wd=data.get("world",{})
    for r,c in wd.get("open_doors",[]):
        for o in game.world.interactables:
            if o["type"]=="door" and o["row"]==r and o["col"]==c: game.world.open_door(o)
    for r,c in wd.get("used_terminals",[]):
        for o in game.world.interactables:
            if o["type"]=="terminal" and o["row"]==r and o["col"]==c: o["used"]=True
    for r,c in wd.get("used_recordings",[]):
        for o in game.world.interactables:
            if o["type"]=="recording" and o["row"]==r and o["col"]==c: o["used"]=True
    game.camera.offset.x=px-SCREEN_WIDTH/2; game.camera.offset.y=py-SCREEN_HEIGHT/2
    game.hud.objective=data.get("objective","Explore."); game._spawn_enemies()
    game.projectiles.clear(); game.particles.particles.clear(); game._damage_flash=0; game._echo_intro_done=True
    return True
def has_save(fp=None): return os.path.exists(fp or SAVE_FILE)
def autosave(game): return save_game(game,AUTOSAVE_FILE)
