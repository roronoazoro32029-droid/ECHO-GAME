"""
Hunter — advanced AI enemy.
Fast, dangerous, can hear movement, flanks, retreats when hurt.
"""
import math, random
import pygame
from entities.enemy import Enemy
from ai.state_machine import StateMachine, State
from ai.perception import has_line_of_sight, in_field_of_view, can_hear
from game.settings import (
    HUNTER_SPEED, HUNTER_HEALTH, HUNTER_RADIUS,
    HUNTER_SIGHT_RANGE, HUNTER_SIGHT_ANGLE, HUNTER_DAMAGE,
    HUNTER_ATTACK_RANGE, HUNTER_FIRE_RATE, HUNTER_HEAR_RANGE,
    ENEMY_COLORS, TILE_SIZE
)


def _can_see(entity, ctx):
    in_fov, dist = in_field_of_view(
        entity.pos, entity.angle, ctx["player_pos"],
        HUNTER_SIGHT_ANGLE, HUNTER_SIGHT_RANGE
    )
    if not in_fov:
        return False
    return has_line_of_sight(ctx["tile_map"], entity.pos, ctx["player_pos"],
                            ctx.get("open_doors"))


def _pdist(entity, ctx):
    return math.hypot(ctx["player_pos"][0] - entity.pos.x,
                      ctx["player_pos"][1] - entity.pos.y)


# ── States ───────────────────────────────────────────────
class HPatrol(State):
    def __init__(self):
        super().__init__("patrol")

    def enter(self, entity):
        entity.patrol_index = getattr(entity, "patrol_index", 0)

    def update(self, entity, dt, ctx):
        if _can_see(entity, ctx):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "chase"
        if can_hear(entity.pos, ctx["player_pos"], HUNTER_HEAR_RANGE,
                    ctx.get("player_sprinting"), ctx.get("player_shooting")):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "flank"

        if entity.patrol_points:
            target = entity.patrol_points[entity.patrol_index]
            entity.request_path(ctx["tile_map"], target, ctx.get("open_doors"))
            done = entity.follow_path(dt, ctx["wall_rects"])
            if done:
                entity.patrol_index = (entity.patrol_index + 1) % len(entity.patrol_points)
        return None


class HChase(State):
    def __init__(self):
        super().__init__("chase")

    def update(self, entity, dt, ctx):
        if entity.health < entity.max_health * 0.3:
            return "retreat"

        if _can_see(entity, ctx):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            dist = _pdist(entity, ctx)
            if dist <= HUNTER_ATTACK_RANGE:
                return "attack"
            entity.request_path(ctx["tile_map"], ctx["player_pos"], ctx.get("open_doors"))
            entity.follow_path(dt, ctx["wall_rects"])
        else:
            return "flank"
        return None


class HFlank(State):
    """Move to an offset position rather than straight at the player."""
    def __init__(self):
        super().__init__("flank")

    def enter(self, entity):
        self.timer = 5.0
        self.flank_offset = random.choice([-1, 1]) * random.uniform(80, 160)

    def update(self, entity, dt, ctx):
        self.timer -= dt
        if _can_see(entity, ctx):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "chase"

        if entity.last_known_player_pos:
            # compute a flanking position
            px, py = entity.last_known_player_pos
            angle_to = math.atan2(py - entity.pos.y, px - entity.pos.x)
            flank_x = px + math.cos(angle_to + math.pi/2) * self.flank_offset
            flank_y = py + math.sin(angle_to + math.pi/2) * self.flank_offset
            entity.request_path(ctx["tile_map"], (flank_x, flank_y),
                                ctx.get("open_doors"))
            entity.follow_path(dt, ctx["wall_rects"])

        if self.timer <= 0:
            return "search"
        return None


