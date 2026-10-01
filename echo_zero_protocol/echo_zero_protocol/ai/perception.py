"""
Perception — line-of-sight checks and hearing for enemy AI.
"""
import math
from game.settings import TILE_SIZE, TILE_WALL, TILE_DOOR


def has_line_of_sight(tile_map, from_pos, to_pos, open_doors: set | None = None):
    """
    Raycast from from_pos to to_pos.  Returns True if no wall blocks the line.
    Uses simple DDA (Digital Differential Analyzer).
    """
    x0, y0 = from_pos
    x1, y1 = to_pos
    dx = x1 - x0
    dy = y1 - y0
    dist = math.hypot(dx, dy)
    if dist < 1:
        return True

    steps = int(dist / (TILE_SIZE * 0.4)) + 1
    for i in range(1, steps):
        t = i / steps
        px = x0 + dx * t
        py = y0 + dy * t
        c = int(px // TILE_SIZE)
        r = int(py // TILE_SIZE)
        if r < 0 or r >= len(tile_map) or c < 0 or c >= len(tile_map[0]):
            return False
        tile = tile_map[r][c]
        if tile == TILE_WALL:
            return False
        if tile == TILE_DOOR:
            if not (open_doors and (r, c) in open_doors):
                return False
    return True


def in_field_of_view(enemy_pos, enemy_angle, target_pos, half_angle_deg, sight_range):
    """
    Check if target_pos is within the enemy's field of view cone.
    Returns (in_fov: bool, distance: float).
    """
    dx = target_pos[0] - enemy_pos[0]
    dy = target_pos[1] - enemy_pos[1]
    dist = math.hypot(dx, dy)

    if dist > sight_range:
        return False, dist

    angle_to_target = math.atan2(dy, dx)
    diff = abs(_angle_diff(enemy_angle, angle_to_target))

    return diff <= math.radians(half_angle_deg), dist


def can_hear(enemy_pos, player_pos, hear_range, player_sprinting=False,
             player_shooting=False):
    """
    Check if the enemy can hear the player.
    Sprinting and shooting increase effective noise radius.
    """
    dist = math.hypot(player_pos[0] - enemy_pos[0],
                      player_pos[1] - enemy_pos[1])
    effective_range = hear_range
    if player_sprinting:
        effective_range *= 1.5
    if player_shooting:
        effective_range *= 2.0
    return dist <= effective_range


def _angle_diff(a, b):
    """Signed shortest difference between two angles in radians."""
    d = b - a
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    return d
