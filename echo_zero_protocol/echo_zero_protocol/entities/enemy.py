"""
Enemy base class — shared FSM, movement, health, drawing.
Subclasses (Watcher, Sentinel, Hunter) define specific states and stats.
"""
import math
import pygame
from game.settings import TILE_SIZE, PATHFIND_INTERVAL, RED, WHITE, TEXT_DIM
from ai.pathfinding import find_path


class Enemy:
    def __init__(self, x, y, radius, health, speed, color, enemy_type="enemy"):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = radius
        self.health = health
        self.max_health = health
        self.speed = speed
        self.color = color
        self.enemy_type = enemy_type
        self.alive = True
        self.angle = 0.0
        self.stunned = False
        self.stun_timer = 0.0

        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

        # pathfinding
        self.path: list[tuple[float, float]] = []
        self.path_index = 0
        self.path_timer = 0.0

        # combat
        self.attack_cooldown = 0.0
        self.last_known_player_pos = None
        self.alert_level = 0.0   # 0-100, rises when player detected

        # FSM set up by subclass
        self.fsm = None

        # sprite cache
        self._sprite = None
        self._build_sprite()

    # ── sprite ───────────────────────────────────────────
    def _build_sprite(self):
        size = self.radius * 2 + 10
        self._sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        # outer ring
        pygame.draw.circle(self._sprite, self.color, (c, c), self.radius, 2)
        # body fill
        dim = tuple(max(v // 3, 0) for v in self.color)
        pygame.draw.circle(self._sprite, dim, (c, c), self.radius - 2)
        # eye dot
        pygame.draw.circle(self._sprite, self.color, (c + self.radius // 2, c), 3)

    # ── update ───────────────────────────────────────────
    def update(self, dt, context: dict):
        if not self.alive:
            return

        # stun
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return

        # cooldowns
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.path_timer -= dt

        # FSM drives behavior
        if self.fsm:
            self.fsm.update(self, dt, context)

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    # ── movement helpers ─────────────────────────────────
    def move_toward(self, target, dt, wall_rects):
        dx = target[0] - self.pos.x
        dy = target[1] - self.pos.y
        dist = math.hypot(dx, dy)
        if dist < 4:
            return True  # arrived
        dx, dy = dx / dist, dy / dist
        self.angle = math.atan2(dy, dx)

        new_x = self.pos.x + dx * self.speed * dt
        new_y = self.pos.y + dy * self.speed * dt
        test = pygame.Rect(new_x - self.radius, new_y - self.radius,
                           self.radius * 2, self.radius * 2)
        blocked = any(test.colliderect(w) for w in wall_rects)
        if not blocked:
            self.pos.x = new_x
            self.pos.y = new_y
        return False

    def follow_path(self, dt, wall_rects):
        """Move along self.path. Returns True when path is done."""
        if not self.path or self.path_index >= len(self.path):
            return True
        target = self.path[self.path_index]
        arrived = self.move_toward(target, dt, wall_rects)
        if arrived:
            self.path_index += 1
        return self.path_index >= len(self.path)

    def request_path(self, tile_map, goal, open_doors=None):
        """Recalculate A* path if cooldown allows."""
        if self.path_timer > 0:
            return
        self.path = find_path(tile_map, (self.pos.x, self.pos.y), goal, open_doors)
        self.path_index = 0
        self.path_timer = PATHFIND_INTERVAL

    def face_toward(self, target):
        dx = target[0] - self.pos.x
        dy = target[1] - self.pos.y
        if abs(dx) > 0.1 or abs(dy) > 0.1:
            self.angle = math.atan2(dy, dx)

    # ── combat ───────────────────────────────────────────
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def apply_stun(self, duration=3.0):
        self.stunned = True
        self.stun_timer = duration

    # ── draw ─────────────────────────────────────────────
    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.apply(self.pos)

        # skip if off screen
        if sx < -60 or sx > surface.get_width() + 60:
            return
        if sy < -60 or sy > surface.get_height() + 60:
            return

        # stun flash
        if self.stunned:
            t = pygame.time.get_ticks()
            if (t // 100) % 2 == 0:
                glow = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 255, 100, 50),
                                   (self.radius*2, self.radius*2), self.radius*2)
                surface.blit(glow, (int(sx) - self.radius*2, int(sy) - self.radius*2))

        # rotated sprite
        angle_deg = -math.degrees(self.angle)
        rotated = pygame.transform.rotate(self._sprite, angle_deg)
        rect = rotated.get_rect(center=(int(sx), int(sy)))
        surface.blit(rotated, rect)

        # FOV indicator (subtle wedge)
        self._draw_fov(surface, sx, sy)

        # health bar (only if damaged)
        if self.health < self.max_health:
            self._draw_health_bar(surface, sx, sy)

        # state label (small debug-friendly)
        if self.fsm:
            self._draw_state_label(surface, sx, sy)

    def _draw_fov(self, surface, sx, sy):
        """Small vision cone indicator."""
        length = 30
        half = math.radians(25)
        for a_off in (-half, half):
            ex = sx + math.cos(self.angle + a_off) * length
            ey = sy + math.sin(self.angle + a_off) * length
            pygame.draw.line(surface, (*self.color[:3],),
                             (int(sx), int(sy)), (int(ex), int(ey)), 1)

    def _draw_health_bar(self, surface, sx, sy):
        bar_w = self.radius * 2 + 8
        bar_h = 4
        bx = int(sx) - bar_w // 2
        by = int(sy) - self.radius - 12
        pygame.draw.rect(surface, (20, 20, 30), (bx, by, bar_w, bar_h))
        ratio = self.health / self.max_health
        fill_w = int(bar_w * ratio)
        color = RED if ratio < 0.4 else self.color
        pygame.draw.rect(surface, color, (bx, by, fill_w, bar_h))

    def _draw_state_label(self, surface, sx, sy):
        font = pygame.font.SysFont("consolas", 10)
        label = font.render(self.fsm.current_name.upper(), True, TEXT_DIM)
        surface.blit(label, (int(sx) - label.get_width() // 2,
                             int(sy) + self.radius + 6))
