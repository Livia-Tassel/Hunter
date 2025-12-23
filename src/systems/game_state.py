"""Enhanced game state management with multi-save and auto-save"""
import json
import os
from typing import Dict, Any, Optional, List
from ..core.entities import Player, Room, Item

class GameState:
    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.player: Optional[Player] = None
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        self.npcs: Dict[str, Any] = {}
        self.auto_save_interval = 10  # Auto-save every N actions
        self.last_auto_save = 0

    def get_save_file(self, slot: int = 1) -> str:
        return os.path.join(self.save_dir, f"save_slot_{slot}.json")

    def list_saves(self) -> List[Dict[str, Any]]:
        """List all available save slots"""
        saves = []
        for slot in range(1, 4):  # 3 save slots
            save_file = self.get_save_file(slot)
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        saves.append({
                            'slot': slot,
                            'location': data.get('player_room_id', 'Unknown'),
                            'level': data.get('player_level', 1),
                            'exists': True
                        })
                except Exception:
                    saves.append({'slot': slot, 'exists': False})
            else:
                saves.append({'slot': slot, 'exists': False})
        return saves

    def should_auto_save(self) -> bool:
        """Check if auto-save should trigger"""
        if not self.player:
            return False
        if self.player.actions_count - self.last_auto_save >= self.auto_save_interval:
            return True
        return False

    def auto_save(self) -> bool:
        """Perform auto-save"""
        if self.save_game(slot=0):  # Slot 0 is auto-save
            self.last_auto_save = self.player.actions_count if self.player else 0
            return True
        return False

    def save_game(self, slot: int = 1) -> bool:
        if not self.player:
            return False

        game_state = {
            "player_room_id": self.player.current_room_id,
            "player_inventory": [i.name for i in self.player.inventory],
            "player_health": self.player.health,
            "player_max_health": self.player.max_health,
            "player_score": self.player.score,
            "player_level": self.player.level,
            "player_experience": self.player.experience,
            "player_strength": self.player.strength,
            "player_defense": self.player.defense,
            "player_intelligence": self.player.intelligence,
            "player_gold": self.player.gold,
            "player_visited_rooms": self.player.visited_rooms,
            "player_actions_count": self.player.actions_count,
            "player_history": self.player.history,
            "room_states": {}
        }

        for room_id, room in self.rooms.items():
            game_state["room_states"][room_id] = {
                "items_in_room": [i.name for i in room.items],
                "properties": room.properties.copy(),
                "exits": room.exits.copy(),
                "description": room.description,
                "visited_art_shown": room.visited_art_shown,
                "ambient_sound": room.ambient_sound
            }

        try:
            os.makedirs(self.save_dir, exist_ok=True)
            save_file = self.get_save_file(slot)
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_game(self, slot: int = 1) -> bool:
        save_file = self.get_save_file(slot)
        if not os.path.exists(save_file):
            return False

        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                game_state = json.load(f)

            if not self.player:
                return False

            self.player.current_room_id = game_state.get("player_room_id", "cabin")
            self.player.health = game_state.get("player_health", 100)
            self.player.max_health = game_state.get("player_max_health", 100)
            self.player.score = game_state.get("player_score", 0)
            self.player.level = game_state.get("player_level", 1)
            self.player.experience = game_state.get("player_experience", 0)
            self.player.strength = game_state.get("player_strength", 10)
            self.player.defense = game_state.get("player_defense", 5)
            self.player.intelligence = game_state.get("player_intelligence", 10)
            self.player.gold = game_state.get("player_gold", 0)
            self.player.visited_rooms = game_state.get("player_visited_rooms", [])
            self.player.actions_count = game_state.get("player_actions_count", 0)
            self.player.history = game_state.get("player_history", self.player.history)

            self.player.inventory = [
                self.items[name.lower()]
                for name in game_state.get("player_inventory", [])
                if name.lower() in self.items
            ]

            loaded_room_states = game_state.get("room_states", {})
            for room_id, room in self.rooms.items():
                room_data = loaded_room_states.get(room_id)
                if room_data:
                    room.items = [
                        self.items[name.lower()]
                        for name in room_data.get("items_in_room", [])
                        if name.lower() in self.items
                    ]
                    room.properties = room_data.get("properties", room.properties)
                    room.exits = room_data.get("exits", room.exits)
                    room.description = room_data.get("description", room.description)
                    room.visited_art_shown = room_data.get("visited_art_shown", False)
                    room.ambient_sound = room_data.get("ambient_sound", room.ambient_sound)

            return True
        except Exception:
            return False
