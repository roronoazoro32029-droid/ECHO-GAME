"""
Watcher — small surveillance drone.
Patrols a route, scans for the player, alerts nearby enemies.
Low combat ability.
"""
import math, random
import pygame
from entities.enemy import Enemy
from ai.state_machine import StateMachine, State
from ai.perception import has_line_of_sight, in_field_of_view
from game.settings import (
    WATCHER_SPEED, WATCHER_HEALTH, WATCHER_RADIUS,
    WATCHER_SIGHT_RANGE, WATCHER_SIGHT_ANGLE, WATCHER_DAMAGE,
    ENEMY_COLORS, TILE_SIZE
)


# ── FSM States ───────────────────────────────────────────
class PatrolState(State):
    def __init__(self):
        super().__init__("patrol")

    def enter(self, entity):
        entity.patrol_index = getattr(entity, "patrol_index", 0)

    def update(self, entity, dt, ctx):
        # check for player
        if _can_see_player(entity, ctx):
            entity.last_known_player_pos = ctx["player_pos"]
            entity.alert_level = 100
            return "alert"

        # follow patrol route
        if entity.patrol_points:
            target = entity.patrol_points[entity.patrol_index]
            arrived = entity.move_toward(target, dt, ctx["wall_rects"])
            if arrived:
                entity.patrol_index = (entity.patrol_index + 1) % len(entity.patrol_points)
        return None


class ScanState(State):
    def __init__(self):
        super().__init__("scan")
        self.timer = 0

    def enter(self, entity):
        self.timer = 2.0
        self.start_angle = entity.angle

    def update(self, entity, dt, ctx):
        self.timer -= dt
        # slowly rotate to scan
        entity.angle += 1.5 * dt

        if _can_see_player(entity, ctx):
            entity.last_known_player_pos = ctx["player_pos"]
            entity.alert_level = 100
            return "alert"

        if self.timer <= 0:
            return "patrol"
        return None


class AlertState(State):
    def __init__(self):
        super().__init__("alert")
        self.timer = 0

    def enter(self, entity):
        self.timer = 4.0

    def update(self, entity, dt, ctx):
        self.timer -= dt
        player_pos = ctx["player_pos"]

        # keep tracking if visible
        if _can_see_player(entity, ctx):
            entity.last_known_player_pos = player_pos
            entity.face_toward(player_pos)
            self.timer = 4.0
            # flee away from player (watchers are cowardly)
            dx = entity.pos.x - player_pos[0]
            dy = entity.pos.y - player_pos[1]
            dist = math.hypot(dx, dy)
            if dist < 150 and dist > 0:
                flee_x = entity.pos.x + (dx / dist) * 60
                flee_y = entity.pos.y + (dy / dist) * 60
                entity.move_toward((flee_x, flee_y), dt, ctx["wall_rects"])
        else:
            entity.alert_level = max(0, entity.alert_level - 20 * dt)

        if self.timer <= 0 or entity.alert_level <= 0:
            return "scan"
        return None


# ── Helper ───────────────────────────────────────────────
def _can_see_player(entity, ctx):
    in_fov, dist = in_field_of_view(
        entity.pos, entity.angle, ctx["player_pos"],
        WATCHER_SIGHT_ANGLE, WATCHER_SIGHT_RANGE
    )
    if not in_fov:
        return False
    return has_line_of_sight(ctx["tile_map"], entity.pos, ctx["player_pos"],
                            ctx.get("open_doors"))


# ── Watcher class ────────────────────────────────────────
class Watcher(Enemy):
    def __init__(self, x, y, patrol_points=None):
        super().__init__(x, y, WATCHER_RADIUS, WATCHER_HEALTH,
                         WATCHER_SPEED, ENEMY_COLORS["watcher"], "watcher")
        self.patrol_points = patrol_points or []
        self.patrol_index = 0

        # build FSM
        self.fsm = StateMachine()
        self.fsm.add_state(PatrolState())
        self.fsm.add_state(ScanState())
        self.fsm.add_state(AlertState())
        self.fsm.set_state("patrol", self)

    def _build_sprite(self):
        """Override — watcher is a diamond shape."""
        size = self.radius * 2 + 10
        self._sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        r = self.radius
        points = [(c + r, c), (c, c + r), (c - r, c), (c, c - r)]
        dim = tuple(max(v // 3, 0) for v in self.color)
        pygame.draw.polygon(self._sprite, dim, points)
        pygame.draw.polygon(self._sprite, self.color, points, 2)
        # eye
        pygame.draw.circle(self._sprite, self.color, (c + 4, c), 2)
