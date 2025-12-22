"""Achievement and crafting systems"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from ..core.entities import Item, Player

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    unlocked: bool = False
    hidden: bool = False

class AchievementSystem:
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self._init_achievements()

    def _init_achievements(self):
        achievements = [
            Achievement("first_steps", "初次探险", "开始你的冒险之旅"),
            Achievement("explorer", "探险家", "探索所有房间"),
            Achievement("collector", "收藏家", "收集10个物品"),
            Achievement("treasure_hunter", "寻宝猎人", "找到远古神像"),
            Achievement("puzzle_master", "解谜大师", "解开所有谜题"),
            Achievement("survivor", "幸存者", "生命值降至10以下后存活"),
            Achievement("level_5", "进阶冒险者", "达到5级"),
            Achievement("rich", "富有", "拥有100金币"),
            Achievement("crafter", "工匠", "合成5个物品"),
            Achievement("social", "社交达人", "与所有NPC对话"),
        ]
        for ach in achievements:
            self.achievements[ach.id] = ach

    def unlock(self, achievement_id: str) -> bool:
        if achievement_id in self.achievements and not self.achievements[achievement_id].unlocked:
            self.achievements[achievement_id].unlocked = True
            return True
        return False

    def check_and_unlock(self, achievement_id: str, condition: bool) -> bool:
        if condition:
            return self.unlock(achievement_id)
        return False

    def get_all(self) -> List[Tuple[str, str, bool]]:
        return [(a.name, a.description, a.unlocked) for a in self.achievements.values() if not a.hidden]

    def get_unlocked_count(self) -> int:
        return sum(1 for a in self.achievements.values() if a.unlocked)

@dataclass
class Recipe:
    id: str
    name: str
    materials: List[str]
    result: str
    result_item: Optional[Item] = None

class CraftingSystem:
    def __init__(self):
        self.recipes: Dict[str, Recipe] = {}
        self.crafted_count = 0

    def add_recipe(self, recipe: Recipe):
        self.recipes[recipe.id] = recipe

    def can_craft(self, recipe_id: str, player: Player) -> bool:
        if recipe_id not in self.recipes:
            return False
        recipe = self.recipes[recipe_id]
        for material in recipe.materials:
            if not player.has_item(material):
                return False
        return True

    def craft(self, recipe_id: str, player: Player, items_dict: Dict[str, Item]) -> Optional[Item]:
        if not self.can_craft(recipe_id, player):
            return None

        recipe = self.recipes[recipe_id]

        # Remove materials
        for material in recipe.materials:
            player.remove_from_inventory(material)

        # Create result item
        if recipe.result in items_dict:
            result_item = items_dict[recipe.result]
        else:
            result_item = Item(recipe.result, recipe.result, f"合成的{recipe.result}", True)

        self.crafted_count += 1
        return result_item

    def get_available_recipes(self, player: Player) -> List[Tuple[str, str, str]]:
        available = []
        for recipe in self.recipes.values():
            materials_str = " + ".join(recipe.materials)
            available.append((recipe.name, materials_str, recipe.result))
        return available

def init_crafting_recipes(crafting_system: CraftingSystem):
    """Initialize crafting recipes"""
    recipes = [
        Recipe("torch_oil", "长效火把", ["火把", "油"], "长效火把"),
        Recipe("grappling_hook", "抓钩", ["绳子", "钩子"], "抓钩"),
        Recipe("healing_potion_strong", "强效治疗药水", ["治疗药水", "草药"], "强效治疗药水"),
        Recipe("lockpick", "开锁工具", ["铁丝", "撬棍"], "开锁工具"),
        Recipe("map_enhanced", "详细地图", ["古老的地图", "墨水"], "详细地图"),
    ]

    for recipe in recipes:
        crafting_system.add_recipe(recipe)
