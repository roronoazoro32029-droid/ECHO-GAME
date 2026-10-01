"""
Pause Menu — dark overlay with options.
"""
import math
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG, CYAN, CYAN_DIM,
    WHITE, TEXT_COLOR, TEXT_DIM, PANEL_BG, PANEL_BORDER
)


class PauseMenu:
    ITEMS = ["RESUME", "SETTINGS", "SAVE GAME", "MAIN MENU"]

    def __init__(self):
        self.selected = 0
        self.font_title = pygame.font.SysFont("consolas", 42, bold=True)
        self.font_item = pygame.font.SysFont("consolas", 24)

        # dark overlay
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 160))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "RESUME"
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

    def draw(self, surface):
        surface.blit(self.overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        t = pygame.time.get_ticks() / 1000.0

        # title
        title = self.font_title.render("PAUSED", True, CYAN)
        surface.blit(title, (cx - title.get_width() // 2, 180))

        # items
        self._item_rects = []
        start_y = 280
        spacing = 52
        for i, item in enumerate(self.ITEMS):
            y = start_y + i * spacing
            is_sel = (i == self.selected)
            box_w, box_h = 240, 40
            bx = cx - box_w // 2
            by = y - box_h // 2
            self._item_rects.append(pygame.Rect(bx, by, box_w, box_h))

            if is_sel:
                pulse = int(20 + 10 * math.sin(t * 4))
                pygame.draw.rect(surface, (0, pulse + 25, pulse + 40),
                                 (bx, by, box_w, box_h), border_radius=4)
                pygame.draw.rect(surface, CYAN, (bx, by, box_w, box_h), 2,
                                 border_radius=4)
                text = self.font_item.render(f"▸ {item}", True, WHITE)
            else:
                pygame.draw.rect(surface, PANEL_BORDER,
                                 (bx, by, box_w, box_h), 1, border_radius=4)
                text = self.font_item.render(item, True, TEXT_DIM)
            surface.blit(text, (cx - text.get_width() // 2, y - text.get_height() // 2))

    def _check_click(self, pos):
        if not hasattr(self, '_item_rects'):
            return None
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(pos):
                return self.ITEMS[i]
        return None

    def _check_hover(self, pos):
        if not hasattr(self, '_item_rects'):
            return
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(pos):
                self.selected = i
                break
