"""
World — tile-based level with collision and procedural visuals.
Supports loading different level data per chapter.
"""
import random, math
import pygame
from game.settings import (
    TILE_SIZE, TILE_FLOOR, TILE_WALL, TILE_DOOR, TILE_TERMINAL,
    TILE_MEDICAL, TILE_EXIT, TILE_RECORDING,
    TILE_COLORS, CYAN_DIM, DARK_BG, PURPLE,
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from game.levels import LEVEL_CH0, LEVEL_CH1


class World:
    def __init__(self, chapter=0):
        if chapter == 0:
            self.tile_map = [row[:] for row in LEVEL_CH0]
        else:
            self.tile_map = [row[:] for row in LEVEL_CH1]

        self.chapter = chapter
        self.rows = len(self.tile_map)
        self.cols = len(self.tile_map[0]) if self.rows else 0
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

        self.wall_rects: list[pygame.Rect] = []
        self.interactables: list[dict] = []
        self.exit_zones: list[pygame.Rect] = []
        self._build()

        self._cache = pygame.Surface((self.width, self.height))
        self._cache.fill(DARK_BG)
        self._render_cache()

    def _build(self):
        for r, row in enumerate(self.tile_map):
            for c, tile in enumerate(row):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == TILE_WALL:
                    self.wall_rects.append(rect)
                elif tile == TILE_DOOR:
                    self.wall_rects.append(rect)
                    self.interactables.append({
                        "type": "door", "rect": rect,
                        "row": r, "col": c, "open": False
                    })
                elif tile == TILE_TERMINAL:
                    self.interactables.append({
                        "type": "terminal", "rect": rect,
                        "row": r, "col": c, "used": False
                    })
                elif tile == TILE_MEDICAL:
                    self.interactables.append({
                        "type": "medical", "rect": rect,
                        "row": r, "col": c
                    })
                elif tile == TILE_EXIT:
                    self.exit_zones.append(rect)
                    self.interactables.append({
                        "type": "exit", "rect": rect,
                        "row": r, "col": c
                    })
                elif tile == TILE_RECORDING:
                    self.interactables.append({
                        "type": "recording", "rect": rect,
                        "row": r, "col": c, "used": False
                    })

    def _render_cache(self):
        for r, row in enumerate(self.tile_map):
            for c, tile in enumerate(row):
                x, y = c * TILE_SIZE, r * TILE_SIZE
                color = TILE_COLORS.get(tile, TILE_COLORS[TILE_FLOOR])

                if tile == TILE_WALL:
                    self._draw_wall(x, y, color)
                elif tile == TILE_DOOR:
                    self._draw_door(x, y)
                elif tile == TILE_TERMINAL:
                    self._draw_floor(x, y, color)
                    self._draw_terminal_marker(x, y)
                elif tile == TILE_MEDICAL:
                    self._draw_floor(x, y, color)
                    self._draw_medical_marker(x, y)
                elif tile == TILE_EXIT:
                    self._draw_floor(x, y, color)
                    self._draw_exit_marker(x, y)
                elif tile == TILE_RECORDING:
                    self._draw_floor(x, y, color)
                    self._draw_recording_marker(x, y)
                else:
                    self._draw_floor(x, y, color)

    def _draw_floor(self, x, y, color):
        pygame.draw.rect(self._cache, color, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self._cache, (color[0]+4, color[1]+4, color[2]+6),
                         (x, y, TILE_SIZE, TILE_SIZE), 1)

    def _draw_wall(self, x, y, color):
        pygame.draw.rect(self._cache, color, (x, y, TILE_SIZE, TILE_SIZE))
        lighter = tuple(min(c + 18, 255) for c in color)
        pygame.draw.line(self._cache, lighter, (x, y), (x + TILE_SIZE, y))
        darker = tuple(max(c - 12, 0) for c in color)
        pygame.draw.line(self._cache, darker, (x, y + TILE_SIZE - 1),
                         (x + TILE_SIZE, y + TILE_SIZE - 1))

    def _draw_door(self, x, y):
        pygame.draw.rect(self._cache, (50, 40, 18), (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self._cache, (80, 65, 20),
                         (x + 4, y + TILE_SIZE//2 - 2, TILE_SIZE - 8, 4))

    def _draw_terminal_marker(self, x, y):
        cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
        pygame.draw.circle(self._cache, CYAN_DIM, (cx, cy), 6)

    def _draw_medical_marker(self, x, y):
        cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
        pygame.draw.line(self._cache, (60, 20, 20), (cx - 5, cy), (cx + 5, cy), 2)
        pygame.draw.line(self._cache, (60, 20, 20), (cx, cy - 5), (cx, cy + 5), 2)

    def _draw_exit_marker(self, x, y):
        cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
        pygame.draw.rect(self._cache, (30, 60, 30), (x+2, y+2, TILE_SIZE-4, TILE_SIZE-4))
        pygame.draw.polygon(self._cache, (60, 180, 60),
                            [(cx, cy-8), (cx+8, cy+4), (cx-8, cy+4)])

    def _draw_recording_marker(self, x, y):
        cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
        pygame.draw.circle(self._cache, (80, 50, 120), (cx, cy), 5)

    # ── runtime drawing ──────────────────────────────────
    def draw(self, surface, camera):
        sx, sy = camera.apply((0, 0))
        surface.blit(self._cache, (sx, sy))

        t = pygame.time.get_ticks() / 1000.0
        for obj in self.interactables:
            if obj["type"] == "terminal" and not obj.get("used"):
                pulse = int(40 + 25 * math.sin(t * 3 + obj["col"]))
                cx, cy = obj["rect"].centerx, obj["rect"].centery
                scx, scy = camera.apply((cx, cy))
                glow = pygame.Surface((28, 28), pygame.SRCALPHA)
                pygame.draw.circle(glow, (0, pulse+100, pulse+130, 70), (14, 14), 14)
                surface.blit(glow, (int(scx)-14, int(scy)-14))
            elif obj["type"] == "door" and not obj["open"]:
                sr = camera.apply_rect(obj["rect"])
                pulse = int(30 + 15 * math.sin(t * 2))
                pygame.draw.rect(surface, (pulse+40, pulse+30, 0), sr, 2)
            elif obj["type"] == "exit":
                cx, cy = obj["rect"].centerx, obj["rect"].centery
                scx, scy = camera.apply((cx, cy))
                pulse = int(30 + 25 * math.sin(t * 2.5))
                glow = pygame.Surface((TILE_SIZE+16, TILE_SIZE+16), pygame.SRCALPHA)
                pygame.draw.rect(glow, (pulse+30, pulse+80, pulse+30, 50),
                                 (0, 0, TILE_SIZE+16, TILE_SIZE+16), border_radius=6)
                surface.blit(glow, (int(scx)-TILE_SIZE//2-8, int(scy)-TILE_SIZE//2-8))
            elif obj["type"] == "recording" and not obj.get("used"):
                cx, cy = obj["rect"].centerx, obj["rect"].centery
                scx, scy = camera.apply((cx, cy))
                pulse = int(30 + 20 * math.sin(t * 2 + obj["row"]))
                glow = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(glow, (pulse+80, pulse+40, pulse+100, 60), (12, 12), 12)
                surface.blit(glow, (int(scx)-12, int(scy)-12))

    def get_spawn_pos(self):
        for r, row in enumerate(self.tile_map):
            for c, tile in enumerate(row):
                if tile == TILE_MEDICAL:
                    return (c * TILE_SIZE + TILE_SIZE // 2,
                            r * TILE_SIZE + TILE_SIZE // 2)
        return (TILE_SIZE * 3, TILE_SIZE * 3)

    def open_door(self, door_obj):
        door_obj["open"] = True
        r, c = door_obj["row"], door_obj["col"]
        self.tile_map[r][c] = TILE_FLOOR
        rect = door_obj["rect"]
        if rect in self.wall_rects:
            self.wall_rects.remove(rect)
        x, y = c * TILE_SIZE, r * TILE_SIZE
        self._draw_floor(x, y, TILE_COLORS[TILE_FLOOR])

    def get_nearby_interactable(self, pos, radius=60):
        px, py = pos
        for obj in self.interactables:
            cx = obj["rect"].centerx
            cy = obj["rect"].centery
            dist = math.hypot(px - cx, py - cy)
            if dist < radius:
                return obj
        return None

    def check_exit_zone(self, player_pos):
        px, py = player_pos
        pr = pygame.Rect(px - 10, py - 10, 20, 20)
        for ez in self.exit_zones:
            if pr.colliderect(ez):
                return True
        return False
