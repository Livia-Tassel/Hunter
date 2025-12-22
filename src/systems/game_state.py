"""Game state management and save/load system"""
import json
import os
from typing import Dict, Any, Optional
from ..core.entities import Player, Room, Item

class GameState:
    def __init__(self, save_file: str):
        self.save_file = save_file
        self.player: Optional[Player] = None
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        self.npcs: Dict[str, Any] = {}

    def save_game(self) -> bool:
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
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_game(self) -> bool:
        if not os.path.exists(self.save_file):
            return False

        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
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
