"""
Projectiles (bullets) and particle effects (sparks, muzzle flash, explosions).
"""
import math, random
import pygame
from game.settings import MAX_PARTICLES, TILE_SIZE, TILE_WALL, TILE_DOOR


# ── Projectile ───────────────────────────────────────────
class Projectile:
    def __init__(self, x, y, angle, speed, damage, color, owner="player",
                 size=4, lifetime=2.0):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(math.cos(angle) * speed,
                                       math.sin(angle) * speed)
        self.damage = damage
        self.color = color
        self.owner = owner  # "player" or "enemy"
        self.size = size
        self.alive = True
        self.lifetime = lifetime

    def update(self, dt, wall_rects, tile_map=None):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return

        self.pos += self.vel * dt

        # wall collision
        r = self.size
        rect = pygame.Rect(self.pos.x - r, self.pos.y - r, r*2, r*2)
        for wr in wall_rects:
            if rect.colliderect(wr):
                self.alive = False
                return

    def draw(self, surface, camera):
        sx, sy = camera.apply(self.pos)
        ix, iy = int(sx), int(sy)
        # glow
        glow = pygame.Surface((self.size*6, self.size*6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 40), (self.size*3, self.size*3), self.size*3)
        surface.blit(glow, (ix - self.size*3, iy - self.size*3))
        # core
        pygame.draw.circle(surface, self.color, (ix, iy), self.size)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), max(1, self.size - 2))
        # trail
        tail_x = ix - self.vel.x * 0.02
        tail_y = iy - self.vel.y * 0.02
        pygame.draw.line(surface, (*self.color,), (ix, iy),
                         (int(tail_x), int(tail_y)), max(1, self.size - 1))


# ── Particle ─────────────────────────────────────────────
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "alive")

    def __init__(self, x, y, vx, vy, life, size, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.96
        self.vy *= 0.96
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.apply((self.x, self.y))
        alpha = max(0, int(255 * (self.life / self.max_life)))
        s = max(1, int(self.size * (self.life / self.max_life)))
        if alpha > 10:
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), s)


# ── Particle Manager ─────────────────────────────────────
class ParticleManager:
    def __init__(self):
        self.particles: list[Particle] = []

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        # cap
        if len(self.particles) > MAX_PARTICLES:
            self.particles = self.particles[-MAX_PARTICLES:]

    def draw(self, surface, camera):
        for p in self.particles:
            p.draw(surface, camera)

    def emit_sparks(self, x, y, color, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 200)
            life = random.uniform(0.2, 0.6)
            size = random.uniform(1, 3)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life, size, color
            ))

    def emit_muzzle_flash(self, x, y, angle, color):
        for _ in range(5):
            spread = random.uniform(-0.3, 0.3)
            speed = random.uniform(100, 250)
            a = angle + spread
            life = random.uniform(0.1, 0.25)
            self.particles.append(Particle(
                x, y,
                math.cos(a) * speed, math.sin(a) * speed,
                life, random.uniform(2, 4), color
            ))
        # bright core
        self.particles.append(Particle(
            x, y, 0, 0, 0.08, 8, (255, 255, 255)
        ))

    def emit_explosion(self, x, y, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(40, 180)
            life = random.uniform(0.3, 0.8)
            size = random.uniform(2, 5)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed, math.sin(angle) * speed,
                life, size, color
            ))

    def emit_death(self, x, y, color):
        """Enemy death burst."""
        self.emit_explosion(x, y, color, count=25)
        self.emit_sparks(x, y, (255, 255, 200), count=10)

    def emit_emp(self, x, y, radius):
        """EMP pulse ring effect."""
        for i in range(30):
            angle = (i / 30) * math.pi * 2
            speed = radius / 0.4  # expand to radius in ~0.4s
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed, math.sin(angle) * speed,
                0.4, 3, (255, 255, 100)
            ))
