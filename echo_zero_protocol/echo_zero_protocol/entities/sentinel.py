"""
Sentinel — standard combat robot.
Full FSM: PATROL → INVESTIGATE → CHASE → ATTACK → SEARCH → RETURN.
"""
import math, random
import pygame
from entities.enemy import Enemy
from ai.state_machine import StateMachine, State
from ai.perception import has_line_of_sight, in_field_of_view, can_hear
from game.settings import (
    SENTINEL_SPEED, SENTINEL_HEALTH, SENTINEL_RADIUS,
    SENTINEL_SIGHT_RANGE, SENTINEL_SIGHT_ANGLE, SENTINEL_DAMAGE,
    SENTINEL_ATTACK_RANGE, SENTINEL_FIRE_RATE,
    ENEMY_COLORS, TILE_SIZE
)


# ── Helpers ──────────────────────────────────────────────
def _can_see_player(entity, ctx):
    in_fov, dist = in_field_of_view(
        entity.pos, entity.angle, ctx["player_pos"],
        SENTINEL_SIGHT_ANGLE, SENTINEL_SIGHT_RANGE
    )
    if not in_fov:
        return False
    return has_line_of_sight(ctx["tile_map"], entity.pos, ctx["player_pos"],
                            ctx.get("open_doors"))


def _player_dist(entity, ctx):
    return math.hypot(ctx["player_pos"][0] - entity.pos.x,
                      ctx["player_pos"][1] - entity.pos.y)


# ── FSM States ───────────────────────────────────────────
class PatrolState(State):
    def __init__(self):
        super().__init__("patrol")

    def enter(self, entity):
        entity.patrol_index = getattr(entity, "patrol_index", 0)

    def update(self, entity, dt, ctx):
        if _can_see_player(entity, ctx):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "chase"

        # hear player?
        if can_hear(entity.pos, ctx["player_pos"], 180,
                    ctx.get("player_sprinting"), ctx.get("player_shooting")):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "investigate"

        # patrol
        if entity.patrol_points:
            target = entity.patrol_points[entity.patrol_index]
            entity.request_path(ctx["tile_map"], target, ctx.get("open_doors"))
            done = entity.follow_path(dt, ctx["wall_rects"])
            if done:
                entity.patrol_index = (entity.patrol_index + 1) % len(entity.patrol_points)
        else:
            entity.angle += 0.5 * dt  # idle rotation
        return None


class InvestigateState(State):
    def __init__(self):
        super().__init__("investigate")

    def enter(self, entity):
        self.timer = 5.0
        if entity.last_known_player_pos:
            entity.request_path(
                None, entity.last_known_player_pos)  # will be called properly in update

    def update(self, entity, dt, ctx):
        self.timer -= dt
        if _can_see_player(entity, ctx):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "chase"

        # move toward last known position
        if entity.last_known_player_pos:
            entity.request_path(ctx["tile_map"], entity.last_known_player_pos,
                                ctx.get("open_doors"))
            done = entity.follow_path(dt, ctx["wall_rects"])
            if done:
                return "search"

        if self.timer <= 0:
            return "patrol"
        return None


class ChaseState(State):
    def __init__(self):
        super().__init__("chase")

    def update(self, entity, dt, ctx):
        player_pos = ctx["player_pos"]

        if _can_see_player(entity, ctx):
            entity.last_known_player_pos = tuple(player_pos)
            dist = _player_dist(entity, ctx)

            if dist <= SENTINEL_ATTACK_RANGE:
                return "attack"

            # chase — path toward player
            entity.request_path(ctx["tile_map"], player_pos, ctx.get("open_doors"))
            entity.follow_path(dt, ctx["wall_rects"])
        else:
            # lost sight
            return "search"
        return None


class AttackState(State):
    def __init__(self):
        super().__init__("attack")

    def update(self, entity, dt, ctx):
        player_pos = ctx["player_pos"]

        if not _can_see_player(entity, ctx):
            return "search"

        dist = _player_dist(entity, ctx)
        if dist > SENTINEL_ATTACK_RANGE * 1.2:
            return "chase"

        entity.face_toward(player_pos)

        # fire
        if entity.attack_cooldown <= 0:
            entity.attack_cooldown = SENTINEL_FIRE_RATE
            # signal to game to create a projectile
            ctx["enemy_shots"].append({
                "pos": (entity.pos.x, entity.pos.y),
                "angle": entity.angle,
                "damage": SENTINEL_DAMAGE,
                "speed": 350,
                "color": entity.color,
                "enemy": entity,
            })

        # slight strafe
        strafe = math.sin(pygame.time.get_ticks() / 500.0) * 40
        sx = entity.pos.x + math.cos(entity.angle + math.pi / 2) * strafe * dt
        sy = entity.pos.y + math.sin(entity.angle + math.pi / 2) * strafe * dt
        test = pygame.Rect(sx - entity.radius, sy - entity.radius,
                           entity.radius * 2, entity.radius * 2)
        if not any(test.colliderect(w) for w in ctx["wall_rects"]):
            entity.pos.x = sx
            entity.pos.y = sy
        return None


class SearchState(State):
    def __init__(self):
        super().__init__("search")

    def enter(self, entity):
        self.timer = 6.0
        self.spin_dir = random.choice([-1, 1])

    def update(self, entity, dt, ctx):
        self.timer -= dt

        if _can_see_player(entity, ctx):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "chase"

        # move to last known position, then spin
        if entity.last_known_player_pos:
            dist = math.hypot(entity.pos.x - entity.last_known_player_pos[0],
                              entity.pos.y - entity.last_known_player_pos[1])
            if dist > 30:
                entity.request_path(ctx["tile_map"], entity.last_known_player_pos,
                                    ctx.get("open_doors"))
                entity.follow_path(dt, ctx["wall_rects"])
            else:
                entity.angle += self.spin_dir * 2.0 * dt

        if self.timer <= 0:
            return "patrol"
        return None


# ── Sentinel class ───────────────────────────────────────
class Sentinel(Enemy):
    def __init__(self, x, y, patrol_points=None):
        super().__init__(x, y, SENTINEL_RADIUS, SENTINEL_HEALTH,
                         SENTINEL_SPEED, ENEMY_COLORS["sentinel"], "sentinel")
        self.patrol_points = patrol_points or []
        self.patrol_index = 0

        # FSM
        self.fsm = StateMachine()
        self.fsm.add_state(PatrolState())
        self.fsm.add_state(InvestigateState())
        self.fsm.add_state(ChaseState())
        self.fsm.add_state(AttackState())
        self.fsm.add_state(SearchState())
        self.fsm.set_state("patrol", self)

    def _build_sprite(self):
        """Sentinel — hexagonal shape."""
        size = self.radius * 2 + 10
        self._sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        r = self.radius
        points = []
        for i in range(6):
            a = math.radians(60 * i - 30)
            points.append((c + r * math.cos(a), c + r * math.sin(a)))
        dim = tuple(max(v // 3, 0) for v in self.color)
        pygame.draw.polygon(self._sprite, dim, points)
        pygame.draw.polygon(self._sprite, self.color, points, 2)
        # eye
        pygame.draw.circle(self._sprite, self.color, (c + 5, c), 3)
