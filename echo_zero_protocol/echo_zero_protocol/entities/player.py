"""
Player — movement, stamina, flashlight, collision.
"""
import math
import pygame
from game.settings import (
    PLAYER_SPEED, PLAYER_SPRINT_MULT, PLAYER_SIZE,
    PLAYER_MAX_HEALTH, PLAYER_MAX_STAMINA, PLAYER_MAX_ENERGY,
    PLAYER_STAMINA_DRAIN, PLAYER_STAMINA_REGEN,
    CYAN, CYAN_DIM, WHITE, TILE_SIZE
)


class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.radius = PLAYER_SIZE
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                                self.radius * 2, self.radius * 2)

        # stats
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.stamina = PLAYER_MAX_STAMINA
        self.max_stamina = PLAYER_MAX_STAMINA
        self.energy = PLAYER_MAX_ENERGY
        self.max_energy = PLAYER_MAX_ENERGY
        self.ammo = 24
        self.max_ammo = 48

        # state
        self.sprinting = False
        self.flashlight_on = False
        self.alive = True
        self.angle = 0.0  # facing angle in radians (toward mouse)

        # procedural sprite
        self._build_sprite()

    # ── sprite ───────────────────────────────────────────
    def _build_sprite(self):
        size = self.radius * 2 + 8
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        # outer ring
        pygame.draw.circle(self.sprite, (30, 50, 70), (c, c), self.radius, 2)
        # body
        pygame.draw.circle(self.sprite, (20, 35, 55), (c, c), self.radius - 2)
        # inner glow
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow, (0, 180, 220, 40), (c, c), self.radius - 4)
        self.sprite.blit(glow, (0, 0))
        # center dot
        pygame.draw.circle(self.sprite, CYAN, (c, c), 3)

    # ── update ───────────────────────────────────────────
    def update(self, dt, keys, mouse_pos, camera, wall_rects):
        # ─ facing angle ─
        screen_pos = camera.apply(self.pos)
        dx = mouse_pos[0] - screen_pos[0]
        dy = mouse_pos[1] - screen_pos[1]
        self.angle = math.atan2(dy, dx)

        # ─ input → velocity ─
        move = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1

        if move.length_squared() > 0:
            move = move.normalize()

        speed = PLAYER_SPEED
        self.sprinting = keys[pygame.K_LSHIFT] and self.stamina > 0 and move.length_squared() > 0
        if self.sprinting:
            speed *= PLAYER_SPRINT_MULT
            self.stamina = max(0, self.stamina - PLAYER_STAMINA_DRAIN * dt)
        else:
            self.stamina = min(self.max_stamina, self.stamina + PLAYER_STAMINA_REGEN * dt)

        self.vel = move * speed

        # ─ move with collision (separate axes) ─
        new_x = self.pos.x + self.vel.x * dt
        test_rect = pygame.Rect(new_x - self.radius, self.pos.y - self.radius,
                                self.radius * 2, self.radius * 2)
        if not self._collides(test_rect, wall_rects):
            self.pos.x = new_x

        new_y = self.pos.y + self.vel.y * dt
        test_rect = pygame.Rect(self.pos.x - self.radius, new_y - self.radius,
                                self.radius * 2, self.radius * 2)
        if not self._collides(test_rect, wall_rects):
            self.pos.y = new_y

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def _collides(self, rect, wall_rects):
        for wr in wall_rects:
            if rect.colliderect(wr):
                return True
        return False

    # ── draw ─────────────────────────────────────────────
    def draw(self, surface, camera):
        sx, sy = camera.apply(self.pos)

        # flashlight cone
        if self.flashlight_on:
            self._draw_flashlight(surface, sx, sy)

        # rotated sprite
        sprite_center = (self.sprite.get_width() // 2, self.sprite.get_height() // 2)
        angle_deg = -math.degrees(self.angle)
        rotated = pygame.transform.rotate(self.sprite, angle_deg)
        rect = rotated.get_rect(center=(int(sx), int(sy)))
        surface.blit(rotated, rect)

        # aim line (subtle)
        end_x = sx + math.cos(self.angle) * 36
        end_y = sy + math.sin(self.angle) * 36
        pygame.draw.line(surface, (*CYAN_DIM, ), (int(sx), int(sy)),
                         (int(end_x), int(end_y)), 1)

    def _draw_flashlight(self, surface, sx, sy):
        """Draw a soft cone of light."""
        from game.settings import FLASHLIGHT_RANGE, FLASHLIGHT_ANGLE
        cone_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        points = [(int(sx), int(sy))]
        num_segments = 20
        half_angle = math.radians(FLASHLIGHT_ANGLE)
        for i in range(num_segments + 1):
            a = self.angle - half_angle + (2 * half_angle) * i / num_segments
            px = sx + math.cos(a) * FLASHLIGHT_RANGE
            py = sy + math.sin(a) * FLASHLIGHT_RANGE
            points.append((int(px), int(py)))
        if len(points) >= 3:
            pygame.draw.polygon(cone_surf, (255, 255, 200, 18), points)
            pygame.draw.polygon(cone_surf, (255, 255, 220, 8), points)
        surface.blit(cone_surf, (0, 0))

    # ── actions ──────────────────────────────────────────
    def toggle_flashlight(self):
        self.flashlight_on = not self.flashlight_on

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.alive = False

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
