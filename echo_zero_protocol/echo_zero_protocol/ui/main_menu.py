"""
Main Menu — animated dark sci-fi menu with particles and glitch effects.
"""
import random, math, time
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG, CYAN, CYAN_DIM,
    WHITE, TEXT_COLOR, TEXT_DIM, PANEL_BG, PANEL_BORDER
)


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color")

    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-15, -4)
        self.life = random.uniform(2, 6)
        self.max_life = self.life
        self.size = random.uniform(1, 3)
        base = random.choice([(0, 180, 220), (0, 120, 160), (60, 80, 120)])
        self.color = base

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0 or self.y < -10:
            self.reset()
            self.y = SCREEN_HEIGHT + 10

    def draw(self, surface):
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        s = max(1, int(self.size * (self.life / self.max_life)))
        if alpha > 10:
            glow = pygame.Surface((s * 4, s * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, alpha // 2), (s * 2, s * 2), s * 2)
            surface.blit(glow, (int(self.x) - s * 2, int(self.y) - s * 2))
            pygame.draw.circle(surface, (*self.color, alpha),
                               (int(self.x), int(self.y)), s)


class MainMenu:
    ITEMS = ["NEW GAME", "CONTINUE", "SETTINGS", "EXIT"]

    def __init__(self, screen):
        self.screen = screen
        self.selected = 0
        self.particles = [Particle() for _ in range(80)]

        # fonts
        self.font_title = pygame.font.SysFont("consolas", 72, bold=True)
        self.font_sub = pygame.font.SysFont("consolas", 22)
        self.font_item = pygame.font.SysFont("consolas", 28)
        self.font_hint = pygame.font.SysFont("consolas", 14)

        # scanline overlay
        self.scanlines = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(self.scanlines, (0, 0, 0, 20), (0, y), (SCREEN_WIDTH, y))

        self.start_time = time.time()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % len(self.ITEMS)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.ITEMS[self.selected]
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._check_click(event.pos)
        if event.type == pygame.MOUSEMOTION:
            self._check_hover(event.pos)
        return None

    def update(self, dt):
        for p in self.particles:
            p.update(dt)

    def draw(self):
        self.screen.fill(DARK_BG)

        # background grid (subtle)
        t = time.time() - self.start_time
        grid_alpha = int(12 + 6 * math.sin(t * 0.5))
        for x in range(0, SCREEN_WIDTH, 60):
            pygame.draw.line(self.screen, (20, 30, 45, ), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 60):
            pygame.draw.line(self.screen, (20, 30, 45, ), (0, y), (SCREEN_WIDTH, y))

        # particles
        for p in self.particles:
            p.draw(self.screen)

        # title
        self._draw_title(t)

        # menu items
        self._draw_items(t)

        # bottom hint
        hint = self.font_hint.render("↑↓ Navigate  ·  ENTER Select  ·  Python + Pygame", True, TEXT_DIM)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))

        # scanlines
        self.screen.blit(self.scanlines, (0, 0))

    # ── internal ─────────────────────────────────────────
    def _draw_title(self, t):
        cx = SCREEN_WIDTH // 2
        # "ECHO"
        glitch_offset = 0
        if random.random() < 0.03:  # rare glitch
            glitch_offset = random.randint(-4, 4)

        title_text = "ECHO"
        title_surf = self.font_title.render(title_text, True, CYAN)
        # glow layer
        glow_surf = self.font_title.render(title_text, True, (0, 80, 100))
        self.screen.blit(glow_surf, (cx - glow_surf.get_width()//2 + 2 + glitch_offset,
                                     120 + 2))
        self.screen.blit(title_surf, (cx - title_surf.get_width()//2 + glitch_offset, 120))

        # subtitle
        sub_text = "Z E R O   P R O T O C O L"
        sub_alpha = int(160 + 60 * math.sin(t * 1.5))
        sub_surf = self.font_sub.render(sub_text, True, (*CYAN_DIM,))
        self.screen.blit(sub_surf, (cx - sub_surf.get_width()//2, 200))

    def _draw_items(self, t):
        cx = SCREEN_WIDTH // 2
        start_y = 310
        spacing = 56

        self._item_rects = []

        for i, item in enumerate(self.ITEMS):
            y = start_y + i * spacing
            is_sel = (i == self.selected)

            # background box
            box_w = 280
            box_h = 44
            bx = cx - box_w // 2
            by = y - box_h // 2

            self._item_rects.append(pygame.Rect(bx, by, box_w, box_h))

            if is_sel:
                # animated highlight
                pulse = int(20 + 10 * math.sin(t * 4))
                pygame.draw.rect(self.screen, (0, pulse + 30, pulse + 50),
                                 (bx, by, box_w, box_h), border_radius=4)
                pygame.draw.rect(self.screen, CYAN,
                                 (bx, by, box_w, box_h), 2, border_radius=4)
                # arrow
                arrow = self.font_item.render("▸ ", True, CYAN)
                text = self.font_item.render(item, True, WHITE)
                total_w = arrow.get_width() + text.get_width()
                self.screen.blit(arrow, (cx - total_w // 2, y - arrow.get_height() // 2))
                self.screen.blit(text, (cx - total_w // 2 + arrow.get_width(),
                                        y - text.get_height() // 2))
            else:
                pygame.draw.rect(self.screen, PANEL_BORDER,
                                 (bx, by, box_w, box_h), 1, border_radius=4)
                text = self.font_item.render(item, True, TEXT_DIM)
                self.screen.blit(text, (cx - text.get_width() // 2,
                                        y - text.get_height() // 2))

    def _check_click(self, pos):
        if not hasattr(self, '_item_rects'):
            return None
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(pos):
                self.selected = i
                return self.ITEMS[i]
        return None

    def _check_hover(self, pos):
        if not hasattr(self, '_item_rects'):
            return
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(pos):
                self.selected = i
                break
