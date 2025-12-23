"""Core game entities: Item, Room, NPC, Player"""
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class Item:
    name: str
    display_name: str
    description: str
    takeable: bool = True
    use_on: Optional[str] = None
    effect_description: Optional[str] = None
    ascii_art_name: Optional[str] = None
    item_type: str = "misc"
    value: int = 0

    def __post_init__(self):
        self.name = self.name.lower()

@dataclass
class Room:
    name: str
    display_name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)
    items: List[Item] = field(default_factory=list)
    npcs: List['NPC'] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    ascii_art_on_enter: Optional[str] = None
    ambient_sound: Optional[str] = None
    visited_art_shown: bool = False
    monsters: List['NPC'] = field(default_factory=list)

    def add_exit(self, direction: str, room_id: str):
        self.exits[direction.lower()] = room_id

    def add_item(self, item: Item):
        self.items.append(item)

    def remove_item(self, item_name: str) -> Optional[Item]:
        item_name_lower = item_name.lower()
        for i, item in enumerate(self.items):
            if item.name == item_name_lower:
                return self.items.pop(i)
        return None

    def has_item(self, item_name: str) -> bool:
        return any(item.name == item_name.lower() for item in self.items)

@dataclass
class NPC:
    name: str
    description: str
    dialogue: Dict[str, str] = field(default_factory=dict)
    inventory: List[Item] = field(default_factory=list)
    ascii_art_name: Optional[str] = None
    tts_voice_name: Optional[str] = None
    health: int = 100
    attack_power: int = 10
    defense_power: int = 5
    hostile: bool = False

    def talk(self, topic: str = "default") -> str:
        return self.dialogue.get(topic.lower(), self.dialogue.get("default", "嗯？我不明白你的意思。"))

@dataclass
class Player:
    current_room_id: str
    inventory: List[Item] = field(default_factory=list)
    health: int = 100
    max_health: int = 100
    score: int = 0
    strength: int = 10
    intelligence: int = 10
    defense: int = 5
    experience: int = 0
    level: int = 1
    gold: int = 0
    visited_rooms: List[str] = field(default_factory=list)
    actions_count: int = 0
    history: List[str] = field(default_factory=list)

    def add_to_inventory(self, item: Item):
        self.inventory.append(item)
        self.actions_count += 1

    def remove_from_inventory(self, item_name: str) -> Optional[Item]:
        item_name_lower = item_name.lower()
        for i, item in enumerate(self.inventory):
            if item.name == item_name_lower:
                return self.inventory.pop(i)
        return None

    def has_item(self, item_name: str) -> bool:
        return any(item.name == item_name.lower() for item in self.inventory)

    def take_damage(self, damage: int):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def add_experience(self, exp: int):
        self.experience += exp
        while self.experience >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        self.strength += 2
        self.defense += 1
        self.intelligence += 1

    def add_gold(self, amount: int):
        self.gold += amount

    def record_action(self, description: str):
        """Track recent actions for auto-save and journal display"""
        self.actions_count += 1
        self.history.append(description)
        # Keep the journal reasonably small
        if len(self.history) > 30:
            self.history = self.history[-30:]

    def visit_room(self, room_id: str, label: Optional[str] = None):
        """Mark a room as visited and log it"""
        if room_id not in self.visited_rooms:
            self.visited_rooms.append(room_id)
        self.record_action(f"抵达 {label or room_id}")

    def spend_gold(self, amount: int) -> bool:
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
