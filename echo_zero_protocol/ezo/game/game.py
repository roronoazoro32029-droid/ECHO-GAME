"""Game — master class: all phases + Phase 5 audio."""
import sys,math,random,pygame
from game.settings import *
from game.camera import Camera
from game.world import World
from game.levels import ENEMIES_CH0,ENEMIES_CH1
from entities.player import Player
from entities.watcher import Watcher
from entities.sentinel import Sentinel
from entities.hunter import Hunter
from systems.combat import Projectile,ParticleManager
from systems.inventory import Inventory
from systems.save_system import save_game,load_game,has_save,autosave
from systems.story_manager import StoryManager
from systems.audio import AudioManager
from ai.player_behavior import PlayerBehavior
from ai.echo_ai import EchoAI
from ui.main_menu import MainMenu
from ui.hud import HUD
from ui.pause_menu import PauseMenu
from ui.inventory_ui import InventoryUI
from ui.dialogue_ui import DialogueUI
from ui.recording_ui import RecordingUI
from ui.story_screens import ChapterIntroUI,EndingUI

class Game:
    def __init__(s):
        pygame.init()
        s.screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        s.clock=pygame.time.Clock();s.running=True;s.state=STATE_MENU
        s.audio=AudioManager()
        s.main_menu=MainMenu(s.screen);s.pause_menu=PauseMenu();s.hud=HUD()
        s.camera=Camera();s.particles=ParticleManager()
        s.world=None;s.player=None
        s.inventory=Inventory();s.behavior=PlayerBehavior();s.echo_ai=EchoAI()
        s.inventory_ui=InventoryUI();s.dialogue_ui=DialogueUI()
        s.story=StoryManager();s.recording_ui=RecordingUI()
        s.chapter_intro_ui=ChapterIntroUI();s.ending_ui=EndingUI()
        s.story_flags={};s._pending_dlg=None;s._last_cid=""
        s.projectiles=[];s.enemies=[];s.player_shooting=False
        s.fire_timer=0.0;s.current_weapon=WEAPONS["pulse_pistol"]
        s._dmg_flash=0.0;s._echo_cd=30.0;s._auto_cd=120.0;s._low_hp_w=False
        s.darkness=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
        s._ei_done=False;s._ei_timer=0.0
        s._ei_msgs=[(1.5,"Systems online. Neural interface connected."),(5.0,"Your motor functions are stable."),
            (8.5,"Warning: hostile machines detected."),(12.0,"I can guide you. Stay alert.")]
        s._ei_idx=0

    def run(s):
        while s.running:
            dt=min(s.clock.tick(FPS)/1000.0,0.05)
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT:s.running=False;break
                s._event(ev)
            s._update(dt);s._draw();pygame.display.flip()
        pygame.quit();sys.exit()

    def _event(s,ev):
        if s.state==STATE_MENU:
            a=s.main_menu.handle_event(ev)
            if a=="NEW GAME":s._new_game()
            elif a=="CONTINUE":
                if s.player:s.state=STATE_PLAYING
                elif has_save():
                    if load_game(s):s.state=STATE_PLAYING;s.hud.show_echo("Save data restored.",2.5);s.audio.play_music("explore",0.25)
            elif a=="EXIT":s.running=False
        elif s.state==STATE_PLAYING:
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE:s.state=STATE_PAUSED
                elif ev.key==pygame.K_f:s.player.toggle_flashlight()
                elif ev.key==pygame.K_e:s._interact()
                elif ev.key==pygame.K_q:s._emp()
                elif ev.key==pygame.K_TAB:s.state=STATE_INVENTORY
                elif ev.key==pygame.K_1:s.current_weapon=WEAPONS["pulse_pistol"];s.hud.show_echo("Pulse Pistol.",1.5)
                elif ev.key==pygame.K_2:s.current_weapon=WEAPONS["arc_rifle"];s.hud.show_echo("Arc Rifle.",1.5)
        elif s.state==STATE_PAUSED:
            a=s.pause_menu.handle_event(ev)
            if a=="RESUME":s.state=STATE_PLAYING
            elif a=="SAVE GAME":
                if save_game(s):s.hud.show_echo("Game saved.",2.0)
                s.state=STATE_PLAYING
            elif a=="MAIN MENU":s.state=STATE_MENU
        elif s.state==STATE_INVENTORY:
            a,msg=s.inventory_ui.handle_event(ev,s.inventory,s.player)
            if a=="close":s.state=STATE_PLAYING
            elif a in("use","drop")and msg:s.hud.show_echo(msg,2.0)
            if a=="use":s.behavior.on_item_used()
        elif s.state==STATE_DIALOGUE:
            r=s.dialogue_ui.handle_event(ev)
            if r:
                if r["type"]=="choice":
                    s._last_cid=r["id"];s.echo_ai.process_choice(r["id"])
                    if s._pending_dlg:
                        follow=s.story.get_terminal_follow_up(s._pending_dlg,r["id"])
                        if follow:s._pending_dlg=None;s.dialogue_ui.start("ECHO",follow);return
                    s._pending_dlg=None
                    if s.story.is_final_chapter()and s.story.terminal_index>=3:s._ending();return
                s.state=STATE_PLAYING
        elif s.state==STATE_RECORDING:
            if s.recording_ui.handle_event(ev):s.state=STATE_PLAYING
        elif s.state==STATE_INTRO:
            if s.chapter_intro_ui.handle_event(ev):s.state=STATE_PLAYING;s.audio.play_music("explore",0.25)
        elif s.state==STATE_ENDING:
            r=s.ending_ui.handle_event(ev)
            if r=="main_menu":s.state=STATE_MENU

    def _update(s,dt):
        if s.state==STATE_MENU:s.main_menu.update(dt);s.audio.play_music("menu",0.25)
        elif s.state==STATE_DIALOGUE:s.dialogue_ui.update(dt)
        elif s.state==STATE_INTRO:s.chapter_intro_ui.update(dt)
        elif s.state==STATE_ENDING:s.ending_ui.update(dt);s.audio.stop_music(2000)
        elif s.state==STATE_PLAYING:s._tick(dt)

    def _tick(s,dt):
        keys=pygame.key.get_pressed();mouse=pygame.mouse.get_pos();mb=pygame.mouse.get_pressed()
        s.player.update(dt,keys,mouse,s.camera,s.world.wall_rects)
        s.camera.update(s.player.pos,dt);s.hud.update(dt)
        s.fire_timer=max(0,s.fire_timer-dt);s._dmg_flash=max(0,s._dmg_flash-dt*3)
        s.behavior.update(dt,s.player.health,s.player.max_health);s.echo_ai.update(dt)
        s.player_shooting=False
        if mb[0]and s.fire_timer<=0:s._shoot()
        # interaction prompt
        nb=s.world.get_nearby_interactable(s.player.pos,60)
        if nb:
            t=nb["type"]
            if t=="door"and not nb["open"]:s.hud.interaction_prompt="[E] Open Door"
            elif t=="terminal"and not nb.get("used"):s.hud.interaction_prompt="[E] Access Terminal"
            elif t=="medical":s.hud.interaction_prompt="[E] Examine"
            elif t=="recording"and not nb.get("used"):s.hud.interaction_prompt="[E] Play Recording"
            elif t=="exit":s.hud.interaction_prompt="[E] Proceed"
            else:s.hud.interaction_prompt=None
        else:s.hud.interaction_prompt=None
        # exit zone
        if s.world.check_exit_zone((s.player.pos.x,s.player.pos.y)):
            if not s.story.is_final_chapter():s._advance_ch()
        # open doors set
        od=set((o["row"],o["col"])for o in s.world.interactables if o["type"]=="door"and o.get("open"))
        # enemy AI
        ctx={"player_pos":(s.player.pos.x,s.player.pos.y),"tile_map":s.world.tile_map,
            "wall_rects":s.world.wall_rects,"open_doors":od,"player_sprinting":s.player.sprinting,
            "player_shooting":s.player_shooting,"enemy_shots":[]}
        for e in s.enemies:
            prev=e.fsm.current_name if e.fsm else""
            e.update(dt,ctx)
            new=e.fsm.current_name if e.fsm else""
            if prev in("chase","attack")and new in("search","patrol"):
                s.behavior.on_enemy_avoided()
                c=s.echo_ai.on_enemy_avoided(s.behavior)
                if c:s.hud.show_echo(c,3.0)
        for shot in ctx["enemy_shots"]:
            s.projectiles.append(Projectile(shot["pos"][0],shot["pos"][1],shot["angle"],shot["speed"],shot["damage"],shot["color"],owner="enemy",size=4))
            s.particles.emit_muzzle_flash(shot["pos"][0],shot["pos"][1],shot["angle"],shot["color"])
            s.audio.play_sfx("enemy_shoot",0.3)
        for p in s.projectiles:
            p.update(dt,s.world.wall_rects)
            if not p.alive:s.particles.emit_sparks(p.pos.x,p.pos.y,p.color,5)
        # player bullets hit enemies
        for p in s.projectiles:
            if not p.alive or p.owner!="player":continue
            for e in s.enemies:
                if not e.alive:continue
                if math.hypot(p.pos.x-e.pos.x,p.pos.y-e.pos.y)<e.radius+p.size:
                    e.take_damage(p.damage);s.behavior.on_damage_dealt(p.damage);p.alive=False
                    s.particles.emit_sparks(p.pos.x,p.pos.y,e.color,10);s.camera.shake(3);s.audio.play_sfx("impact",0.4)
                    if not e.alive:s._kill(e)
                    break
        # enemy bullets hit player
        for p in s.projectiles:
            if not p.alive or p.owner!="enemy":continue
            if math.hypot(p.pos.x-s.player.pos.x,p.pos.y-s.player.pos.y)<s.player.radius+p.size:
                s.player.take_damage(p.damage);p.alive=False;s._dmg_flash=1.0
                s.camera.shake(6);s.particles.emit_sparks(p.pos.x,p.pos.y,RED,8)
                s.audio.play_sfx("player_hurt",0.6)
        s.projectiles=[p for p in s.projectiles if p.alive]
        s.enemies=[e for e in s.enemies if e.alive]
        s.particles.update(dt)
        # dynamic music
        alert=any(e.fsm and e.fsm.current_name in("chase","attack","flank")for e in s.enemies if e.alive)
        s.audio.update(dt,alert)
        if not alert and s.audio.current_music!="explore"and not s.audio.combat_active:
            s.audio.play_music("explore",0.25)
        # HUD sync
        s.hud.weapon_name=s.current_weapon["name"]
        s.hud.behavior_profile=s.behavior.get_profile()
        s.hud.echo_trust=s.echo_ai.get_trust_label()
        # ECHO comments
        s._echo_cd-=dt
        if s._echo_cd<=0:
            s._echo_cd=random.uniform(25,50);c=s.echo_ai.get_periodic_comment(s.behavior)
            if c:s.hud.show_echo(c,4.0)
        if s.player.health<25 and not s._low_hp_w:
            s._low_hp_w=True;w=s.echo_ai.on_low_health()
            if w:s.hud.show_echo(w,3.0)
        elif s.player.health>50:s._low_hp_w=False
        s._auto_cd-=dt
        if s._auto_cd<=0:s._auto_cd=120.0;autosave(s)
        if not s._ei_done:
            s._ei_timer+=dt
            if s._ei_idx<len(s._ei_msgs):
                tt,msg=s._ei_msgs[s._ei_idx]
                if s._ei_timer>=tt:s.hud.show_echo(msg,3.0);s._ei_idx+=1
            else:s._ei_done=True
        if not s.player.alive:s.hud.show_echo("Critical failure. Systems shutting down.",5.0)

    def _draw(s):
        if s.state==STATE_MENU:s.main_menu.draw()
        elif s.state==STATE_INTRO:s.chapter_intro_ui.draw(s.screen)
        elif s.state==STATE_ENDING:s.ending_ui.draw(s.screen)
        elif s.state in(STATE_PLAYING,STATE_PAUSED,STATE_INVENTORY,STATE_DIALOGUE,STATE_RECORDING):
            s.screen.fill(DARK_BG);s.world.draw(s.screen,s.camera)
            for e in s.enemies:e.draw(s.screen,s.camera)
            for p in s.projectiles:p.draw(s.screen,s.camera)
            s.particles.draw(s.screen,s.camera);s.player.draw(s.screen,s.camera)
            # vignette
            s.darkness.fill((0,0,0,0));w,h=SCREEN_WIDTH,SCREEN_HEIGHT
            for i in range(100):a=int(40*(1-i/100));pygame.draw.rect(s.darkness,(0,0,0,a),(i,i,w-2*i,h-2*i),1)
            s.screen.blit(s.darkness,(0,0))
            if s._dmg_flash>0:
                fl=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
                fl.fill((200,30,30,int(80*s._dmg_flash)));s.screen.blit(fl,(0,0))
            s.hud.draw(s.screen,s.player)
            if s.state==STATE_PAUSED:s.pause_menu.draw(s.screen)
            elif s.state==STATE_INVENTORY:s.inventory_ui.draw(s.screen,s.inventory,s.player)
            elif s.state==STATE_DIALOGUE:s.dialogue_ui.draw(s.screen)
            elif s.state==STATE_RECORDING:s.recording_ui.draw(s.screen)

    def _shoot(s):
        w=s.current_weapon
        if s.player.ammo<=0:return
        s.player.ammo-=1;s.fire_timer=w["fire_rate"];s.player_shooting=True;s.behavior.on_shot_fired()
        sp=math.radians(random.uniform(-w["spread"],w["spread"]));a=s.player.angle+sp
        mx,my=s.player.pos.x+math.cos(s.player.angle)*24,s.player.pos.y+math.sin(s.player.angle)*24
        s.projectiles.append(Projectile(mx,my,a,w["speed"],w["damage"],w["color"],owner="player",size=w["bullet_size"]))
        s.particles.emit_muzzle_flash(mx,my,s.player.angle,w["color"]);s.camera.shake(2)
        s.audio.play_sfx("shoot_rifle"if w is WEAPONS["arc_rifle"]else"shoot_pistol",0.5)
    def _emp(s):
        if s.player.energy<30:s.hud.show_echo("Insufficient energy.",2.0);return
        s.player.energy-=30;r=WEAPONS["emp_device"].get("aoe_radius",150)
        px,py=s.player.pos.x,s.player.pos.y;s.particles.emit_emp(px,py,r);s.camera.shake(8);s.audio.play_sfx("emp",0.6)
        st=0
        for e in s.enemies:
            if e.alive and math.hypot(e.pos.x-px,e.pos.y-py)<=r:
                e.apply_stun(3.0);e.take_damage(WEAPONS["emp_device"]["damage"]);s.particles.emit_sparks(e.pos.x,e.pos.y,YELLOW,12);st+=1
        s.hud.show_echo(f"EMP discharged. {st} target(s) disabled."if st else"EMP discharged. No targets.",2.5)
    def _kill(s,e):
        s.particles.emit_death(e.pos.x,e.pos.y,e.color);s.behavior.on_kill();s.audio.play_sfx("enemy_death",0.5)
        c=s.echo_ai.on_kill(s.behavior);s.hud.show_echo(c or"Hostile neutralized.",2.0)
        drops={"watcher":[("ammo_pack",0.5)],"sentinel":[("ammo_pack",0.6),("medkit",0.3),("energy_cell",0.2)],"hunter":[("medkit",0.5),("energy_cell",0.4),("emp_charge",0.2)]}
        for iid,ch in drops.get(e.enemy_type,[]):
            if random.random()<ch and s.inventory.add_item(iid):
                from systems.inventory import ITEM_DB
                s.hud.show_echo(f"Acquired: {ITEM_DB[iid]['name']}",2.0);s.audio.play_sfx("pickup",0.4)
    def _interact(s):
        nb=s.world.get_nearby_interactable(s.player.pos,60)
        if not nb:return
        t=nb["type"]
        if t=="door"and not nb["open"]:
            s.world.open_door(nb);s.behavior.on_door_opened();s.hud.show_echo("Door unlocked.",2.0);s.audio.play_sfx("door_open",0.5)
        elif t=="terminal"and not nb.get("used"):
            nb["used"]=True;s.behavior.on_terminal_accessed();s.camera.shake(5);s.audio.play_sfx("terminal",0.5)
            s.player.ammo=min(s.player.max_ammo,s.player.ammo+8)
            dlg=s.story.get_terminal_dialogue()
            if dlg:s._pending_dlg=dlg;s.dialogue_ui.start(dlg["speaker"],dlg["text"],dlg.get("choices"));s.state=STATE_DIALOGUE
            else:r=s.echo_ai.on_terminal_access(s.behavior);s.hud.show_echo(r,3.0)
        elif t=="medical":
            if s.player.health<s.player.max_health:
                s.player.heal(30);s.behavior.on_item_used();s.hud.show_echo("Medical supplies. +30 HP.",2.5);s.audio.play_sfx("heal",0.5)
            else:s.hud.show_echo("Medical bay. No treatment required.",2.0)
        elif t=="recording"and not nb.get("used"):
            nb["used"]=True;s.behavior.on_evidence_found();s.audio.play_sfx("recording",0.5)
            rec=s.story.get_next_recording()
            if rec:s.recording_ui.start(rec);s.state=STATE_RECORDING;r=s.echo_ai.on_evidence_found(s.behavior);s.hud.show_echo(r,3.0)
            else:s.hud.show_echo("Corrupted data.",2.0)
        elif t=="exit":
            if not s.story.is_final_chapter():s._advance_ch()
            else:s.hud.show_echo("Exit controls locked. Find a terminal.",3.0)
    def _advance_ch(s):
        if not s.story.advance_chapter():return
        ch=s.story.current_chapter;autosave(s);s.audio.play_sfx("chapter_transition",0.6);s.audio.stop_music(1500)
        s.world=World(chapter=ch);sx,sy=s.world.get_spawn_pos()
        s.player.pos.x=sx;s.player.pos.y=sy;s.camera.offset.x=sx-SCREEN_WIDTH/2;s.camera.offset.y=sy-SCREEN_HEIGHT/2
        s.projectiles.clear();s.particles.particles.clear();s._spawn()
        intro=s.story.get_chapter_intro()
        if intro:s.chapter_intro_ui.start(intro);s.state=STATE_INTRO
        obj={1:"Explore the Research Wing. Find Dr. Voss's recordings."}
        s.hud.objective=obj.get(ch,"Explore.")
    def _ending(s):
        eid=s.story.determine_ending(s.echo_ai.trust,s._last_cid)
        e=s.story.get_ending(eid)
        if e:s.ending_ui.start(e,s.behavior.to_dict(),s.echo_ai.trust);s.state=STATE_ENDING;s.audio.stop_music(2000)
    def _new_game(s):
        s.story=StoryManager();s.world=World(chapter=0)
        sx,sy=s.world.get_spawn_pos();s.player=Player(sx,sy)
        s.player.ammo=WEAPONS["pulse_pistol"]["ammo_start"];s.player.max_ammo=WEAPONS["pulse_pistol"]["ammo_max"]
        s.current_weapon=WEAPONS["pulse_pistol"]
        s.inventory=Inventory();s.behavior=PlayerBehavior();s.echo_ai=EchoAI()
        s.story_flags={};s._pending_dlg=None;s._last_cid=""
        s.inventory.add_item("medkit",2);s.inventory.add_item("ammo_pack",1)
        s.camera.offset.x=sx-SCREEN_WIDTH/2;s.camera.offset.y=sy-SCREEN_HEIGHT/2
        s.hud.objective="Find a way out of Medical Sector A."
        s.projectiles.clear();s.particles.particles.clear()
        s._dmg_flash=0;s._auto_cd=120.0;s._echo_cd=30.0;s._low_hp_w=False
        s._spawn()
        intro=s.story.get_chapter_intro()
        if intro:s.chapter_intro_ui.start(intro);s.state=STATE_INTRO
        else:s.state=STATE_PLAYING
        s._ei_done=False;s._ei_timer=0.0;s._ei_idx=0
    def _spawn(s):
        TS=TILE_SIZE;s.enemies=[];data=ENEMIES_CH0 if s.story.current_chapter==0 else ENEMIES_CH1
        for e in data:
            x,y=e["x"]*TS,e["y"]*TS;pat=[(px*TS,py*TS)for px,py in e["patrol"]]
            if e["type"]=="watcher":s.enemies.append(Watcher(x,y,patrol_points=pat))
            elif e["type"]=="sentinel":s.enemies.append(Sentinel(x,y,patrol_points=pat))
            elif e["type"]=="hunter":s.enemies.append(Hunter(x,y,patrol_points=pat))
