"""
Chapter Intro and Ending screens — cinematic text overlays.
"""
import math
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BG, CYAN, CYAN_DIM,
    WHITE, TEXT_COLOR, TEXT_DIM
)


class ChapterIntroUI:
    """Displays chapter title and intro text with a fade-in effect."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_sub = pygame.font.SysFont("consolas", 20)
        self.font_line = pygame.font.SysFont("consolas", 17)
        self.font_hint = pygame.font.SysFont("consolas", 14)

        self.active = False
        self.data = None
        self.timer = 0.0
        self.phase = 0  # 0=fade_in_title, 1=show_lines, 2=waiting

    def start(self, intro_data: dict):
        self.active = True
        self.data = intro_data
        self.timer = 0.0
        self.phase = 0

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if self.phase < 2:
                self.phase = 2
                self.timer = 0
            else:
                self.active = False
                return True
        return False

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.phase == 0 and self.timer > 2.0:
            self.phase = 1
            self.timer = 0
        elif self.phase == 1 and self.timer > 4.0:
            self.phase = 2
            self.timer = 0

    def draw(self, surface):
        if not self.active or not self.data:
            return

        surface.fill(DARK_BG)
        cx = SCREEN_WIDTH // 2
        t = pygame.time.get_ticks() / 1000.0

        # fade factor
        fade = min(1.0, self.timer / 1.5)

        # title
        title = self.data.get("title", "CHAPTER")
        color = tuple(int(c * fade) for c in CYAN)
        ts = self.font_title.render(title, True, color)
        surface.blit(ts, (cx - ts.get_width() // 2, 200))

        # subtitle
        if self.phase >= 1 or self.phase == 2:
            sub = self.data.get("subtitle", "")
            alpha = min(1.0, self.timer / 1.0) if self.phase == 1 else 1.0
            sc = tuple(int(c * alpha) for c in TEXT_DIM)
            ss = self.font_sub.render(sub, True, sc)
            surface.blit(ss, (cx - ss.get_width() // 2, 250))

        # lines
        if self.phase >= 1:
            lines = self.data.get("lines", [])
            for i, line in enumerate(lines):
                delay = 0.6 * i
                line_alpha = max(0, min(1.0, (self.timer - delay) / 0.8)) if self.phase == 1 else 1.0
                lc = tuple(int(c * line_alpha) for c in TEXT_COLOR)
                ls = self.font_line.render(line, True, lc)
                surface.blit(ls, (cx - ls.get_width() // 2, 310 + i * 28))

        # continue hint
        if self.phase == 2:
            pulse = int(120 + 80 * math.sin(t * 3))
            hint = self.font_hint.render("Press any key to continue...", True,
                                          (pulse, pulse, pulse))
            surface.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 60))


class EndingUI:
    """Displays ending narrative with player stats."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("consolas", 38, bold=True)
        self.font_line = pygame.font.SysFont("consolas", 18)
        self.font_stat = pygame.font.SysFont("consolas", 15)
        self.font_hint = pygame.font.SysFont("consolas", 14)

        self.active = False
        self.ending = None
        self.behavior_data = None
        self.echo_trust = 0
        self.timer = 0.0
        self.done_animating = False

    def start(self, ending: dict, behavior_data: dict, echo_trust: float):
        self.active = True
        self.ending = ending
        self.behavior_data = behavior_data
        self.echo_trust = echo_trust
        self.timer = 0.0
        self.done_animating = False

    def handle_event(self, event):
        if not self.active:
            return None
        if event.type == pygame.KEYDOWN:
            if not self.done_animating:
                self.done_animating = True
                self.timer = 99
            else:
                self.active = False
                return "main_menu"
        return None

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        lines = self.ending.get("lines", []) if self.ending else []
        needed = 1.0 + len(lines) * 0.4 + 2.0
        if self.timer > needed:
            self.done_animating = True

    def draw(self, surface):
        if not self.active or not self.ending:
            return

        surface.fill(DARK_BG)
        cx = SCREEN_WIDTH // 2
        t = pygame.time.get_ticks() / 1000.0

        title_color = self.ending.get("color", CYAN)

        # title
        fade = min(1.0, self.timer / 1.5)
        tc = tuple(int(c * fade) for c in title_color)
        title = self.font_title.render(self.ending["title"], True, tc)
        surface.blit(title, (cx - title.get_width() // 2, 60))

        # narrative lines
        lines = self.ending.get("lines", [])
        for i, line in enumerate(lines):
            delay = 1.0 + 0.4 * i
            alpha = max(0, min(1.0, (self.timer - delay) / 0.6))
            if alpha <= 0:
                continue
            lc = tuple(int(c * alpha) for c in TEXT_COLOR)
            if line == "":
                continue
            ls = self.font_line.render(line, True, lc)
            surface.blit(ls, (cx - ls.get_width() // 2, 130 + i * 26))

        # stats panel (appears after text)
        stats_delay = 1.0 + len(lines) * 0.4 + 0.5
        stats_alpha = max(0, min(1.0, (self.timer - stats_delay) / 1.0))
        if stats_alpha > 0 and self.behavior_data:
            self._draw_stats(surface, cx, 530, stats_alpha)

        # hint
        if self.done_animating:
            pulse = int(120 + 80 * math.sin(t * 3))
            hint = self.font_hint.render("Press any key to return to menu...",
                                          True, (pulse, pulse, pulse))
            surface.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 40))

    def _draw_stats(self, surface, cx, y, alpha):
        """Show player stats summary."""
        bd = self.behavior_data

        label_color = tuple(int(c * alpha) for c in CYAN_DIM)
        val_color = tuple(int(c * alpha) for c in TEXT_COLOR)

        stats_label = self.ending.get("stats_label", "")
        sl = self.font_stat.render(stats_label, True, label_color)
        surface.blit(sl, (cx - sl.get_width() // 2, y))

        stats = [
            f"Play Time: {int(bd.get('play_time', 0) // 60)}m {int(bd.get('play_time', 0) % 60)}s",
            f"Enemies Killed: {bd.get('kills', 0)}",
            f"Terminals Accessed: {bd.get('terminals_accessed', 0)}",
            f"Evidence Found: {bd.get('evidence_found', 0)}",
            f"Items Used: {bd.get('items_used', 0)}",
            f"ECHO Trust: {int(self.echo_trust)}%",
        ]
        for i, stat in enumerate(stats):
            s = self.font_stat.render(stat, True, val_color)
            surface.blit(s, (cx - s.get_width() // 2, y + 24 + i * 20))
