"""
Story Manager — drives chapter progression, triggers events,
                manages recordings, and determines endings.
"""
from data.story_data import (
    CHAPTER_INTROS, RECORDINGS, TERMINAL_DIALOGUES, ENDINGS
)


class StoryManager:
    def __init__(self):
        self.current_chapter = 0
        self.terminal_index = 0   # which terminal dialogue to show next
        self.recordings_found: list[str] = []
        self.story_flags: dict = {}

        # chapter-specific terminal keys
        self._terminal_keys = {
            0: ["ch0_terminal_1", "ch0_terminal_2", "ch0_terminal_3"],
            1: ["ch1_terminal_1", "ch1_terminal_2", "ch1_terminal_3"],
        }

        # recording positions per chapter (row, col) → recording_id
        # these are mapped by World tile positions of type 7 (recording)
        self._recording_map = {
            0: {
                0: "rec_ch0_1",
                1: "rec_ch0_2",
            },
            1: {
                0: "rec_ch1_1",
                1: "rec_ch1_2",
                2: "rec_ch1_3",
                3: "rec_ch1_4",
            },
        }
        self._recording_counter = {0: 0, 1: 0}

    # ── Terminal interaction ─────────────────────────────
    def get_terminal_dialogue(self):
        """Return the next terminal dialogue dict for current chapter, or None."""
        keys = self._terminal_keys.get(self.current_chapter, [])
        idx = self.terminal_index
        if idx < len(keys):
            self.terminal_index += 1
            key = keys[idx]
            return TERMINAL_DIALOGUES.get(key)
        return None

    def get_terminal_follow_up(self, dialogue, choice_id):
        """Given a terminal dialogue and chosen choice_id, return follow-up text."""
        if not dialogue or "choices" not in dialogue:
            return None
        for choice in dialogue["choices"]:
            if choice["id"] == choice_id:
                return choice.get("follow")
        return None

    # ── Recordings ───────────────────────────────────────
    def get_next_recording(self):
        """Return the next recording for current chapter, or None."""
        ch = self.current_chapter
        counter = self._recording_counter.get(ch, 0)
        recs = self._recording_map.get(ch, {})
        if counter in recs:
            rec_id = recs[counter]
            self._recording_counter[ch] = counter + 1
            if rec_id not in self.recordings_found:
                self.recordings_found.append(rec_id)
            return RECORDINGS.get(rec_id)
        return None

    # ── Chapter progression ──────────────────────────────
    def get_chapter_intro(self):
        return CHAPTER_INTROS.get(self.current_chapter)

    def advance_chapter(self) -> bool:
        """Move to next chapter. Returns True if there is a next chapter."""
        next_ch = self.current_chapter + 1
        if next_ch <= 1:
            self.current_chapter = next_ch
            self.terminal_index = 0
            return True
        return False

    def is_final_chapter(self):
        return self.current_chapter >= 1

    # ── Endings ──────────────────────────────────────────
    def determine_ending(self, echo_trust, last_choice_id=""):
        """
        Determine which ending to trigger based on trust and final choice.
        """
        if last_choice_id == "trust_echo" or echo_trust >= 55:
            return "liberation"
        else:
            return "containment"

    def get_ending(self, ending_id):
        return ENDINGS.get(ending_id)

    # ── Serialization ────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "chapter": self.current_chapter,
            "terminal_index": self.terminal_index,
            "recordings_found": self.recordings_found,
            "story_flags": dict(self.story_flags),
            "recording_counters": dict(self._recording_counter),
        }

    def from_dict(self, data: dict):
        self.current_chapter = data.get("chapter", 0)
        self.terminal_index = data.get("terminal_index", 0)
        self.recordings_found = data.get("recordings_found", [])
        self.story_flags = data.get("story_flags", {})
        self._recording_counter = {
            int(k): v for k, v in data.get("recording_counters", {}).items()
        }
