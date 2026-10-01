"""
Recording UI — displays found audio log transcripts with a styled panel.
"""
import math
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CYAN, CYAN_DIM, WHITE,
    TEXT_COLOR, TEXT_DIM, PANEL_BG, PANEL_BORDER, YELLOW, PURPLE
)


class RecordingUI:
    def __init__(self):
        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_speaker = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_text = pygame.font.SysFont("consolas", 16)
        self.font_hint = pygame.font.SysFont("consolas", 13)

        self.active = False
        self.recording = None  # dict with title, speaker, text

    def start(self, recording: dict):
        self.active = True
        self.recording = recording

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.active = False
                return True
        return False

    def draw(self, surface):
        if not self.active or not self.recording:
            return

        t = pygame.time.get_ticks() / 1000.0

        # overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # panel
        pw, ph = 600, 340
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*PANEL_BG, 230), (0, 0, pw, ph), border_radius=10)
        pygame.draw.rect(panel, (160, 100, 220, 200), (0, 0, pw, ph), 2, border_radius=10)
        # top accent
        pygame.draw.line(panel, PURPLE, (15, 0), (pw - 15, 0), 2)
        surface.blit(panel, (px, py))

        # icon + "RECORDING FOUND"
        pulse = int(180 + 70 * math.sin(t * 3))
        label = self.font_hint.render("◆ RECORDING FOUND", True, (160, 100, 220))
        surface.blit(label, (px + 20, py + 14))

        # title
        title = self.font_title.render(self.recording.get("title", "Unknown"), True, WHITE)
        surface.blit(title, (px + 20, py + 38))

        # speaker
        speaker = self.recording.get("speaker", "UNKNOWN")
        sp = self.font_speaker.render(f"— {speaker}", True, CYAN_DIM)
        surface.blit(sp, (px + 20, py + 66))

        # text body (word wrapped)
        text = self.recording.get("text", "")
        self._draw_wrapped(surface, text, px + 20, py + 95, pw - 40,
                           self.font_text, TEXT_COLOR)

        # hint
        hint_pulse = int(140 + 80 * math.sin(t * 2.5))
        hint = self.font_hint.render("[E] Close", True, (hint_pulse, hint_pulse, hint_pulse))
        surface.blit(hint, (px + pw - hint.get_width() - 20, py + ph - 28))

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
