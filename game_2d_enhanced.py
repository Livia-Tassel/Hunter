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
    exits: Dict[str, Tuple[str, int, int]] = field(default_factory=dict)
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

        self.player = Player(x=320, y=320)
        self.camera_x = 0
        self.camera_y = 0

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

        self.rooms = self._create_rooms()
        self.current_room_id = "cabin"
        self.items = self._create_items()
        self.npcs = self._create_npcs()

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

    def _create_rooms(self) -> Dict[str, GameRoom]:
        rooms = {}

        # Cabin - 20x15 tiles
        cabin_tiles = [[2 if (x > 0 and x < 19 and y > 0 and y < 14) else 1 for x in range(20)] for y in range(15)]
        rooms["cabin"] = GameRoom("cabin", "废弃小屋", cabin_tiles, 10, 7,
            {"北": ("forest_path", 10, 13), "东": ("dark_cellar_entrance", 18, 7)},
            {"fireplace_lit": False, "table_searched": False})

        # Forest Path - 20x15 tiles
        forest_tiles = [[0 if (x + y) % 5 != 0 else 1 for x in range(20)] for y in range(15)]
        rooms["forest_path"] = GameRoom("forest_path", "森林小径", forest_tiles, 10, 13,
            {"南": ("cabin", 10, 1), "北": ("deep_forest", 10, 13)},
            {"leaves_searched": False})

        # Dark Cellar Entrance - 20x15 tiles
        cellar_ent_tiles = [[2 if x > 0 and x < 19 and y > 0 and y < 14 else 1 for x in range(20)] for y in range(15)]
        rooms["dark_cellar_entrance"] = GameRoom("dark_cellar_entrance", "地下室入口", cellar_ent_tiles, 2, 7,
            {"西": ("cabin", 1, 7), "下": ("cellar", 10, 1)},
            {"door_locked": True, "requires_light": True})

        # Cellar - 20x15 tiles
        cellar_tiles = [[4 for x in range(20)] for y in range(15)]
        rooms["cellar"] = GameRoom("cellar", "阴暗的地下室", cellar_tiles, 10, 1,
            {"上": ("dark_cellar_entrance", 10, 13)},
            {"crates_searched": False})

        # Deep Forest - 20x15 tiles
        deep_forest_tiles = [[0 if (x * y) % 7 != 0 else 1 for x in range(20)] for y in range(15)]
        rooms["deep_forest"] = GameRoom("deep_forest", "森林深处", deep_forest_tiles, 10, 13,
            {"南": ("forest_path", 10, 1), "进入洞穴": ("cave_entrance", 10, 7)},
            {"cave_hidden": False})

        # Cave Entrance - 20x15 tiles
        cave_ent_tiles = [[4 if x > 2 and x < 17 and y > 2 and y < 12 else 1 for x in range(20)] for y in range(15)]
        rooms["cave_entrance"] = GameRoom("cave_entrance", "洞穴入口", cave_ent_tiles, 10, 7,
            {"离开洞穴": ("deep_forest", 10, 7), "深入": ("cave_chamber", 2, 7)},
            {"symbols_deciphered": False})

        # Cave Chamber - 20x15 tiles
        cave_chamber_tiles = [[4 for x in range(20)] for y in range(15)]
        rooms["cave_chamber"] = GameRoom("cave_chamber", "洞穴密室", cave_chamber_tiles, 2, 7,
            {"离开": ("cave_entrance", 18, 7)},
            {"coffin_opened": False, "treasure_found": False})

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
        return [NPC(x=5*TILE_SIZE, y=5*TILE_SIZE, name="斗桨先生", color=BLUE, dialogue=dialogue)]

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

        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2

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
                elif event.key == pygame.K_a:
                    self.show_achievements = not self.show_achievements
                    self.show_inventory = False
                    self.show_crafting = False
                    self.show_quests = False
                elif event.key == pygame.K_c:
                    self.show_crafting = not self.show_crafting
                    self.show_inventory = False
                    self.show_achievements = False
                    self.show_quests = False
                elif event.key == pygame.K_q:
                    self.show_quests = not self.show_quests
                    self.show_inventory = False
                    self.show_achievements = False
                    self.show_crafting = False
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
        room = self.rooms[self.current_room_id]
        tile_x = int(self.player.x // TILE_SIZE)
        tile_y = int(self.player.y // TILE_SIZE)

        for exit_name, (next_room, spawn_x, spawn_y) in room.exits.items():
            if abs(tile_x - spawn_x) < 2 and abs(tile_y - spawn_y) < 2:
                if next_room == "cellar" and room.properties.get("door_locked"):
                    if "生锈的钥匙" in self.player.inventory:
                        room.properties["door_locked"] = False
                        self.player.inventory.remove("生锈的钥匙")
                    else:
                        continue
                if next_room == "cellar" and room.properties.get("requires_light"):
                    if "火把" not in self.player.inventory:
                        continue
                self.current_room_id = next_room
                self.player.x = spawn_x * TILE_SIZE
                self.player.y = spawn_y * TILE_SIZE
                self.screen.fill(BLACK)
                pygame.display.flip()
                break

    def _handle_f_key(self):
        room = self.rooms[self.current_room_id]

        # Fireplace interaction
        if self.current_room_id == "cabin" and "火把" in self.player.inventory:
            if not room.properties.get("fireplace_lit"):
                room.properties["fireplace_lit"] = True
                self.player.inventory.remove("火把")
                self.player.inventory.append("点燃的火把")
                return

        # Coffin interaction
        if self.current_room_id == "cave_chamber" and "撬棍" in self.player.inventory:
            if not room.properties.get("coffin_opened"):
                room.properties["coffin_opened"] = True
                if "远古神像" in self.player.inventory:
                    self.game_won = True
                return

        # Item pickup
        for item in self.items:
            if not item.picked_up:
                dist = ((self.player.x - item.x) ** 2 + (self.player.y - item.y) ** 2) ** 0.5
                if dist < 50:
                    item.picked_up = True
                    self.player.inventory.append(item.name)
                    self._check_achievements()
                    self._check_quests()
                    return

        # NPC dialogue
        for npc in self.npcs:
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

    def _check_nearby_item(self):
        self.nearby_item = None
        for item in self.items:
            if not item.picked_up:
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

        # Render exit indicators
        for exit_name, (next_room, spawn_x, spawn_y) in room.exits.items():
            exit_x = spawn_x * TILE_SIZE
            exit_y = spawn_y * TILE_SIZE
            pygame.draw.rect(self.screen, ORANGE, (exit_x - 16, exit_y - 16, 32, 32), 3)
            exit_text = self.small_font.render(exit_name, True, ORANGE)
            self.screen.blit(exit_text, (exit_x - exit_text.get_width()//2, exit_y - 35))

        # Render NPCs in current room
        if self.current_room_id == "cabin":
            for npc in self.npcs:
                sprite = self.sprite_gen.create_npc_sprite()
                self.screen.blit(sprite, (npc.x - 12, npc.y - 12))
                text = self.small_font.render(npc.name, True, WHITE)
                self.screen.blit(text, (npc.x - text.get_width()//2, npc.y - 30))

        # Render player
        player_sprite = self.sprite_gen.create_player_sprite(self.player.direction, self.player.animation_frame)
        self.screen.blit(player_sprite, (self.player.x - 12, self.player.y - 12))

        self._render_ui()
        pygame.display.flip()

    def _render_ui(self):
        room = self.rooms[self.current_room_id]

        # Status bar
        status_text = f"{room.name} | HP: {self.player.health}/{self.player.max_health} | Items: {len(self.player.inventory)}"
        status = self.font.render(status_text, True, YELLOW)
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 35))
        self.screen.blit(status, (10, 5))

        # Controls
        controls = self.small_font.render("WASD:移动 F:交互 I:物品 C:合成 Q:任务 A:成就 ESC:退出", True, WHITE)
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
