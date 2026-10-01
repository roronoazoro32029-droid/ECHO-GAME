"""
HUD — in-game overlay: health, stamina, energy, ammo, objective, interaction.
"""
import math
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    CYAN, CYAN_DIM, RED, RED_DIM, GREEN, GREEN_DIM,
    YELLOW, YELLOW_DIM, WHITE, TEXT_COLOR, TEXT_DIM,
    PANEL_BG, PANEL_BORDER
)


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 16)
        self.font_sm = pygame.font.SysFont("consolas", 13)
        self.font_lg = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_prompt = pygame.font.SysFont("consolas", 20, bold=True)

        self.objective = "Find a way out of Medical Sector A."
        self.interaction_prompt = None   # set externally when near something
        self.show_echo_message = False
        self.echo_message = ""
        self.echo_timer = 0.0

        self.weapon_name = "PULSE PISTOL"
        self.behavior_profile = ""
        self.echo_trust = ""

    # ── draw ─────────────────────────────────────────────
    def draw(self, surface, player):
        self._draw_bars(surface, player)
        self._draw_ammo(surface, player)
        self._draw_objective(surface)
        if self.interaction_prompt:
            self._draw_interaction(surface)
        if self.show_echo_message:
            self._draw_echo(surface)
        self._draw_minimap_hint(surface)

    # ── bars (bottom-left) ───────────────────────────────
    def _draw_bars(self, surface, player):
        x, y = 20, SCREEN_HEIGHT - 90
        bar_w, bar_h = 180, 12
        gap = 20

        # panel background
        panel = pygame.Surface((bar_w + 40, 80), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 180), (0, 0, bar_w + 40, 80),
                         border_radius=6)
        pygame.draw.rect(panel, (*PANEL_BORDER, 120), (0, 0, bar_w + 40, 80),
                         1, border_radius=6)
        surface.blit(panel, (x - 10, y - 10))

        self._bar(surface, x, y, bar_w, bar_h,
                  player.health, player.max_health, RED, RED_DIM, "HP")
        self._bar(surface, x, y + gap, bar_w, bar_h,
                  player.energy, player.max_energy, CYAN, CYAN_DIM, "EN")
        self._bar(surface, x, y + gap * 2, bar_w, bar_h,
                  player.stamina, player.max_stamina, GREEN, GREEN_DIM, "ST")

    def _bar(self, surface, x, y, w, h, current, maximum, color, dim_color, label):
        # label
        lbl = self.font_sm.render(label, True, TEXT_DIM)
        surface.blit(lbl, (x, y - 1))
        bx = x + 28

        # background
        pygame.draw.rect(surface, (15, 18, 28), (bx, y, w - 28, h), border_radius=3)

        # fill
        ratio = max(0, current / maximum)
        fill_w = int((w - 28) * ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, dim_color, (bx, y, fill_w, h), border_radius=3)
            # bright top half
            pygame.draw.rect(surface, color, (bx, y, fill_w, h // 2), border_radius=2)

        # border
        pygame.draw.rect(surface, (*PANEL_BORDER,), (bx, y, w - 28, h), 1, border_radius=3)

        # value text
        txt = self.font_sm.render(f"{int(current)}", True, TEXT_COLOR)
        surface.blit(txt, (bx + w - 28 + 4, y - 1))

    # ── ammo (bottom-right) ──────────────────────────────
    def _draw_ammo(self, surface, player):
        x = SCREEN_WIDTH - 180
        y = SCREEN_HEIGHT - 60

        panel = pygame.Surface((160, 50), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 180), (0, 0, 160, 50), border_radius=6)
        pygame.draw.rect(panel, (*PANEL_BORDER, 120), (0, 0, 160, 50), 1, border_radius=6)
        surface.blit(panel, (x - 10, y - 10))

        weapon = self.font_sm.render(self.weapon_name, True, TEXT_DIM)
        surface.blit(weapon, (x, y - 2))

        ammo_text = f"{player.ammo} / {player.max_ammo}"
        ammo = self.font_lg.render(ammo_text, True, CYAN)
        surface.blit(ammo, (x, y + 16))

    # ── objective (top-right) ────────────────────────────
    def _draw_objective(self, surface):
        x = SCREEN_WIDTH - 340
        y = 20

        panel = pygame.Surface((320, 50), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 160), (0, 0, 320, 50), border_radius=6)
        pygame.draw.rect(panel, (*PANEL_BORDER, 100), (0, 0, 320, 50), 1, border_radius=6)
        surface.blit(panel, (x - 10, y - 8))

        label = self.font_sm.render("OBJECTIVE", True, CYAN_DIM)
        surface.blit(label, (x, y))

        obj = self.font.render(self.objective, True, TEXT_COLOR)
        surface.blit(obj, (x, y + 18))

    # ── interaction prompt (center) ──────────────────────
    def _draw_interaction(self, surface):
        t = pygame.time.get_ticks() / 1000.0
        alpha = int(180 + 60 * math.sin(t * 3))

        text = self.font_prompt.render(self.interaction_prompt, True, CYAN)
        tx = SCREEN_WIDTH // 2 - text.get_width() // 2
        ty = SCREEN_HEIGHT // 2 + 60

        bg = pygame.Surface((text.get_width() + 24, text.get_height() + 12), pygame.SRCALPHA)
        pygame.draw.rect(bg, (*PANEL_BG, 200), bg.get_rect(), border_radius=4)
        pygame.draw.rect(bg, (*CYAN_DIM, min(alpha, 180)), bg.get_rect(), 1, border_radius=4)
        surface.blit(bg, (tx - 12, ty - 6))
        surface.blit(text, (tx, ty))

    # ── ECHO message (top-center) ────────────────────────
    def _draw_echo(self, surface):
        t = pygame.time.get_ticks() / 1000.0
        cx = SCREEN_WIDTH // 2
        y = 90

        label = self.font_sm.render("◈ ECHO", True, CYAN)
        msg = self.font.render(self.echo_message, True, TEXT_COLOR)

        total_w = max(label.get_width(), msg.get_width()) + 40
        panel = pygame.Surface((total_w, 52), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 200), (0, 0, total_w, 52), border_radius=6)
        pygame.draw.rect(panel, (*CYAN_DIM, 140), (0, 0, total_w, 52), 1, border_radius=6)
        surface.blit(panel, (cx - total_w // 2, y - 6))

        surface.blit(label, (cx - label.get_width() // 2, y))
        surface.blit(msg, (cx - msg.get_width() // 2, y + 20))

    def _draw_minimap_hint(self, surface):
        hint = self.font_sm.render("[M] Map  [TAB] Inventory  [F] Flashlight  [Q] EMP", True, TEXT_DIM)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                            SCREEN_HEIGHT - 20))

        # behavior + trust (top-left)
        if self.behavior_profile or self.echo_trust:
            y = 20
            if self.behavior_profile:
                prof = self.font_sm.render(f"Profile: {self.behavior_profile.upper()}", True, TEXT_DIM)
                surface.blit(prof, (20, y))
                y += 16
            if self.echo_trust:
                trust = self.font_sm.render(f"ECHO: {self.echo_trust}", True, CYAN_DIM)
                surface.blit(trust, (20, y))

    # ── public helpers ───────────────────────────────────
    def show_echo(self, message, duration=4.0):
        self.echo_message = message
        self.show_echo_message = True
        self.echo_timer = duration

    def update(self, dt):
        if self.show_echo_message:
            self.echo_timer -= dt
            if self.echo_timer <= 0:
                self.show_echo_message = False
