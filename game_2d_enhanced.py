# -*- coding: utf-8 -*-
"""Enhanced 2D Graphical Game with Pixel Art, Animations, Achievements, Crafting, Quests"""
import pygame
import sys
import random
import subprocess
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
BLUE = (70, 130, 180)
YELLOW = (255, 215, 0)
RED = (220, 20, 60)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 140, 0)

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    unlocked: bool = False

@dataclass
class Quest:
    id: str
    name: str
    description: str
    completed: bool = False

@dataclass
class GameRoom:
    id: str
    name: str
    tiles: List[List[int]]
    spawn_x: int
    spawn_y: int
    exits: Dict[str, Tuple[str, int, int]] = field(default_factory=dict)  # name -> (target_room, target_x, target_y)
    exit_positions: Dict[str, Tuple[int, int]] = field(default_factory=dict)  # name -> (exit_tile_x, exit_tile_y)
    properties: Dict[str, any] = field(default_factory=dict)

@dataclass
class Recipe:
    id: str
    name: str
    materials: List[str]
    result: str

@dataclass
class Player:
    x: float
    y: float
    speed: float = 3.0
    inventory: List[str] = field(default_factory=list)
    health: int = 100
    max_health: int = 100
    gold: int = 0
    level: int = 1
    exp: int = 0
    direction: str = "down"
    animation_frame: int = 0
    animation_timer: float = 0

@dataclass
class Item:
    x: float
    y: float
    name: str
    color: Tuple[int, int, int]
    room_id: str
    picked_up: bool = False

@dataclass
class NPC:
    x: float
    y: float
    name: str
    color: Tuple[int, int, int]
    dialogue: Dict[str, str]
    room_id: str
    current_topic: str = "default"

class SpriteGenerator:
    """Generate simple pixel art sprites"""
    @staticmethod
    def create_player_sprite(direction: str, frame: int) -> pygame.Surface:
        sprite = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Body
        pygame.draw.rect(sprite, RED, (8, 8, 8, 12))
        # Head
        pygame.draw.circle(sprite, (255, 200, 150), (12, 6), 4)
        # Legs (animated)
        if frame % 2 == 0:
            pygame.draw.rect(sprite, BLUE, (8, 20, 3, 4))
            pygame.draw.rect(sprite, BLUE, (13, 20, 3, 4))
        else:
            pygame.draw.rect(sprite, BLUE, (9, 20, 3, 4))
            pygame.draw.rect(sprite, BLUE, (12, 20, 3, 4))
        return sprite

    @staticmethod
    def create_npc_sprite() -> pygame.Surface:
        sprite = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(sprite, BLUE, (8, 8, 8, 12))
        pygame.draw.circle(sprite, (255, 220, 180), (12, 6), 4)
        pygame.draw.rect(sprite, GRAY, (8, 20, 8, 4))
        return sprite

    @staticmethod
    def create_item_sprite(color: Tuple[int, int, int]) -> pygame.Surface:
        sprite = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(sprite, color, (8, 8), 6)
        pygame.draw.circle(sprite, WHITE, (8, 8), 6, 2)
        return sprite

