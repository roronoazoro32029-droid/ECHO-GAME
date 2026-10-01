"""
Player Behavior Tracker — records how the player plays.
Values are normalized 0–100 and used by ECHO's adaptive system.
"""


class PlayerBehavior:
    def __init__(self):
        self.aggression = 0.0
        self.stealth = 0.0
        self.exploration = 0.0
        self.risk_taking = 0.0
        self.resource_usage = 0.0

        # raw counters for normalization
        self._kills = 0
        self._shots_fired = 0
        self._damage_dealt = 0
        self._enemies_avoided = 0
        self._time_unseen = 0.0
        self._rooms_visited = set()
        self._terminals_accessed = 0
        self._evidence_found = 0
        self._low_health_time = 0.0
        self._items_used = 0
        self._doors_opened = 0
        self._total_play_time = 0.0

    # ── event hooks (called by Game) ─────────────────────
    def on_kill(self):
        self._kills += 1
        self._recalc()

    def on_shot_fired(self):
        self._shots_fired += 1
        self._recalc()

    def on_damage_dealt(self, amount):
        self._damage_dealt += amount
        self._recalc()

    def on_enemy_avoided(self):
        """Called when an enemy loses the player after alert."""
        self._enemies_avoided += 1
        self._recalc()

    def on_time_unseen(self, dt):
        self._time_unseen += dt

    def on_room_visited(self, room_id: str):
        self._rooms_visited.add(room_id)
        self._recalc()

    def on_terminal_accessed(self):
        self._terminals_accessed += 1
        self._recalc()

    def on_evidence_found(self):
        self._evidence_found += 1
        self._recalc()

    def on_low_health(self, dt):
        self._low_health_time += dt
        self._recalc()

    def on_item_used(self):
        self._items_used += 1
        self._recalc()

    def on_door_opened(self):
        self._doors_opened += 1
        self._recalc()

    def update(self, dt, player_health, max_health):
        """Called every frame."""
        self._total_play_time += dt
        if player_health < max_health * 0.35:
            self.on_low_health(dt)

    # ── recalculate scores ───────────────────────────────
    def _recalc(self):
        # Aggression: kills + shots + damage
        raw_agg = self._kills * 15 + self._shots_fired * 1.5 + self._damage_dealt * 0.1
        self.aggression = min(100, raw_agg)

        # Stealth: time unseen + enemies avoided - aggression penalty
        raw_stealth = (self._enemies_avoided * 20 +
                       self._time_unseen * 0.3 -
                       self.aggression * 0.3)
        self.stealth = max(0, min(100, raw_stealth))

        # Exploration: rooms + terminals + evidence + doors
        raw_explore = (len(self._rooms_visited) * 12 +
                       self._terminals_accessed * 15 +
                       self._evidence_found * 20 +
                       self._doors_opened * 5)
        self.exploration = min(100, raw_explore)

        # Risk-taking: low health time + aggression
        raw_risk = self._low_health_time * 2 + self.aggression * 0.3
        self.risk_taking = min(100, raw_risk)

        # Resource usage: items used
        raw_res = self._items_used * 12
        self.resource_usage = min(100, raw_res)

    def get_profile(self) -> str:
        """Return the dominant behavior profile."""
        scores = {
            "aggressive": self.aggression,
            "stealthy": self.stealth,
            "explorer": self.exploration,
            "reckless": self.risk_taking,
        }
        if max(scores.values()) < 15:
            return "balanced"
        return max(scores, key=scores.get)

    def to_dict(self) -> dict:
        return {
            "aggression": round(self.aggression, 1),
            "stealth": round(self.stealth, 1),
            "exploration": round(self.exploration, 1),
            "risk_taking": round(self.risk_taking, 1),
            "resource_usage": round(self.resource_usage, 1),
            "kills": self._kills,
            "shots_fired": self._shots_fired,
            "terminals_accessed": self._terminals_accessed,
            "evidence_found": self._evidence_found,
            "rooms_visited": list(self._rooms_visited),
            "items_used": self._items_used,
            "play_time": round(self._total_play_time, 1),
        }

    def from_dict(self, data: dict):
        self.aggression = data.get("aggression", 0)
        self.stealth = data.get("stealth", 0)
        self.exploration = data.get("exploration", 0)
        self.risk_taking = data.get("risk_taking", 0)
        self.resource_usage = data.get("resource_usage", 0)
        self._kills = data.get("kills", 0)
        self._shots_fired = data.get("shots_fired", 0)
        self._terminals_accessed = data.get("terminals_accessed", 0)
        self._evidence_found = data.get("evidence_found", 0)
        self._rooms_visited = set(data.get("rooms_visited", []))
        self._items_used = data.get("items_used", 0)
        self._total_play_time = data.get("play_time", 0)
