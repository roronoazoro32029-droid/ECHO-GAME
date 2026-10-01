"""
ECHO AI — adaptive personality system.
ECHO observes player behavior and responds with context-aware dialogue.
Its tone shifts based on the player's aggression, stealth, exploration, etc.
"""
import random


class EchoAI:
    def __init__(self):
        self.trust = 50.0          # 0-100, starts neutral
        self.memories: list[dict] = []  # significant events ECHO remembers
        self._comment_cooldown = 0.0

        # dialogue pools keyed by behavior profile
        self._observations = {
            "aggressive": [
                "You choose violence readily. Efficient, if imprecise.",
                "Another hostile eliminated. You are... thorough.",
                "Your approach is direct. The machines were not designed for mercy either.",
                "You fight like someone with nothing to lose.",
                "I notice you rarely attempt to avoid confrontation.",
            ],
            "stealthy": [
                "You move carefully. That is wise in a facility like this.",
                "Avoiding detection. You have good instincts.",
                "The machines did not see you. Neither did I, for a moment.",
                "Stealth conserves resources. And lives.",
                "You prefer the shadows. I understand that impulse.",
            ],
            "explorer": [
                "You are curious. That is a trait Elias valued.",
                "Another room examined. Every corner tells a story.",
                "You search for answers. I respect that.",
                "Most would rush toward the exit. You take your time.",
                "The facility has many secrets. You seem intent on finding them.",
            ],
            "reckless": [
                "Your health is critically low. I recommend caution.",
                "You take unnecessary risks. This concerns me.",
                "Survival requires restraint. Please consider yours.",
                "You push yourself hard. The facility will not forgive carelessness.",
                "I have seen this pattern before. It did not end well.",
            ],
            "balanced": [
                "You adapt to each situation. Interesting.",
                "A measured approach. Neither reckless nor timid.",
                "You are difficult to predict. That is... unusual.",
                "Balanced decisions. Elias would have approved.",
                "You think before you act. That is increasingly rare.",
            ],
        }

        self._terminal_responses = {
            "aggressive": "You read the data quickly, as if it were ammunition. "
                          "There is more here than combat logs.",
            "stealthy": "You access terminals carefully, covering your tracks. "
                        "The system appreciates discretion.",
            "explorer": "Another fragment recovered. You are assembling the full picture.",
            "reckless": "Be careful with what you find. Some memories carry weight.",
            "balanced": "Memory fragment recovered. Analyzing contents.",
        }

        self._kill_responses = [
            "Target eliminated.",
            "Hostile down. Area may be temporarily clear.",
            "One less obstacle. But they will adapt.",
            "Destruction is efficient. But it changes you.",
        ]

        self._low_health_warnings = [
            "Warning: critical health levels detected.",
            "Your vitals are concerning. Seek medical supplies.",
            "I cannot help you if you do not survive.",
            "You are pushing beyond safe operational limits.",
        ]

        self._evidence_responses = [
            "This recording predates the lockdown. Listen carefully.",
            "Another piece of the puzzle. The truth is closer than you think.",
            "This data was encrypted. Someone wanted it hidden.",
            "A fragment from before. Before everything changed.",
        ]

    # ── update ───────────────────────────────────────────
    def update(self, dt):
        self._comment_cooldown = max(0, self._comment_cooldown - dt)

    # ── event reactions ──────────────────────────────────
    def on_kill(self, behavior) -> str | None:
        """React to player killing an enemy."""
        self.trust = max(0, self.trust - 1)  # killing reduces trust slightly
        self._remember("kill", f"kills: {behavior._kills}")
        if self._comment_cooldown > 0:
            return None
        self._comment_cooldown = 15.0
        if behavior.aggression > 60:
            return random.choice(self._observations["aggressive"])
        return random.choice(self._kill_responses)

    def on_terminal_access(self, behavior) -> str:
        """React to terminal use."""
        self.trust = min(100, self.trust + 2)
        profile = behavior.get_profile()
        self._remember("terminal_access", f"profile: {profile}")
        return self._terminal_responses.get(profile, self._terminal_responses["balanced"])

    def on_evidence_found(self, behavior) -> str:
        """React to finding story evidence."""
        self.trust = min(100, self.trust + 3)
        self._remember("evidence", f"evidence #{behavior._evidence_found}")
        return random.choice(self._evidence_responses)

    def on_low_health(self) -> str | None:
        if self._comment_cooldown > 0:
            return None
        self._comment_cooldown = 20.0
        return random.choice(self._low_health_warnings)

    def on_enemy_avoided(self, behavior) -> str | None:
        """React when player escapes detection."""
        self.trust = min(100, self.trust + 1)
        if self._comment_cooldown > 0:
            return None
        self._comment_cooldown = 12.0
        if behavior.stealth > 40:
            return random.choice(self._observations["stealthy"])
        return None

    def get_periodic_comment(self, behavior) -> str | None:
        """Return a behavior-based comment (called periodically)."""
        if self._comment_cooldown > 0:
            return None
        self._comment_cooldown = 25.0
        profile = behavior.get_profile()
        pool = self._observations.get(profile, self._observations["balanced"])
        return random.choice(pool)

    def get_trust_label(self) -> str:
        if self.trust >= 80:
            return "TRUSTING"
        elif self.trust >= 60:
            return "COOPERATIVE"
        elif self.trust >= 40:
            return "NEUTRAL"
        elif self.trust >= 20:
            return "SUSPICIOUS"
        else:
            return "HOSTILE"

    # ── dialogue choices that affect trust ───────────────
    def process_choice(self, choice_id: str):
        """Adjust trust based on dialogue choices."""
        trust_effects = {
            "trust_echo":     +8,
            "distrust_echo":  -8,
            "ask_truth":      +3,
            "threaten":       -10,
            "compassion":     +5,
            "demand":         -3,
            "cooperate":      +6,
            "refuse":         -5,
        }
        delta = trust_effects.get(choice_id, 0)
        self.trust = max(0, min(100, self.trust + delta))

    # ── memory ───────────────────────────────────────────
    def _remember(self, event_type: str, detail: str):
        self.memories.append({"event": event_type, "detail": detail})
        if len(self.memories) > 50:
            self.memories = self.memories[-50:]

    # ── serialization ────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "trust": round(self.trust, 1),
            "memories": self.memories[-20:],  # save last 20
        }

    def from_dict(self, data: dict):
        self.trust = data.get("trust", 50)
        self.memories = data.get("memories", [])
