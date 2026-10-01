"""
Dialogue UI — bottom panel showing ECHO messages and player choices.
Supports typewriter effect and branching choices.
"""
import math
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CYAN, CYAN_DIM, WHITE,
    TEXT_COLOR, TEXT_DIM, PANEL_BG, PANEL_BORDER
)


class DialogueUI:
    def __init__(self):
        self.font_speaker = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_text = pygame.font.SysFont("consolas", 18)
        self.font_choice = pygame.font.SysFont("consolas", 16)
        self.font_hint = pygame.font.SysFont("consolas", 12)

        self.active = False
        self.speaker = ""
        self.full_text = ""
        self.displayed_text = ""
        self.char_index = 0
        self.char_timer = 0.0
        self.char_speed = 0.03  # seconds per character

        self.choices: list[dict] = []  # [{"text": ..., "id": ...}, ...]
        self.selected_choice = 0
        self.waiting_for_choice = False
        self.finished_typing = False

        self.result = None  # set when player makes a choice or continues

    def start(self, speaker: str, text: str, choices: list[dict] | None = None):
        """Begin a dialogue sequence."""
        self.active = True
        self.speaker = speaker
        self.full_text = text
        self.displayed_text = ""
        self.char_index = 0
        self.char_timer = 0.0
        self.choices = choices or []
        self.selected_choice = 0
        self.waiting_for_choice = False
        self.finished_typing = False
        self.result = None

    def handle_event(self, event):
        """Returns a result dict when dialogue completes, or None."""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if not self.finished_typing:
                # skip typewriter — show all text
                if event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                    self.displayed_text = self.full_text
                    self.finished_typing = True
                    if self.choices:
                        self.waiting_for_choice = True
            elif self.waiting_for_choice:
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.selected_choice = (self.selected_choice - 1) % len(self.choices)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_choice = (self.selected_choice + 1) % len(self.choices)
                elif event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                    choice = self.choices[self.selected_choice]
                    self.result = {"type": "choice", "id": choice.get("id", ""),
                                   "text": choice.get("text", "")}
                    self.active = False
                    return self.result
            else:
                # no choices, just continue
                if event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                    self.result = {"type": "continue"}
                    self.active = False
                    return self.result

        return None

    def update(self, dt):
        if not self.active or self.finished_typing:
            return

        self.char_timer += dt
        while self.char_timer >= self.char_speed and self.char_index < len(self.full_text):
            self.char_timer -= self.char_speed
            self.char_index += 1
            self.displayed_text = self.full_text[:self.char_index]

        if self.char_index >= len(self.full_text):
            self.finished_typing = True
            if self.choices:
                self.waiting_for_choice = True

    def draw(self, surface):
        if not self.active:
            return

        t = pygame.time.get_ticks() / 1000.0
        panel_h = 160 if not self.choices else 160 + len(self.choices) * 28 + 16
        panel_y = SCREEN_HEIGHT - panel_h - 20
        panel_x = 60
        panel_w = SCREEN_WIDTH - 120

        # background
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 220), (0, 0, panel_w, panel_h),
                         border_radius=8)
        pygame.draw.rect(panel, (*CYAN_DIM, 160), (0, 0, panel_w, panel_h),
                         1, border_radius=8)
        # top accent line
        pygame.draw.line(panel, CYAN, (12, 0), (panel_w - 12, 0), 2)
        surface.blit(panel, (panel_x, panel_y))

        # speaker name
        speaker_icon = "◈ " if self.speaker.upper() == "ECHO" else "◇ "
        speaker = self.font_speaker.render(speaker_icon + self.speaker.upper(), True, CYAN)
        surface.blit(speaker, (panel_x + 20, panel_y + 14))

        # dialogue text (word-wrapped)
        self._draw_wrapped(surface, self.displayed_text,
                           panel_x + 20, panel_y + 40, panel_w - 40,
                           self.font_text, TEXT_COLOR)

        # typing cursor
        if not self.finished_typing:
            cursor_alpha = int(200 + 55 * math.sin(t * 8))
            cursor = self.font_text.render("▌", True, CYAN)
            # approximate position
            last_line = self.displayed_text.split('\n')[-1] if self.displayed_text else ""
            cx = panel_x + 20 + self.font_text.size(last_line)[0]
            cy = panel_y + 40
            surface.blit(cursor, (cx, cy))

        # choices
        if self.waiting_for_choice and self.choices:
            choice_y = panel_y + 100
            for i, choice in enumerate(self.choices):
                is_sel = (i == self.selected_choice)
                prefix = "▸ " if is_sel else "  "
                color = WHITE if is_sel else TEXT_DIM
                text = self.font_choice.render(prefix + choice["text"], True, color)
                if is_sel:
                    # highlight bg
                    hx = panel_x + 18
                    hw = text.get_width() + 12
                    hh = text.get_height() + 4
                    hy = choice_y - 2
                    highlight = pygame.Surface((hw, hh), pygame.SRCALPHA)
                    pygame.draw.rect(highlight, (0, 60, 80, 80), (0, 0, hw, hh),
                                     border_radius=3)
                    surface.blit(highlight, (hx, hy))
                surface.blit(text, (panel_x + 24, choice_y))
                choice_y += 28

        # continue hint
        if self.finished_typing and not self.waiting_for_choice:
            pulse = int(120 + 80 * math.sin(t * 3))
            hint = self.font_hint.render("[E] Continue", True, (*CYAN_DIM,))
            surface.blit(hint, (panel_x + panel_w - hint.get_width() - 20,
                                panel_y + panel_h - 22))

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
