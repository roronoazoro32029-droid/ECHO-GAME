"""
A* Pathfinding on the tile grid.
Returns a list of (px, py) world-coordinate waypoints.
"""
import heapq
from game.settings import TILE_SIZE, TILE_WALL, TILE_DOOR


def _is_walkable(tile_map, r, c, open_doors: set | None = None):
    if r < 0 or r >= len(tile_map) or c < 0 or c >= len(tile_map[0]):
        return False
    tile = tile_map[r][c]
    if tile == TILE_WALL:
        return False
    if tile == TILE_DOOR:
        # walkable only if door is open (tracked externally)
        if open_doors and (r, c) in open_doors:
            return True
        return False
    return True


def _heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def find_path(tile_map, start_world, goal_world, open_doors: set | None = None,
              max_iterations: int = 600):
    """
    A* from start_world (px) to goal_world (px).
    Returns list of (px, py) waypoints, or empty list if no path.
    """
    sc = int(start_world[0] // TILE_SIZE)
    sr = int(start_world[1] // TILE_SIZE)
    gc = int(goal_world[0] // TILE_SIZE)
    gr = int(goal_world[1] // TILE_SIZE)

    rows = len(tile_map)
    cols = len(tile_map[0]) if rows else 0

    # clamp
    sr = max(0, min(sr, rows - 1))
    sc = max(0, min(sc, cols - 1))
    gr = max(0, min(gr, rows - 1))
    gc = max(0, min(gc, cols - 1))

    if not _is_walkable(tile_map, sr, sc, open_doors):
        return []
    if not _is_walkable(tile_map, gr, gc, open_doors):
        return []

    start = (sr, sc)
    goal = (gr, gc)
    if start == goal:
        return [_tile_center(gr, gc)]

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    visited = set()
    iterations = 0

    # 8-directional neighbors
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1),
                 (-1, -1), (-1, 1), (1, -1), (1, 1)]

    while open_set and iterations < max_iterations:
        iterations += 1
        _, current = heapq.heappop(open_set)

        if current == goal:
            # reconstruct path
            path = []
            node = current
            while node in came_from:
                path.append(_tile_center(node[0], node[1]))
                node = came_from[node]
            path.reverse()
            return path

        if current in visited:
            continue
        visited.add(current)

        for dr, dc in neighbors:
            nr, nc = current[0] + dr, current[1] + dc
            if not _is_walkable(tile_map, nr, nc, open_doors):
                continue
            # prevent diagonal cutting through walls
            if dr != 0 and dc != 0:
                if not _is_walkable(tile_map, current[0] + dr, current[1], open_doors):
                    continue
                if not _is_walkable(tile_map, current[0], current[1] + dc, open_doors):
                    continue

            cost = 1.414 if (dr != 0 and dc != 0) else 1.0
            tentative = g_score[current] + cost
            neighbor = (nr, nc)
            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f = tentative + _heuristic(neighbor, goal)
                heapq.heappush(open_set, (f, neighbor))

    return []  # no path found


def _tile_center(row, col):
    return (col * TILE_SIZE + TILE_SIZE // 2,
            row * TILE_SIZE + TILE_SIZE // 2)
