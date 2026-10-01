"""
Inventory UI — full-screen overlay with item grid, descriptions, and controls.
"""
import math
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CYAN, CYAN_DIM, WHITE,
    TEXT_COLOR, TEXT_DIM, PANEL_BG, PANEL_BORDER, RED, GREEN, YELLOW
)
from systems.inventory import ITEM_DB


class InventoryUI:
    COLS = 4
    CELL_SIZE = 72
    CELL_GAP = 8

    def __init__(self):
        self.selected = 0
        self.font_title = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_item = pygame.font.SysFont("consolas", 14)
        self.font_desc = pygame.font.SysFont("consolas", 15)
        self.font_hint = pygame.font.SysFont("consolas", 13)
        self.font_icon = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_count = pygame.font.SysFont("consolas", 12, bold=True)
        self.font_cat = pygame.font.SysFont("consolas", 11)

        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))

    def handle_event(self, event, inventory, player):
        """Returns 'close' to exit inventory, or None."""
        items = inventory.get_items_list()
        count = max(len(items), 1)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                return "close", None
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.selected = (self.selected + 1) % count
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                self.selected = (self.selected - 1) % count
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = min(self.selected + self.COLS, count - 1)
            elif event.key in (pygame.K_w, pygame.K_UP):
                self.selected = max(self.selected - self.COLS, 0)
            elif event.key == pygame.K_e:
                # use selected item
                if items and 0 <= self.selected < len(items):
                    item_id, _ = items[self.selected]
                    msg = inventory.use_item(item_id, player)
                    if msg:
                        return "use", msg
            elif event.key == pygame.K_q:
                # drop selected item
                if items and 0 <= self.selected < len(items):
                    item_id, _ = items[self.selected]
                    inventory.remove_item(item_id)
                    self.selected = min(self.selected, len(inventory.get_items_list()) - 1)
                    self.selected = max(self.selected, 0)
                    return "drop", f"Dropped {ITEM_DB[item_id]['name']}."

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos, items)
        if event.type == pygame.MOUSEMOTION:
            self._handle_hover(event.pos, items)

        return None, None

    def draw(self, surface, inventory, player):
        surface.blit(self.overlay, (0, 0))
        t = pygame.time.get_ticks() / 1000.0

        # title
        title = self.font_title.render("INVENTORY", True, CYAN)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        items = inventory.get_items_list()

        # grid area
        grid_w = self.COLS * (self.CELL_SIZE + self.CELL_GAP) - self.CELL_GAP
        grid_x = SCREEN_WIDTH // 2 - grid_w // 2 - 120
        grid_y = 100

        # panel background
        rows_needed = max(1, (len(items) + self.COLS - 1) // self.COLS)
        panel_h = rows_needed * (self.CELL_SIZE + self.CELL_GAP) + 30
        panel_w = grid_w + 40
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 200), (0, 0, panel_w, panel_h),
                         border_radius=8)
        pygame.draw.rect(panel, (*PANEL_BORDER, 150), (0, 0, panel_w, panel_h),
                         1, border_radius=8)
        surface.blit(panel, (grid_x - 20, grid_y - 15))

        self._cell_rects = []

        for i, (item_id, count) in enumerate(items):
            col = i % self.COLS
            row = i // self.COLS
            cx = grid_x + col * (self.CELL_SIZE + self.CELL_GAP)
            cy = grid_y + row * (self.CELL_SIZE + self.CELL_GAP)
            self._draw_cell(surface, cx, cy, item_id, count, i == self.selected, t)
            self._cell_rects.append(pygame.Rect(cx, cy, self.CELL_SIZE, self.CELL_SIZE))

        # empty slots
        total_shown = len(items)
        for i in range(total_shown, inventory.max_slots):
            col = i % self.COLS
            row = i // self.COLS
            cx = grid_x + col * (self.CELL_SIZE + self.CELL_GAP)
            cy = grid_y + row * (self.CELL_SIZE + self.CELL_GAP)
            if cy < grid_y + panel_h - 20:
                pygame.draw.rect(surface, (20, 25, 35),
                                 (cx, cy, self.CELL_SIZE, self.CELL_SIZE), border_radius=4)
                pygame.draw.rect(surface, (30, 38, 55),
                                 (cx, cy, self.CELL_SIZE, self.CELL_SIZE), 1, border_radius=4)

        # detail panel (right side)
        self._draw_detail(surface, items, grid_x + grid_w + 60, grid_y)

        # player stats sidebar
        self._draw_stats(surface, player, grid_x - 20, grid_y + panel_h + 20)

        # controls hint
        hint = self.font_hint.render(
            "WASD Navigate  ·  E Use  ·  Q Drop  ·  TAB Close", True, TEXT_DIM)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                            SCREEN_HEIGHT - 40))

    def _draw_cell(self, surface, x, y, item_id, count, selected, t):
        info = ITEM_DB.get(item_id, {})
        w = self.CELL_SIZE

        # background
        if selected:
            pulse = int(25 + 12 * math.sin(t * 4))
            bg_color = (0, pulse + 30, pulse + 50)
            border_color = CYAN
        else:
            bg_color = (18, 22, 34)
            border_color = PANEL_BORDER

        pygame.draw.rect(surface, bg_color, (x, y, w, w), border_radius=6)
        pygame.draw.rect(surface, border_color, (x, y, w, w), 2 if selected else 1,
                         border_radius=6)

        # category color strip
        cat = info.get("category", "")
        cat_colors = {"consumable": GREEN, "key": YELLOW, "evidence": (160, 100, 220),
                      "component": (220, 160, 40)}
        strip_color = cat_colors.get(cat, TEXT_DIM)
        pygame.draw.rect(surface, strip_color, (x + 2, y + 2, w - 4, 3), border_radius=1)

        # icon
        icon_color = info.get("icon_color", (100, 100, 100))
        symbol = info.get("icon_symbol", "?")
        icon = self.font_icon.render(symbol, True, icon_color)
        surface.blit(icon, (x + w // 2 - icon.get_width() // 2,
                            y + w // 2 - icon.get_height() // 2 - 2))

        # count badge
        if count > 1:
            cnt = self.font_count.render(f"x{count}", True, WHITE)
            surface.blit(cnt, (x + w - cnt.get_width() - 4, y + w - 16))

        # name below icon
        name = self.font_item.render(info.get("name", item_id)[:10], True,
                                     WHITE if selected else TEXT_DIM)
        surface.blit(name, (x + w // 2 - name.get_width() // 2, y + w - 16))

    def _draw_detail(self, surface, items, x, y):
        """Right-side detail panel for selected item."""
        panel_w, panel_h = 280, 200
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 200), (0, 0, panel_w, panel_h),
                         border_radius=8)
        pygame.draw.rect(panel, (*PANEL_BORDER, 150), (0, 0, panel_w, panel_h),
                         1, border_radius=8)
        surface.blit(panel, (x, y))

        if not items or self.selected >= len(items):
            empty = self.font_desc.render("No item selected.", True, TEXT_DIM)
            surface.blit(empty, (x + 16, y + 30))
            return

        item_id, count = items[self.selected]
        info = ITEM_DB.get(item_id, {})

        # name
        name = self.font_title.render(info.get("name", item_id), True, WHITE)
        surface.blit(name, (x + 16, y + 12))

        # category
        cat_text = info.get("category", "").upper()
        cat = self.font_cat.render(cat_text, True, CYAN_DIM)
        surface.blit(cat, (x + 16, y + 48))

        # quantity
        qty = self.font_desc.render(f"Quantity: {count}", True, TEXT_COLOR)
        surface.blit(qty, (x + 16, y + 70))

        # description (word wrap)
        desc = info.get("desc", "")
        self._draw_wrapped(surface, desc, x + 16, y + 95, panel_w - 32, self.font_desc,
                           TEXT_COLOR)

        # usage hint
        if info.get("usable"):
            hint = self.font_hint.render("Press E to use", True, GREEN)
            surface.blit(hint, (x + 16, y + panel_h - 28))

    def _draw_stats(self, surface, player, x, y):
        """Quick player stats below inventory."""
        stats = [
            (f"HP: {int(player.health)}/{player.max_health}", RED),
            (f"Energy: {int(player.energy)}/{player.max_energy}", CYAN),
            (f"Ammo: {player.ammo}/{player.max_ammo}", YELLOW),
        ]
        for i, (text, color) in enumerate(stats):
            s = self.font_desc.render(text, True, color)
            surface.blit(s, (x, y + i * 20))

    def _draw_wrapped(self, surface, text, x, y, max_w, font, color):
        words = text.split()
        line = ""
        cy = y
        for word in words:
            test = line + word + " "
            if font.size(test)[0] > max_w:
                if line:
                    s = font.render(line.strip(), True, color)
                    surface.blit(s, (x, cy))
                    cy += font.get_linesize()
                line = word + " "
            else:
                line = test
        if line.strip():
            s = font.render(line.strip(), True, color)
            surface.blit(s, (x, cy))

    def _handle_click(self, pos, items):
        if not hasattr(self, '_cell_rects'):
            return
        for i, rect in enumerate(self._cell_rects):
            if rect.collidepoint(pos):
                self.selected = i
                return

    def _handle_hover(self, pos, items):
        if not hasattr(self, '_cell_rects'):
            return
        for i, rect in enumerate(self._cell_rects):
            if rect.collidepoint(pos):
                self.selected = i
                return
