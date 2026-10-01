"""
Game — master class with full story integration:
  chapters, recordings, dialogue, endings, save/load, behavior, ECHO AI.
"""
import sys, math, random
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, DARK_BG,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_INVENTORY, STATE_DIALOGUE, STATE_RECORDING,
    STATE_INTRO, STATE_ENDING,
    WEAPONS, TILE_SIZE, CYAN, YELLOW, RED
)
from game.camera import Camera
from game.world import World
from game.levels import ENEMIES_CH0, ENEMIES_CH1
from entities.player import Player
from entities.watcher import Watcher
from entities.sentinel import Sentinel
from entities.hunter import Hunter
from systems.combat import Projectile, ParticleManager
from systems.inventory import Inventory
from systems.save_system import save_game, load_game, has_save, autosave
from systems.story_manager import StoryManager
from ai.player_behavior import PlayerBehavior
from ai.echo_ai import EchoAI
from ui.main_menu import MainMenu
from ui.hud import HUD
from ui.pause_menu import PauseMenu
from ui.inventory_ui import InventoryUI
from ui.dialogue_ui import DialogueUI
from ui.recording_ui import RecordingUI
from ui.story_screens import ChapterIntroUI, EndingUI


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU

        # core systems
        self.main_menu = MainMenu(self.screen)
        self.pause_menu = PauseMenu()
        self.hud = HUD()
        self.camera = Camera()
        self.particles = ParticleManager()
        self.world = None
        self.player = None

        # Phase 3 systems
        self.inventory = Inventory()
        self.behavior = PlayerBehavior()
        self.echo_ai = EchoAI()
        self.inventory_ui = InventoryUI()
        self.dialogue_ui = DialogueUI()
        self.story_flags: dict = {}

        # Phase 4 systems
        self.story = StoryManager()
        self.recording_ui = RecordingUI()
        self.chapter_intro_ui = ChapterIntroUI()
        self.ending_ui = EndingUI()
        self._pending_dialogue = None  # terminal dialogue waiting for follow-up
        self._last_choice_id = ""

        # combat
        self.projectiles: list[Projectile] = []
        self.enemies: list = []
        self.player_shooting = False
        self.fire_timer = 0.0
        self.current_weapon = WEAPONS["pulse_pistol"]

        # timers
        self._damage_flash = 0.0
        self._echo_comment_timer = 30.0
        self._autosave_timer = 120.0
        self._low_health_warned = False

        self.darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # echo intro
        self._echo_intro_done = False
        self._echo_intro_timer = 0.0
        self._echo_messages = [
            (1.5,  "Systems online. Neural interface connected."),
            (5.0,  "Your motor functions are stable."),
            (8.5,  "Warning: hostile machines detected in the facility."),
            (12.0, "I can guide you. Stay alert."),
        ]
        self._echo_msg_index = 0

    # ══════════════════════════════════════════════════════
    #  MAIN LOOP
    # ══════════════════════════════════════════════════════
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self._handle_event(event)
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    # ══════════════════════════════════════════════════════
    #  EVENTS
    # ══════════════════════════════════════════════════════
    def _handle_event(self, event):
        if self.state == STATE_MENU:
            action = self.main_menu.handle_event(event)
            if action == "NEW GAME":
                self._start_new_game()
            elif action == "CONTINUE":
                if self.player:
                    self.state = STATE_PLAYING
                elif has_save():
                    if load_game(self):
                        self.state = STATE_PLAYING
                        self.hud.show_echo("Save data restored.", 2.5)
            elif action == "EXIT":
                self.running = False

        elif self.state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = STATE_PAUSED
                elif event.key == pygame.K_f:
                    self.player.toggle_flashlight()
                elif event.key == pygame.K_e:
                    self._interact()
                elif event.key == pygame.K_q:
                    self._use_emp()
                elif event.key == pygame.K_TAB:
                    self.state = STATE_INVENTORY
                elif event.key == pygame.K_1:
                    self.current_weapon = WEAPONS["pulse_pistol"]
                    self.hud.show_echo("Pulse Pistol selected.", 1.5)
                elif event.key == pygame.K_2:
                    self.current_weapon = WEAPONS["arc_rifle"]
                    self.hud.show_echo("Arc Rifle selected.", 1.5)

        elif self.state == STATE_PAUSED:
            action = self.pause_menu.handle_event(event)
            if action == "RESUME":
                self.state = STATE_PLAYING
            elif action == "SAVE GAME":
                if save_game(self):
                    self.hud.show_echo("Game saved.", 2.0)
                self.state = STATE_PLAYING
            elif action == "MAIN MENU":
                self.state = STATE_MENU

        elif self.state == STATE_INVENTORY:
            action, msg = self.inventory_ui.handle_event(event, self.inventory, self.player)
            if action == "close":
                self.state = STATE_PLAYING
            elif action in ("use", "drop") and msg:
                self.hud.show_echo(msg, 2.0)
                if action == "use":
                    self.behavior.on_item_used()

        elif self.state == STATE_DIALOGUE:
            result = self.dialogue_ui.handle_event(event)
            if result:
                if result["type"] == "choice":
                    self._last_choice_id = result["id"]
                    self.echo_ai.process_choice(result["id"])
                    # check for terminal follow-up
                    if self._pending_dialogue:
                        follow = self.story.get_terminal_follow_up(
                            self._pending_dialogue, result["id"])
                        if follow:
                            self._pending_dialogue = None
                            self.dialogue_ui.start("ECHO", follow)
                            return
                    self._pending_dialogue = None
                    # check if this was the final terminal in final chapter
                    if (self.story.is_final_chapter() and
                            self.story.terminal_index >= 3):
                        self._trigger_ending()
                        return
                self.state = STATE_PLAYING

        elif self.state == STATE_RECORDING:
            if self.recording_ui.handle_event(event):
                self.state = STATE_PLAYING

        elif self.state == STATE_INTRO:
            if self.chapter_intro_ui.handle_event(event):
                self.state = STATE_PLAYING

        elif self.state == STATE_ENDING:
            result = self.ending_ui.handle_event(event)
            if result == "main_menu":
                self.state = STATE_MENU

    # ══════════════════════════════════════════════════════
    #  UPDATE
    # ══════════════════════════════════════════════════════
    def _update(self, dt):
        if self.state == STATE_MENU:
            self.main_menu.update(dt)
        elif self.state == STATE_DIALOGUE:
            self.dialogue_ui.update(dt)
        elif self.state == STATE_INTRO:
            self.chapter_intro_ui.update(dt)
        elif self.state == STATE_ENDING:
            self.ending_ui.update(dt)
        elif self.state == STATE_PLAYING:
            self._update_gameplay(dt)

    def _update_gameplay(self, dt):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        self.player.update(dt, keys, mouse, self.camera, self.world.wall_rects)
        self.camera.update(self.player.pos, dt)
        self.hud.update(dt)
        self.fire_timer = max(0, self.fire_timer - dt)
        self._damage_flash = max(0, self._damage_flash - dt * 3)
        self.behavior.update(dt, self.player.health, self.player.max_health)
        self.echo_ai.update(dt)

        # shooting
        self.player_shooting = False
        if mouse_buttons[0] and self.fire_timer <= 0:
            self._player_shoot()

        # interaction prompt
        nearby = self.world.get_nearby_interactable(self.player.pos, radius=60)
        if nearby:
            t = nearby["type"]
            if t == "door" and not nearby["open"]:
                self.hud.interaction_prompt = "[E] Open Door"
            elif t == "terminal" and not nearby.get("used"):
                self.hud.interaction_prompt = "[E] Access Terminal"
            elif t == "medical":
                self.hud.interaction_prompt = "[E] Examine"
            elif t == "recording" and not nearby.get("used"):
                self.hud.interaction_prompt = "[E] Play Recording"
            elif t == "exit":
                self.hud.interaction_prompt = "[E] Proceed"
            else:
                self.hud.interaction_prompt = None
        else:
            self.hud.interaction_prompt = None

        # exit zone check (auto-trigger)
        if self.world.check_exit_zone((self.player.pos.x, self.player.pos.y)):
            if not self.story.is_final_chapter():
                self._advance_chapter()
            # final chapter exit handled via terminal dialogue

        # open doors
        open_doors = set()
        for obj in self.world.interactables:
            if obj["type"] == "door" and obj.get("open"):
                open_doors.add((obj["row"], obj["col"]))

        # enemy AI
        ctx = {
            "player_pos": (self.player.pos.x, self.player.pos.y),
            "tile_map": self.world.tile_map,
            "wall_rects": self.world.wall_rects,
            "open_doors": open_doors,
            "player_sprinting": self.player.sprinting,
            "player_shooting": self.player_shooting,
            "enemy_shots": [],
        }
        for enemy in self.enemies:
            prev = enemy.fsm.current_name if enemy.fsm else ""
            enemy.update(dt, ctx)
            new = enemy.fsm.current_name if enemy.fsm else ""
            if prev in ("chase", "attack") and new in ("search", "patrol"):
                self.behavior.on_enemy_avoided()
                comment = self.echo_ai.on_enemy_avoided(self.behavior)
                if comment:
                    self.hud.show_echo(comment, 3.0)

        # enemy projectiles
        for shot in ctx["enemy_shots"]:
            self.projectiles.append(Projectile(
                shot["pos"][0], shot["pos"][1], shot["angle"],
                shot["speed"], shot["damage"], shot["color"],
                owner="enemy", size=4))
            self.particles.emit_muzzle_flash(
                shot["pos"][0], shot["pos"][1], shot["angle"], shot["color"])

        # update projectiles
        for proj in self.projectiles:
            proj.update(dt, self.world.wall_rects)
            if not proj.alive:
                self.particles.emit_sparks(proj.pos.x, proj.pos.y, proj.color, 5)

        # collision: player bullets → enemies
        for proj in self.projectiles:
            if not proj.alive or proj.owner != "player":
                continue
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                dist = math.hypot(proj.pos.x - enemy.pos.x, proj.pos.y - enemy.pos.y)
                if dist < enemy.radius + proj.size:
                    enemy.take_damage(proj.damage)
                    self.behavior.on_damage_dealt(proj.damage)
                    proj.alive = False
                    self.particles.emit_sparks(proj.pos.x, proj.pos.y, enemy.color, 10)
                    self.camera.shake(3)
                    if not enemy.alive:
                        self._on_enemy_killed(enemy)
                    break

        # collision: enemy bullets → player
        for proj in self.projectiles:
            if not proj.alive or proj.owner != "enemy":
                continue
            dist = math.hypot(proj.pos.x - self.player.pos.x,
                              proj.pos.y - self.player.pos.y)
            if dist < self.player.radius + proj.size:
                self.player.take_damage(proj.damage)
                proj.alive = False
                self._damage_flash = 1.0
                self.camera.shake(6)
                self.particles.emit_sparks(proj.pos.x, proj.pos.y, RED, 8)

        self.projectiles = [p for p in self.projectiles if p.alive]
        self.enemies = [e for e in self.enemies if e.alive]
        self.particles.update(dt)

        # HUD sync
        self.hud.weapon_name = self.current_weapon["name"]
        self.hud.behavior_profile = self.behavior.get_profile()
        self.hud.echo_trust = self.echo_ai.get_trust_label()

        # ECHO periodic comments
        self._echo_comment_timer -= dt
        if self._echo_comment_timer <= 0:
            self._echo_comment_timer = random.uniform(25, 50)
            comment = self.echo_ai.get_periodic_comment(self.behavior)
            if comment:
                self.hud.show_echo(comment, 4.0)

        # low health warning
        if self.player.health < 25 and not self._low_health_warned:
            self._low_health_warned = True
            w = self.echo_ai.on_low_health()
            if w:
                self.hud.show_echo(w, 3.0)
        elif self.player.health > 50:
            self._low_health_warned = False

        # autosave
        self._autosave_timer -= dt
        if self._autosave_timer <= 0:
            self._autosave_timer = 120.0
            autosave(self)

        # ECHO intro
        if not self._echo_intro_done:
            self._echo_intro_timer += dt
            if self._echo_msg_index < len(self._echo_messages):
                t_time, msg = self._echo_messages[self._echo_msg_index]
                if self._echo_intro_timer >= t_time:
                    self.hud.show_echo(msg, duration=3.0)
                    self._echo_msg_index += 1
            else:
                self._echo_intro_done = True

        if not self.player.alive:
            self.hud.show_echo("Critical failure. Systems shutting down.", 5.0)

    # ══════════════════════════════════════════════════════
    #  DRAW
    # ══════════════════════════════════════════════════════
    def _draw(self):
        if self.state == STATE_MENU:
            self.main_menu.draw()
        elif self.state == STATE_INTRO:
            self.chapter_intro_ui.draw(self.screen)
        elif self.state == STATE_ENDING:
            self.ending_ui.draw(self.screen)
        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_INVENTORY,
                            STATE_DIALOGUE, STATE_RECORDING):
            self.screen.fill(DARK_BG)
            self.world.draw(self.screen, self.camera)
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera)
            for proj in self.projectiles:
                proj.draw(self.screen, self.camera)
            self.particles.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)
            self._draw_vignette()
            if self._damage_flash > 0:
                flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash.fill((200, 30, 30, int(80 * self._damage_flash)))
                self.screen.blit(flash, (0, 0))
            self.hud.draw(self.screen, self.player)

            if self.state == STATE_PAUSED:
                self.pause_menu.draw(self.screen)
            elif self.state == STATE_INVENTORY:
                self.inventory_ui.draw(self.screen, self.inventory, self.player)
            elif self.state == STATE_DIALOGUE:
                self.dialogue_ui.draw(self.screen)
            elif self.state == STATE_RECORDING:
                self.recording_ui.draw(self.screen)

    def _draw_vignette(self):
        self.darkness.fill((0, 0, 0, 0))
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        for i in range(100):
            a = int(40 * (1 - i / 100))
            pygame.draw.rect(self.darkness, (0, 0, 0, a), (i, i, w-2*i, h-2*i), 1)
        self.screen.blit(self.darkness, (0, 0))

    # ══════════════════════════════════════════════════════
    #  COMBAT
    # ══════════════════════════════════════════════════════
    def _player_shoot(self):
        weapon = self.current_weapon
        if self.player.ammo <= 0:
            return
        self.player.ammo -= 1
        self.fire_timer = weapon["fire_rate"]
        self.player_shooting = True
        self.behavior.on_shot_fired()
        spread = math.radians(random.uniform(-weapon["spread"], weapon["spread"]))
        angle = self.player.angle + spread
        mx = self.player.pos.x + math.cos(self.player.angle) * 24
        my = self.player.pos.y + math.sin(self.player.angle) * 24
        self.projectiles.append(Projectile(
            mx, my, angle, weapon["speed"], weapon["damage"],
            weapon["color"], owner="player", size=weapon["bullet_size"]))
        self.particles.emit_muzzle_flash(mx, my, self.player.angle, weapon["color"])
        self.camera.shake(2)

    def _use_emp(self):
        if self.player.energy < 30:
            self.hud.show_echo("Insufficient energy for EMP.", 2.0)
            return
        self.player.energy -= 30
        radius = WEAPONS["emp_device"].get("aoe_radius", 150)
        px, py = self.player.pos.x, self.player.pos.y
        self.particles.emit_emp(px, py, radius)
        self.camera.shake(8)
        stunned = 0
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            if math.hypot(enemy.pos.x - px, enemy.pos.y - py) <= radius:
                enemy.apply_stun(3.0)
                enemy.take_damage(WEAPONS["emp_device"]["damage"])
                self.particles.emit_sparks(enemy.pos.x, enemy.pos.y, YELLOW, 12)
                stunned += 1
        msg = f"EMP discharged. {stunned} target(s) disabled." if stunned else "EMP discharged. No targets in range."
        self.hud.show_echo(msg, 2.5)

    def _on_enemy_killed(self, enemy):
        self.particles.emit_death(enemy.pos.x, enemy.pos.y, enemy.color)
        self.behavior.on_kill()
        comment = self.echo_ai.on_kill(self.behavior)
        self.hud.show_echo(comment or "Hostile neutralized.", 2.0)
        # loot drops
        drops = {
            "watcher":  [("ammo_pack", 0.5)],
            "sentinel": [("ammo_pack", 0.6), ("medkit", 0.3), ("energy_cell", 0.2)],
            "hunter":   [("medkit", 0.5), ("energy_cell", 0.4), ("emp_charge", 0.2)],
        }
        for item_id, chance in drops.get(enemy.enemy_type, []):
            if random.random() < chance:
                if self.inventory.add_item(item_id):
                    from systems.inventory import ITEM_DB
                    self.hud.show_echo(f"Acquired: {ITEM_DB[item_id]['name']}", 2.0)

    # ══════════════════════════════════════════════════════
    #  INTERACTIONS
    # ══════════════════════════════════════════════════════
    def _interact(self):
        nearby = self.world.get_nearby_interactable(self.player.pos, radius=60)
        if not nearby:
            return
        t = nearby["type"]

        if t == "door" and not nearby["open"]:
            self.world.open_door(nearby)
            self.behavior.on_door_opened()
            self.hud.show_echo("Door unlocked.", 2.0)

        elif t == "terminal" and not nearby.get("used"):
            nearby["used"] = True
            self.behavior.on_terminal_accessed()
            self.camera.shake(5)
            self.player.ammo = min(self.player.max_ammo, self.player.ammo + 8)
            # story dialogue
            dlg = self.story.get_terminal_dialogue()
            if dlg:
                self._pending_dialogue = dlg
                self.dialogue_ui.start(dlg["speaker"], dlg["text"],
                                       dlg.get("choices"))
                self.state = STATE_DIALOGUE
            else:
                resp = self.echo_ai.on_terminal_access(self.behavior)
                self.hud.show_echo(resp, 3.0)

        elif t == "medical":
            if self.player.health < self.player.max_health:
                self.player.heal(30)
                self.behavior.on_item_used()
                self.hud.show_echo("Medical supplies found. +30 HP.", 2.5)
            else:
                self.hud.show_echo("Medical bay. No treatment required.", 2.0)

        elif t == "recording" and not nearby.get("used"):
            nearby["used"] = True
            self.behavior.on_evidence_found()
            rec = self.story.get_next_recording()
            if rec:
                self.recording_ui.start(rec)
                self.state = STATE_RECORDING
                # ECHO reacts
                resp = self.echo_ai.on_evidence_found(self.behavior)
                self.hud.show_echo(resp, 3.0)
            else:
                self.hud.show_echo("Corrupted data. Unreadable.", 2.0)

        elif t == "exit":
            if not self.story.is_final_chapter():
                self._advance_chapter()
            else:
                self.hud.show_echo("The exit controls are locked. Find a terminal.", 3.0)

    # ══════════════════════════════════════════════════════
    #  CHAPTER PROGRESSION
    # ══════════════════════════════════════════════════════
    def _advance_chapter(self):
        if not self.story.advance_chapter():
            return
        ch = self.story.current_chapter
        # save before transition
        autosave(self)
        # build new world
        self.world = World(chapter=ch)
        sx, sy = self.world.get_spawn_pos()
        self.player.pos.x = sx
        self.player.pos.y = sy
        self.camera.offset.x = sx - SCREEN_WIDTH / 2
        self.camera.offset.y = sy - SCREEN_HEIGHT / 2
        self.projectiles.clear()
        self.particles.particles.clear()
        self._spawn_enemies()
        # chapter intro
        intro = self.story.get_chapter_intro()
        if intro:
            self.chapter_intro_ui.start(intro)
            self.state = STATE_INTRO
        objectives = {
            1: "Explore the Research Wing. Find Dr. Voss's recordings.",
        }
        self.hud.objective = objectives.get(ch, "Explore.")

    def _trigger_ending(self):
        ending_id = self.story.determine_ending(
            self.echo_ai.trust, self._last_choice_id)
        ending = self.story.get_ending(ending_id)
        if ending:
            self.ending_ui.start(ending, self.behavior.to_dict(),
                                 self.echo_ai.trust)
            self.state = STATE_ENDING

    # ══════════════════════════════════════════════════════
    #  START / SPAWN
    # ══════════════════════════════════════════════════════
    def _start_new_game(self):
        self.story = StoryManager()
        self.world = World(chapter=0)
        sx, sy = self.world.get_spawn_pos()
        self.player = Player(sx, sy)
        self.player.ammo = WEAPONS["pulse_pistol"]["ammo_start"]
        self.player.max_ammo = WEAPONS["pulse_pistol"]["ammo_max"]
        self.current_weapon = WEAPONS["pulse_pistol"]

        self.inventory = Inventory()
        self.behavior = PlayerBehavior()
        self.echo_ai = EchoAI()
        self.story_flags = {}
        self._pending_dialogue = None
        self._last_choice_id = ""

        self.inventory.add_item("medkit", 2)
        self.inventory.add_item("ammo_pack", 1)

        self.camera.offset.x = sx - SCREEN_WIDTH / 2
        self.camera.offset.y = sy - SCREEN_HEIGHT / 2
        self.hud.objective = "Find a way out of Medical Sector A."
        self.projectiles.clear()
        self.particles.particles.clear()
        self._damage_flash = 0
        self._autosave_timer = 120.0
        self._echo_comment_timer = 30.0
        self._low_health_warned = False

        self._spawn_enemies()

        # show chapter 0 intro
        intro = self.story.get_chapter_intro()
        if intro:
            self.chapter_intro_ui.start(intro)
            self.state = STATE_INTRO
        else:
            self.state = STATE_PLAYING

        self._echo_intro_done = False
        self._echo_intro_timer = 0.0
        self._echo_msg_index = 0

    def _spawn_enemies(self):
        TS = TILE_SIZE
        self.enemies = []
        ch = self.story.current_chapter
        data = ENEMIES_CH0 if ch == 0 else ENEMIES_CH1

        for e in data:
            x = e["x"] * TS
            y = e["y"] * TS
            patrol = [(px * TS, py * TS) for px, py in e["patrol"]]
            if e["type"] == "watcher":
                self.enemies.append(Watcher(x, y, patrol_points=patrol))
            elif e["type"] == "sentinel":
                self.enemies.append(Sentinel(x, y, patrol_points=patrol))
            elif e["type"] == "hunter":
                self.enemies.append(Hunter(x, y, patrol_points=patrol))
