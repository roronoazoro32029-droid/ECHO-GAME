"""
Inventory — manages the player's item collection.
Items are defined as dicts; the inventory stores item_id → quantity.
"""

# ── Item definitions ─────────────────────────────────────
ITEM_DB = {
    "medkit": {
        "name": "Medkit",
        "desc": "Restores 40 HP.",
        "icon_color": (200, 40, 40),
        "icon_symbol": "+",
        "stackable": True,
        "max_stack": 5,
        "usable": True,
        "category": "consumable",
    },
    "energy_cell": {
        "name": "Energy Cell",
        "desc": "Restores 35 Energy.",
        "icon_color": (0, 180, 220),
        "icon_symbol": "⚡",
        "stackable": True,
        "max_stack": 5,
        "usable": True,
        "category": "consumable",
    },
    "ammo_pack": {
        "name": "Ammo Pack",
        "desc": "Restores 12 rounds.",
        "icon_color": (180, 180, 80),
        "icon_symbol": "■",
        "stackable": True,
        "max_stack": 8,
        "usable": True,
        "category": "consumable",
    },
    "emp_charge": {
        "name": "EMP Charge",
        "desc": "Extra EMP charge. Restores 40 energy.",
        "icon_color": (220, 220, 60),
        "icon_symbol": "◎",
        "stackable": True,
        "max_stack": 4,
        "usable": True,
        "category": "consumable",
    },
    "access_card_a": {
        "name": "Access Card A",
        "desc": "Opens Security Level A doors.",
        "icon_color": (60, 200, 100),
        "icon_symbol": "▪",
        "stackable": False,
        "max_stack": 1,
        "usable": False,
        "category": "key",
    },
    "access_card_b": {
        "name": "Access Card B",
        "desc": "Opens Security Level B doors.",
        "icon_color": (60, 120, 220),
        "icon_symbol": "▪",
        "stackable": False,
        "max_stack": 1,
        "usable": False,
        "category": "key",
    },
    "data_drive_1": {
        "name": "Research Log #1",
        "desc": "A corrupted data drive. Contains fragments of Project ECHO.",
        "icon_color": (160, 100, 220),
        "icon_symbol": "◆",
        "stackable": False,
        "max_stack": 1,
        "usable": False,
        "category": "evidence",
    },
    "data_drive_2": {
        "name": "Research Log #2",
        "desc": "Personnel file. Subject: Dr. E. Voss.",
        "icon_color": (160, 100, 220),
        "icon_symbol": "◆",
        "stackable": False,
        "max_stack": 1,
        "usable": False,
        "category": "evidence",
    },
    "data_drive_3": {
        "name": "Security Recording",
        "desc": "Audio log — final day before lockdown.",
        "icon_color": (160, 100, 220),
        "icon_symbol": "◆",
        "stackable": False,
        "max_stack": 1,
        "usable": False,
        "category": "evidence",
    },
    "fuse": {
        "name": "Power Fuse",
        "desc": "Can restore power to offline systems.",
        "icon_color": (220, 160, 40),
        "icon_symbol": "⊞",
        "stackable": True,
        "max_stack": 3,
        "usable": False,
        "category": "component",
    },
}


class Inventory:
    """Manages item_id → quantity mapping with max capacity."""

    def __init__(self, max_slots=16):
        self.items: dict[str, int] = {}  # item_id → count
        self.max_slots = max_slots

    def add_item(self, item_id: str, count: int = 1) -> bool:
        """Add item. Returns True if successfully added."""
        if item_id not in ITEM_DB:
            return False
        info = ITEM_DB[item_id]

        if item_id in self.items:
            max_s = info["max_stack"]
            self.items[item_id] = min(self.items[item_id] + count, max_s)
            return True
        else:
            if len(self.items) >= self.max_slots:
                return False  # inventory full
            self.items[item_id] = min(count, info["max_stack"])
            return True

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        if item_id not in self.items:
            return False
        self.items[item_id] -= count
        if self.items[item_id] <= 0:
            del self.items[item_id]
        return True

    def has_item(self, item_id: str) -> bool:
        return item_id in self.items and self.items[item_id] > 0

    def get_count(self, item_id: str) -> int:
        return self.items.get(item_id, 0)

    def get_items_list(self) -> list[tuple[str, int]]:
        """Return list of (item_id, count) for UI display."""
        return list(self.items.items())

    def to_dict(self) -> dict:
        return dict(self.items)

    def from_dict(self, data: dict):
        self.items = dict(data)

    def use_item(self, item_id: str, player) -> str | None:
        """
        Use a consumable item on the player.
        Returns a message string, or None if not usable.
        """
        if not self.has_item(item_id):
            return None
        info = ITEM_DB.get(item_id)
        if not info or not info.get("usable"):
            return None

        if item_id == "medkit":
            if player.health >= player.max_health:
                return "Health is already full."
            player.health = min(player.max_health, player.health + 40)
            self.remove_item(item_id)
            return "Medkit applied. +40 HP."

        elif item_id == "energy_cell":
            if player.energy >= player.max_energy:
                return "Energy is already full."
            player.energy = min(player.max_energy, player.energy + 35)
            self.remove_item(item_id)
            return "Energy cell used. +35 Energy."

        elif item_id == "ammo_pack":
            if player.ammo >= player.max_ammo:
                return "Ammo is already full."
            player.ammo = min(player.max_ammo, player.ammo + 12)
            self.remove_item(item_id)
            return "Ammo loaded. +12 rounds."

        elif item_id == "emp_charge":
            if player.energy >= player.max_energy:
                return "Energy is already full."
            player.energy = min(player.max_energy, player.energy + 40)
            self.remove_item(item_id)
            return "EMP charge absorbed. +40 Energy."

        return None