class Game2DEnhanced:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("迷失的宝藏猎人 - Enhanced")
        self.clock = pygame.time.Clock()
        self.running = True

        self.rooms = self._create_rooms()
        self.current_room_id = "cabin"
        cabin_spawn = self.rooms["cabin"]
        self.player = Player(x=cabin_spawn.spawn_x * TILE_SIZE, y=cabin_spawn.spawn_y * TILE_SIZE)

        # Load Chinese-compatible font
        font_loaded = False
        for font_name in ['stheitimedium', 'stheitilight', 'pingfangsc', 'notosanssc']:
            try:
                test_font = pygame.font.SysFont(font_name, 24)
                test_surface = test_font.render('测试', True, (255, 255, 255))
                if test_surface.get_width() > 20:
                    self.font = pygame.font.SysFont(font_name, 24)
                    self.title_font = pygame.font.SysFont(font_name, 48)
                    self.small_font = pygame.font.SysFont(font_name, 18)
                    print(f"✓ Using font: {font_name}")
                    font_loaded = True
                    break
            except:
                continue

        if not font_loaded:
            print("✗ WARNING: No Chinese font found!")
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 48)
            self.small_font = pygame.font.Font(None, 18)

        self.items = self._create_items()
        self.npcs = self._create_npcs()
        self.monsters = self._create_monsters()

        self.achievements = self._init_achievements()
        self.quests = self._init_quests()
        self.recipes = self._init_recipes()

        self.show_dialogue = False
        self.dialogue_text = ""
        self.dialogue_npc = None
        self.dialogue_topics = []
        self.show_inventory = False
        self.show_achievements = False
        self.show_crafting = False
        self.show_quests = False
        self.nearby_item = None
        self.nearby_npc = None
        self.nearby_interactive = None
        self.game_won = False

        self.sprite_gen = SpriteGenerator()
        self.tts_enabled = True
        self.transition_cooldown = 0
        self.feedback_message = ""
        self.feedback_timer = 0

    def _create_rooms(self) -> Dict[str, GameRoom]:
        rooms = {}

        # Cabin - 20x15 tiles (玩家出生在中央)
        cabin_tiles = [[2 if (x > 0 and x < 19 and y > 0 and y < 14) else 1 for x in range(20)] for y in range(15)]
        # 开放北边和东边的门
        cabin_tiles[1][10] = 2  # 北门
        cabin_tiles[7][18] = 2  # 东门
        rooms["cabin"] = GameRoom(
            id="cabin", name="废弃小屋", tiles=cabin_tiles, spawn_x=10, spawn_y=7,
            exits={"北": ("forest_path", 10, 13), "东": ("dark_cellar_entrance", 2, 7)},
            exit_positions={"北": (10, 1), "东": (18, 7)},
            properties={"fireplace_lit": False, "table_searched": False}
        )

        # Forest Path - 20x15 tiles
        forest_tiles = [[0 for x in range(20)] for y in range(15)]
        # 添加一些树木作为装饰
        for y in range(15):
            for x in range(20):
                if (x + y) % 5 == 0 and not (x == 10 and (y <= 2 or y >= 12)):
                    forest_tiles[y][x] = 1
        rooms["forest_path"] = GameRoom(
            id="forest_path", name="森林小径", tiles=forest_tiles, spawn_x=10, spawn_y=13,
            exits={"南": ("cabin", 10, 2), "北": ("deep_forest", 10, 13)},
            exit_positions={"南": (10, 14), "北": (10, 1)},
            properties={"leaves_searched": False}
        )

        # Dark Cellar Entrance - 20x15 tiles
        cellar_ent_tiles = [[2 if x > 0 and x < 19 and y > 0 and y < 14 else 1 for x in range(20)] for y in range(15)]
        cellar_ent_tiles[7][1] = 2  # 西门
        cellar_ent_tiles[13][10] = 2  # 下楼梯
        rooms["dark_cellar_entrance"] = GameRoom(
            id="dark_cellar_entrance", name="地下室入口", tiles=cellar_ent_tiles, spawn_x=2, spawn_y=7,
            exits={"西": ("cabin", 17, 7), "下": ("cellar", 10, 2)},
            exit_positions={"西": (1, 7), "下": (10, 13)},
            properties={"door_locked": True, "requires_light": True}
        )

        # Cellar - 20x15 tiles
        cellar_tiles = [[4 for x in range(20)] for y in range(15)]
        for x in range(20):
            cellar_tiles[0][x] = 1
            cellar_tiles[14][x] = 1
        for y in range(15):
            cellar_tiles[y][0] = 1
            cellar_tiles[y][19] = 1
        rooms["cellar"] = GameRoom(
            id="cellar", name="阴暗的地下室", tiles=cellar_tiles, spawn_x=10, spawn_y=2,
            exits={"上": ("dark_cellar_entrance", 10, 12)},
            exit_positions={"上": (10, 1)},
            properties={"crates_searched": False}
        )

        # Deep Forest - 20x15 tiles
        deep_forest_tiles = [[0 for x in range(20)] for y in range(15)]
        for y in range(15):
            for x in range(20):
                if (x * y) % 7 == 0 and not (x == 10 and (y <= 2 or y >= 12)) and not (x >= 8 and x <= 12 and y >= 5 and y <= 8):
                    deep_forest_tiles[y][x] = 1
        rooms["deep_forest"] = GameRoom(
            id="deep_forest", name="森林深处", tiles=deep_forest_tiles, spawn_x=10, spawn_y=13,
            exits={"南": ("forest_path", 10, 2), "进入洞穴": ("cave_entrance", 10, 10)},
            exit_positions={"南": (10, 14), "进入洞穴": (10, 6)},
            properties={"cave_hidden": False}
        )

        # Cave Entrance - 20x15 tiles
        cave_ent_tiles = [[4 if x > 2 and x < 17 and y > 2 and y < 12 else 1 for x in range(20)] for y in range(15)]
        rooms["cave_entrance"] = GameRoom(
            id="cave_entrance", name="洞穴入口", tiles=cave_ent_tiles, spawn_x=10, spawn_y=10,
            exits={"离开洞穴": ("deep_forest", 10, 7), "深入": ("cave_chamber", 3, 7)},
            exit_positions={"离开洞穴": (10, 12), "深入": (3, 7)},
            properties={"symbols_deciphered": False}
        )

        # Cave Chamber - 20x15 tiles  
        cave_chamber_tiles = [[4 for x in range(20)] for y in range(15)]
        for x in range(20):
            cave_chamber_tiles[0][x] = 1
            cave_chamber_tiles[14][x] = 1
        for y in range(15):
            cave_chamber_tiles[y][0] = 1
            cave_chamber_tiles[y][19] = 1
        rooms["cave_chamber"] = GameRoom(
            id="cave_chamber", name="洞穴密室", tiles=cave_chamber_tiles, spawn_x=3, spawn_y=7,
            exits={"离开": ("cave_entrance", 16, 7)},
            exit_positions={"离开": (1, 7)},
            properties={"coffin_opened": False, "treasure_found": False}
        )

        return rooms

    def _create_items(self) -> List[Item]:
        return [
            Item(x=5*TILE_SIZE, y=7*TILE_SIZE, name="火把", color=YELLOW, room_id="cabin", picked_up=False),
            Item(x=15*TILE_SIZE, y=7*TILE_SIZE, name="古老的地图", color=BROWN, room_id="cabin", picked_up=False),
            Item(x=10*TILE_SIZE, y=10*TILE_SIZE, name="生锈的钥匙", color=GRAY, room_id="forest_path", picked_up=False),
            Item(x=10*TILE_SIZE, y=5*TILE_SIZE, name="治疗药水", color=RED, room_id="forest_path", picked_up=False),
            Item(x=10*TILE_SIZE, y=7*TILE_SIZE, name="远古神像", color=BLUE, room_id="cave_chamber", picked_up=False),
            Item(x=5*TILE_SIZE, y=5*TILE_SIZE, name="撬棍", color=GRAY, room_id="cellar", picked_up=False),
            Item(x=15*TILE_SIZE, y=10*TILE_SIZE, name="绳子", color=BROWN, room_id="deep_forest", picked_up=False),
        ]

    def _create_npcs(self) -> List[NPC]:
        dialogue = {
            "default": "年轻人，此地凶险，亦藏机缘。\n按数字键选择话题：\n1-宝藏 2-火种 3-此地危险 4-再见",
            "宝藏": "那远古的秘宝藏匿于洞穴最深处，\n被复杂的机关守护。",
            "火种": "在黑暗中，火光能成为指引方向的希望。\n壁炉可以点燃火把。",
            "此地危险": "此地危机四伏，不仅有致命机关，\n更有因秘宝力量而扭曲的生灵徘徊。",
            "再见": "去吧，愿你好运，年轻人。\n记住，选择比寻找更重要。"
        }
        return [NPC(x=5*TILE_SIZE, y=5*TILE_SIZE, name="斗桨先生", color=BLUE, dialogue=dialogue, room_id="cabin")]

    def _create_monsters(self) -> List[dict]:
        """Create hostile monsters in the game world"""
        return [
            {"name": "森林狼", "x": 8*TILE_SIZE, "y": 8*TILE_SIZE, "room_id": "deep_forest",
             "health": 50, "max_health": 50, "attack": 12, "defense": 5, "color": GRAY, "defeated": False},
            {"name": "洞穴蝙蝠", "x": 15*TILE_SIZE, "y": 5*TILE_SIZE, "room_id": "cave_entrance",
             "health": 30, "max_health": 30, "attack": 8, "defense": 2, "color": (50, 50, 50), "defeated": False},
            {"name": "骷髅守卫", "x": 15*TILE_SIZE, "y": 7*TILE_SIZE, "room_id": "cave_chamber",
             "health": 80, "max_health": 80, "attack": 15, "defense": 8, "color": WHITE, "defeated": False},
        ]

    def _init_achievements(self) -> List[Achievement]:
        return [
            Achievement("first_steps", "初次探险", "开始冒险之旅"),
            Achievement("explorer", "探险家", "探索所有区域"),
            Achievement("collector", "收藏家", "收集10个物品"),
            Achievement("treasure_hunter", "寻宝猎人", "找到远古神像"),
            Achievement("crafter", "工匠", "合成5个物品"),
        ]

    def _init_quests(self) -> List[Quest]:
        return [
            Quest("find_torch", "寻找火把", "在小屋中找到火把"),
            Quest("find_key", "寻找钥匙", "找到生锈的钥匙"),
            Quest("find_statue", "寻找神像", "在洞穴中找到远古神像"),
        ]

    def _init_recipes(self) -> List[Recipe]:
        return [
            Recipe("torch_oil", "长效火把", ["火把", "油"], "长效火把"),
            Recipe("grappling_hook", "抓钩", ["绳子", "钩子"], "抓钩"),
        ]

    def _speak_text(self, text: str):
        """Use macOS say command for TTS with Chinese voice"""
        if self.tts_enabled and sys.platform == "darwin":
            try:
                clean_text = text.replace('\n', ' ')
                subprocess.Popen(['say', '-v', 'Ting-Ting', clean_text],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass

    def handle_input(self):
        if self.transition_cooldown > 0:
            self.transition_cooldown -= 1
        if self.feedback_timer > 0:
            self.feedback_timer -= 1

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        moving = False

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.player.speed
            self.player.direction = "up"
            moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.player.speed
            self.player.direction = "down"
            moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.player.speed
            self.player.direction = "left"
            moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.player.speed
            self.player.direction = "right"
            moving = True

        if moving:
            self.player.animation_timer += 0.1
            if self.player.animation_timer >= 1:
                self.player.animation_frame = (self.player.animation_frame + 1) % 2
                self.player.animation_timer = 0

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if not self._check_collision(new_x, new_y):
            self.player.x = new_x
            self.player.y = new_y

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    self._handle_f_key()
                elif event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.show_achievements = False
                    self.show_crafting = False
                    self.show_quests = False
                elif event.key == pygame.K_h:  # Changed from K_a to avoid conflict with movement
                    self.show_achievements = not self.show_achievements
                    self.show_inventory = False
                    self.show_crafting = False
                    self.show_quests = False
                elif event.key == pygame.K_r:  # Changed from K_c to R for Recipe
                    self.show_crafting = not self.show_crafting
                    self.show_inventory = False
                    self.show_achievements = False
                    self.show_quests = False
                elif event.key == pygame.K_q:
                    self.show_quests = not self.show_quests
                    self.show_inventory = False
                    self.show_achievements = False
                    self.show_crafting = False
                elif event.key == pygame.K_e:  # Attack key
                    self._handle_attack()
                elif event.key == pygame.K_SPACE:
                    self.show_dialogue = False
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4] and self.show_dialogue and self.dialogue_npc:
                    topics = ["宝藏", "火种", "此地危险", "再见"]
                    idx = event.key - pygame.K_1
                    if idx < len(topics):
                        self.dialogue_text = self.dialogue_npc.dialogue.get(topics[idx], "...")
                        self._speak_text(self.dialogue_text)

        self._check_room_transitions()

    def _check_collision(self, x: float, y: float) -> bool:
        room = self.rooms[self.current_room_id]
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        if 0 <= tile_y < len(room.tiles) and 0 <= tile_x < len(room.tiles[0]):
            return room.tiles[tile_y][tile_x] in [1, 3]
        return True

    def _check_room_transitions(self):
        if self.transition_cooldown > 0:
            return

        room = self.rooms[self.current_room_id]
        tile_x = int(self.player.x // TILE_SIZE)
        tile_y = int(self.player.y // TILE_SIZE)

        # Check each exit using exit_positions for detection
        for exit_name, (next_room, spawn_x, spawn_y) in room.exits.items():
            exit_pos = room.exit_positions.get(exit_name)
            if not exit_pos:
                continue
            
            exit_tile_x, exit_tile_y = exit_pos
            if abs(tile_x - exit_tile_x) < 2 and abs(tile_y - exit_tile_y) < 2:
                # Check for cellar requirements
                if next_room == "cellar":
                    if room.properties.get("door_locked"):
                        if "生锈的钥匙" in self.player.inventory:
                            room.properties["door_locked"] = False
                            self.player.inventory.remove("生锈的钥匙")
                            self.feedback_message = "你用钥匙打开了门！"
                            self.feedback_timer = 60
                        else:
                            self.feedback_message = "门是锁着的，需要钥匙！"
                            self.feedback_timer = 60
                            continue
                    if room.properties.get("requires_light"):
                        if "点燃的火把" not in self.player.inventory:
                            self.feedback_message = "太暗了！需要光源才能前进。"
                            self.feedback_timer = 60
                            continue
                
                # Transition to next room
                self.current_room_id = next_room
                self.player.x = spawn_x * TILE_SIZE
                self.player.y = spawn_y * TILE_SIZE
                self.transition_cooldown = 30
                
                # Flash screen for transition effect
                self.screen.fill(BLACK)
                pygame.display.flip()
                
                self.feedback_message = f"进入 {self.rooms[next_room].name}"
                self.feedback_timer = 60
                break

    def _handle_f_key(self):
        room = self.rooms[self.current_room_id]

        # Fireplace interaction
        if self.current_room_id == "cabin" and "火把" in self.player.inventory:
            fireplace_x, fireplace_y = 3 * TILE_SIZE, 3 * TILE_SIZE
            dist = ((self.player.x - fireplace_x) ** 2 + (self.player.y - fireplace_y) ** 2) ** 0.5
            if dist < 80 and not room.properties.get("fireplace_lit"):
                room.properties["fireplace_lit"] = True
                self.player.inventory.remove("火把")
                self.player.inventory.append("点燃的火把")
                self.feedback_message = "火把已点燃！火光驱散了黑暗。"
                self.feedback_timer = 120
                return

        # Coffin interaction
        if self.current_room_id == "cave_chamber" and "撬棍" in self.player.inventory:
            coffin_x, coffin_y = 10 * TILE_SIZE, 7 * TILE_SIZE
            dist = ((self.player.x - coffin_x) ** 2 + (self.player.y - coffin_y) ** 2) ** 0.5
            if dist < 80 and not room.properties.get("coffin_opened"):
                room.properties["coffin_opened"] = True
                if "远古神像" in self.player.inventory:
                    self.game_won = True
                    self.feedback_message = "棺材打开了！你找到了传说中的宝藏！"
                else:
                    self.feedback_message = "棺材打开了，但里面空空如也..."
                self.feedback_timer = 120
                return

        # Item pickup
        for item in self.items:
            if not item.picked_up and item.room_id == self.current_room_id:
                dist = ((self.player.x - item.x) ** 2 + (self.player.y - item.y) ** 2) ** 0.5
                if dist < 50:
                    item.picked_up = True
                    self.player.inventory.append(item.name)
                    self._check_achievements()
                    self._check_quests()
                    return

        # NPC dialogue
        for npc in self.npcs:
            if npc.room_id == self.current_room_id:
                dist = ((self.player.x - npc.x) ** 2 + (self.player.y - npc.y) ** 2) ** 0.5
                if dist < 50:
                    self.show_dialogue = True
                    self.dialogue_text = npc.dialogue["default"]
                    self.dialogue_npc = npc
                    self._speak_text(self.dialogue_text)
                    return

    def _check_achievements(self):
        if len(self.player.inventory) >= 10:
            for ach in self.achievements:
                if ach.id == "collector" and not ach.unlocked:
                    ach.unlocked = True
        if "远古神像" in self.player.inventory:
            for ach in self.achievements:
                if ach.id == "treasure_hunter" and not ach.unlocked:
                    ach.unlocked = True

    def _check_quests(self):
        for quest in self.quests:
            if quest.id == "find_torch" and "火把" in self.player.inventory:
                quest.completed = True
            elif quest.id == "find_key" and "生锈的钥匙" in self.player.inventory:
                quest.completed = True
            elif quest.id == "find_statue" and "远古神像" in self.player.inventory:
                quest.completed = True

    def _handle_attack(self):
        """Handle attack action against nearby monsters"""
        import random
        
        for monster in self.monsters:
            if monster["room_id"] == self.current_room_id and not monster["defeated"]:
                dist = ((self.player.x - monster["x"]) ** 2 + (self.player.y - monster["y"]) ** 2) ** 0.5
                if dist < 80:
                    # Player attacks
                    player_damage = max(1, self.player.level * 5 + random.randint(5, 15) - monster["defense"])
                    monster["health"] -= player_damage
                    
                    if monster["health"] <= 0:
                        monster["defeated"] = True
                        exp_gain = monster["attack"] * 10
                        gold_gain = monster["attack"] * 5
                        self.player.exp += exp_gain
                        self.player.gold += gold_gain
                        
                        # Level up check
                        if self.player.exp >= self.player.level * 100:
                            self.player.level += 1
                            self.player.max_health += 10
                            self.player.health = self.player.max_health
                            self.feedback_message = f"击败 {monster['name']}！升级到 Lv.{self.player.level}！"
                        else:
                            self.feedback_message = f"击败 {monster['name']}！获得 {exp_gain} 经验, {gold_gain} 金币！"
                    else:
                        # Monster retaliates
                        monster_damage = max(1, monster["attack"] - self.player.level * 2)
                        self.player.health -= monster_damage
                        self.feedback_message = f"对 {monster['name']} 造成 {player_damage} 伤害！受到 {monster_damage} 点反击！"
                        
                        if self.player.health <= 0:
                            self.player.health = 0
                            self.feedback_message = "你被击败了..."
                            # Respawn player
                            self.player.health = self.player.max_health // 2
                            self.current_room_id = "cabin"
                            self.player.x = 10 * TILE_SIZE
                            self.player.y = 7 * TILE_SIZE
                    
                    self.feedback_timer = 90
                    return
        
        self.feedback_message = "附近没有可攻击的目标"
        self.feedback_timer = 60

    def _handle_craft(self):
        """Handle crafting when player presses craft on a valid recipe"""
        for recipe in self.recipes:
            has_all = all(mat in self.player.inventory for mat in recipe.materials)
            if has_all:
                for mat in recipe.materials:
                    self.player.inventory.remove(mat)
                self.player.inventory.append(recipe.result)
                self.feedback_message = f"合成成功：{recipe.result}！"
                self.feedback_timer = 90
                return True
        return False

    def _check_nearby_item(self):
        self.nearby_item = None
        for item in self.items:
            if not item.picked_up and item.room_id == self.current_room_id:
                dist = ((self.player.x - item.x) ** 2 + (self.player.y - item.y) ** 2) ** 0.5
                if dist < 50:
                    self.nearby_item = item
                    return

    def render(self):
        self.screen.fill(BLACK)
        room = self.rooms[self.current_room_id]

        # Render tiles
        for y, row in enumerate(room.tiles):
            for x, tile in enumerate(row):
                screen_x = x * TILE_SIZE
                screen_y = y * TILE_SIZE
                if tile == 0:
                    pygame.draw.rect(self.screen, GREEN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile == 1:
                    pygame.draw.rect(self.screen, DARK_GREEN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile == 2:
                    pygame.draw.rect(self.screen, BROWN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile == 3:
                    pygame.draw.rect(self.screen, BLUE, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile == 4:
                    pygame.draw.rect(self.screen, GRAY, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

        # Render items in current room
        for item in self.items:
            if not item.picked_up and item.room_id == self.current_room_id:
                sprite = self.sprite_gen.create_item_sprite(item.color)
                self.screen.blit(sprite, (item.x - 8, item.y - 8))
                text = self.small_font.render(item.name, True, WHITE)
                self.screen.blit(text, (item.x - text.get_width()//2, item.y - 20))

        # Render exit indicators using exit_positions
        for exit_name in room.exits.keys():
            exit_pos = room.exit_positions.get(exit_name)
            if exit_pos:
                exit_x = exit_pos[0] * TILE_SIZE
                exit_y = exit_pos[1] * TILE_SIZE
                pygame.draw.rect(self.screen, ORANGE, (exit_x - 16, exit_y - 16, 32, 32), 3)
                exit_text = self.small_font.render(exit_name, True, ORANGE)
                self.screen.blit(exit_text, (exit_x - exit_text.get_width()//2, exit_y - 35))

        # Render interactive objects
        if self.current_room_id == "cabin":
            # Fireplace
            fireplace_x, fireplace_y = 3 * TILE_SIZE, 3 * TILE_SIZE
            fireplace_lit = room.properties.get("fireplace_lit", False)
            fireplace_color = ORANGE if fireplace_lit else GRAY
            pygame.draw.rect(self.screen, fireplace_color, (fireplace_x - 16, fireplace_y - 16, 32, 32))
            pygame.draw.rect(self.screen, RED if fireplace_lit else DARK_GREEN, (fireplace_x - 12, fireplace_y - 12, 24, 24))
            if fireplace_lit:
                # Draw flames
                for i in range(3):
                    flame_x = fireplace_x - 8 + i * 8
                    flame_y = fireplace_y - 20
                    pygame.draw.circle(self.screen, YELLOW, (flame_x, flame_y), 4)

        if self.current_room_id == "cave_chamber":
            # Coffin
            coffin_x, coffin_y = 10 * TILE_SIZE, 7 * TILE_SIZE
            coffin_opened = room.properties.get("coffin_opened", False)
            pygame.draw.rect(self.screen, BROWN, (coffin_x - 24, coffin_y - 12, 48, 24))
            if coffin_opened:
                pygame.draw.rect(self.screen, YELLOW, (coffin_x - 20, coffin_y - 8, 40, 16))
            else:
                pygame.draw.line(self.screen, BLACK, (coffin_x - 24, coffin_y), (coffin_x + 24, coffin_y), 2)

        # Render NPCs in current room
        for npc in self.npcs:
            if npc.room_id == self.current_room_id:
                sprite = self.sprite_gen.create_npc_sprite()
                self.screen.blit(sprite, (npc.x - 12, npc.y - 12))
                text = self.small_font.render(npc.name, True, WHITE)
                self.screen.blit(text, (npc.x - text.get_width()//2, npc.y - 30))

        # Render monsters in current room
        for monster in self.monsters:
            if monster["room_id"] == self.current_room_id and not monster["defeated"]:
                # Draw monster body
                pygame.draw.rect(self.screen, monster["color"], 
                               (monster["x"] - 16, monster["y"] - 16, 32, 32))
                pygame.draw.rect(self.screen, RED, 
                               (monster["x"] - 16, monster["y"] - 16, 32, 32), 2)
                
                # Health bar
                hp_ratio = monster["health"] / monster["max_health"]
                bar_width = 40
                pygame.draw.rect(self.screen, RED, (monster["x"] - 20, monster["y"] - 28, bar_width, 6))
                pygame.draw.rect(self.screen, GREEN, (monster["x"] - 20, monster["y"] - 28, int(bar_width * hp_ratio), 6))
                
                # Monster name
                text = self.small_font.render(monster["name"], True, RED)
                self.screen.blit(text, (monster["x"] - text.get_width()//2, monster["y"] - 40))

        # Render player
        player_sprite = self.sprite_gen.create_player_sprite(self.player.direction, self.player.animation_frame)
        self.screen.blit(player_sprite, (self.player.x - 12, self.player.y - 12))

        self._render_ui()
        pygame.display.flip()

    def _render_ui(self):
        room = self.rooms[self.current_room_id]

        # Enhanced status bar with more info
        status_text = f"{room.name} | HP: {self.player.health}/{self.player.max_health} | Lv.{self.player.level} | EXP: {self.player.exp} | 金币: {self.player.gold} | 物品: {len(self.player.inventory)}"
        status = self.font.render(status_text, True, YELLOW)
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 35))
        self.screen.blit(status, (10, 5))

        # Updated controls with correct key bindings
        controls = self.small_font.render("WASD:移动 F:交互 E:攻击 I:物品 R:合成 Q:任务 H:成就 ESC:退出", True, WHITE)
        self.screen.blit(controls, (10, SCREEN_HEIGHT - 25))

        # Win condition
        if self.game_won:
            win_text = self.title_font.render("恭喜！你找到了宝藏！", True, YELLOW)
            self.screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2 - 50))

        # Inventory
        if self.show_inventory:
            self._render_panel("物品栏", self.player.inventory if self.player.inventory else ["物品栏是空的"])

        # Achievements
        if self.show_achievements:
            ach_list = [f"{'✓' if a.unlocked else '○'} {a.name}" for a in self.achievements]
            self._render_panel("成就", ach_list)

        # Crafting
        if self.show_crafting:
            recipe_list = [f"{r.name}: {' + '.join(r.materials)}" for r in self.recipes]
            self._render_panel("合成配方", recipe_list)

        # Quests
        if self.show_quests:
            quest_list = [f"{'✓' if q.completed else '○'} {q.name}" for q in self.quests]
            self._render_panel("任务", quest_list)

        # Dialogue
        if self.show_dialogue:
            s = pygame.Surface((800, 200), pygame.SRCALPHA)
            s.fill((0, 0, 0, 220))
            self.screen.blit(s, (SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT - 250))
            npc_name = self.dialogue_npc.name if self.dialogue_npc else ""
            name = self.font.render(npc_name, True, YELLOW)
            self.screen.blit(name, (SCREEN_WIDTH//2 - 380, SCREEN_HEIGHT - 235))
            y_offset = SCREEN_HEIGHT - 200
            for line in self.dialogue_text.split('\n'):
                text = self.font.render(line, True, WHITE)
                self.screen.blit(text, (SCREEN_WIDTH//2 - 380, y_offset))
                y_offset += 30

        # Nearby item hint
        self._check_nearby_item()
        if self.nearby_item:
            hint = self.font.render(f"按 F 拾取 {self.nearby_item.name}", True, YELLOW)
            self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 50))

        # Interactive object hints
        if self.current_room_id == "cabin":
            fireplace_x, fireplace_y = 3 * TILE_SIZE, 3 * TILE_SIZE
            dist = ((self.player.x - fireplace_x) ** 2 + (self.player.y - fireplace_y) ** 2) ** 0.5
            if dist < 80 and "火把" in self.player.inventory and not room.properties.get("fireplace_lit"):
                hint = self.font.render("按 F 点燃火把", True, ORANGE)
                self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 50))

        if self.current_room_id == "cave_chamber":
            coffin_x, coffin_y = 10 * TILE_SIZE, 7 * TILE_SIZE
            dist = ((self.player.x - coffin_x) ** 2 + (self.player.y - coffin_y) ** 2) ** 0.5
            if dist < 80 and "撬棍" in self.player.inventory and not room.properties.get("coffin_opened"):
                hint = self.font.render("按 F 打开棺材", True, ORANGE)
                self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 50))

        # Feedback message
        if self.feedback_timer > 0:
            feedback = self.font.render(self.feedback_message, True, YELLOW)
            pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH//2 - feedback.get_width()//2 - 10, 100, feedback.get_width() + 20, 40))
            self.screen.blit(feedback, (SCREEN_WIDTH//2 - feedback.get_width()//2, 110))

    def _render_panel(self, title: str, items: List[str]):
        s = pygame.Surface((400, 400), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 200))
        title_text = self.title_font.render(title, True, YELLOW)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 180))
        y_offset = SCREEN_HEIGHT//2 - 120
        for item in items[:10]:
            text = self.font.render(f"• {item}", True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 150, y_offset))
            y_offset += 30

    def run(self):
        while self.running:
            self.handle_input()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game2DEnhanced()
    game.run()