class HAttack(State):
    def __init__(self):
        super().__init__("attack")

    def update(self, entity, dt, ctx):
        if entity.health < entity.max_health * 0.3:
            return "retreat"
        if not _can_see(entity, ctx):
            return "search"
        dist = _pdist(entity, ctx)
        if dist > HUNTER_ATTACK_RANGE * 1.3:
            return "chase"

        entity.face_toward(ctx["player_pos"])

        if entity.attack_cooldown <= 0:
            entity.attack_cooldown = HUNTER_FIRE_RATE
            ctx["enemy_shots"].append({
                "pos": (entity.pos.x, entity.pos.y),
                "angle": entity.angle,
                "damage": HUNTER_DAMAGE,
                "speed": 420,
                "color": entity.color,
                "enemy": entity,
            })

        # dodge side-to-side
        strafe = math.sin(pygame.time.get_ticks() / 300.0) * 80
        sx = entity.pos.x + math.cos(entity.angle + math.pi/2) * strafe * dt
        sy = entity.pos.y + math.sin(entity.angle + math.pi/2) * strafe * dt
        test = pygame.Rect(sx - entity.radius, sy - entity.radius,
                           entity.radius * 2, entity.radius * 2)
        if not any(test.colliderect(w) for w in ctx["wall_rects"]):
            entity.pos.x = sx
            entity.pos.y = sy
        return None


class HSearch(State):
    def __init__(self):
        super().__init__("search")

    def enter(self, entity):
        self.timer = 5.0

    def update(self, entity, dt, ctx):
        self.timer -= dt
        if _can_see(entity, ctx):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "chase"
        if can_hear(entity.pos, ctx["player_pos"], HUNTER_HEAR_RANGE,
                    ctx.get("player_sprinting"), ctx.get("player_shooting")):
            entity.last_known_player_pos = tuple(ctx["player_pos"])
            return "flank"

        if entity.last_known_player_pos:
            entity.request_path(ctx["tile_map"], entity.last_known_player_pos,
                                ctx.get("open_doors"))
            done = entity.follow_path(dt, ctx["wall_rects"])
            if done:
                entity.angle += 2.5 * dt
        if self.timer <= 0:
            return "patrol"
        return None


class HRetreat(State):
    def __init__(self):
        super().__init__("retreat")

    def enter(self, entity):
        self.timer = 3.0

    def update(self, entity, dt, ctx):
        self.timer -= dt
        pp = ctx["player_pos"]
        dx = entity.pos.x - pp[0]
        dy = entity.pos.y - pp[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            flee = (entity.pos.x + (dx/dist) * 120,
                    entity.pos.y + (dy/dist) * 120)
            entity.request_path(ctx["tile_map"], flee, ctx.get("open_doors"))
            entity.follow_path(dt, ctx["wall_rects"])

        if self.timer <= 0:
            if entity.health > entity.max_health * 0.3:
                return "chase"
            return "patrol"
        return None


# ── Hunter class ─────────────────────────────────────────
class Hunter(Enemy):
    def __init__(self, x, y, patrol_points=None):
        super().__init__(x, y, HUNTER_RADIUS, HUNTER_HEALTH,
                         HUNTER_SPEED, ENEMY_COLORS["hunter"], "hunter")
        self.patrol_points = patrol_points or []
        self.patrol_index = 0

        self.fsm = StateMachine()
        self.fsm.add_state(HPatrol())
        self.fsm.add_state(HChase())
        self.fsm.add_state(HFlank())
        self.fsm.add_state(HAttack())
        self.fsm.add_state(HSearch())
        self.fsm.add_state(HRetreat())
        self.fsm.set_state("patrol", self)

    def _build_sprite(self):
        """Hunter — triangular / arrow shape."""
        size = self.radius * 2 + 10
        self._sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        r = self.radius
        points = [(c + r, c), (c - r * 0.7, c + r * 0.8), (c - r * 0.7, c - r * 0.8)]
        dim = tuple(max(v // 3, 0) for v in self.color)
        pygame.draw.polygon(self._sprite, dim, points)
        pygame.draw.polygon(self._sprite, self.color, points, 2)
        pygame.draw.circle(self._sprite, self.color, (c + 3, c), 3)
