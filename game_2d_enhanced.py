"""Enhanced 2D Graphical Game with Pixel Art, Animations, Achievements, Crafting, Quests"""
import pygame
import sys
import random
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
    picked_up: bool = False

@dataclass
class NPC:
    x: float
    y: float
    name: str
    color: Tuple[int, int, int]
    dialogue: str

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

        self.player = Player(x=400, y=300)
        self.camera_x = 0
        self.camera_y = 0

        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)

        self.tiles = self._create_world()
        self.items = self._create_items()
        self.npcs = self._create_npcs()

        self.achievements = self._init_achievements()
        self.quests = self._init_quests()
        self.recipes = self._init_recipes()

        self.show_dialogue = False
        self.dialogue_text = ""
        self.dialogue_npc = ""
        self.show_inventory = False
        self.show_achievements = False
        self.show_crafting = False
        self.show_quests = False
        self.nearby_item = None

        self.sprite_gen = SpriteGenerator()

    def _create_world(self) -> List[List[int]]:
        world = []
        for y in range(50):
            row = []
            for x in range(60):
                # Cabin (15-25, 10-18)
                if 15 <= x <= 25 and 10 <= y <= 18:
                    if x == 15 or x == 25 or y == 10 or y == 18:
                        row.append(1)
                    else:
                        row.append(2)
                # Cave area (40-50, 30-40)
                elif 40 <= x <= 50 and 30 <= y <= 40:
                    if x == 40 or x == 50 or y == 30 or y == 40:
                        row.append(1)
                    else:
                        row.append(4)  # Cave floor
                # Forest
                elif (x + y) % 7 == 0 or (x * 2 + y) % 11 == 0:
                    row.append(1)
                # Water
                elif y > 45:
                    row.append(3)
                else:
                    row.append(0)
            world.append(row)
        return world

    def _create_items(self) -> List[Item]:
        return [
            Item(x=20*TILE_SIZE, y=14*TILE_SIZE, name="火把", color=YELLOW),
            Item(x=22*TILE_SIZE, y=14*TILE_SIZE, name="古老的地图", color=BROWN),
            Item(x=18*TILE_SIZE, y=16*TILE_SIZE, name="生锈的钥匙", color=GRAY),
            Item(x=10*TILE_SIZE, y=8*TILE_SIZE, name="治疗药水", color=RED),
            Item(x=45*TILE_SIZE, y=35*TILE_SIZE, name="远古神像", color=BLUE),
            Item(x=30*TILE_SIZE, y=25*TILE_SIZE, name="撬棍", color=GRAY),
            Item(x=12*TILE_SIZE, y=20*TILE_SIZE, name="绳子", color=BROWN),
        ]

    def _create_npcs(self) -> List[NPC]:
        return [
            NPC(x=18*TILE_SIZE, y=12*TILE_SIZE, name="斗桨先生", color=BLUE,
                dialogue="年轻人，此地凶险，亦藏机缘。\n按 F 与我对话，WASD 移动，I 物品栏\nC 合成，Q 任务，A 成就"),
            NPC(x=45*TILE_SIZE, y=32*TILE_SIZE, name="神秘商人", color=ORANGE,
                dialogue="我有稀有物品出售...\n但你需要足够的金币。"),
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

    def _check_collision(self, x: float, y: float) -> bool:
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        if 0 <= tile_y < len(self.tiles) and 0 <= tile_x < len(self.tiles[0]):
            return self.tiles[tile_y][tile_x] in [1, 3]
        return True

    def _handle_f_key(self):
        for item in self.items:
            if not item.picked_up:
                dist = ((self.player.x - item.x) ** 2 + (self.player.y - item.y) ** 2) ** 0.5
                if dist < 50:
                    item.picked_up = True
                    self.player.inventory.append(item.name)
                    self._check_achievements()
                    self._check_quests()
                    return

        for npc in self.npcs:
            dist = ((self.player.x - npc.x) ** 2 + (self.player.y - npc.y) ** 2) ** 0.5
            if dist < 50:
                self.show_dialogue = True
                self.dialogue_text = npc.dialogue
                self.dialogue_npc = npc.name
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

        # Render tiles
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y
                if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
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

        # Render items
        for item in self.items:
            if not item.picked_up:
                screen_x = item.x - self.camera_x
                screen_y = item.y - self.camera_y
                sprite = self.sprite_gen.create_item_sprite(item.color)
                self.screen.blit(sprite, (screen_x - 8, screen_y - 8))
                text = self.small_font.render(item.name, True, WHITE)
                self.screen.blit(text, (screen_x - text.get_width()//2, screen_y - 20))

        # Render NPCs
        for npc in self.npcs:
            screen_x = npc.x - self.camera_x
            screen_y = npc.y - self.camera_y
            sprite = self.sprite_gen.create_npc_sprite()
            self.screen.blit(sprite, (screen_x - 12, screen_y - 12))
            text = self.small_font.render(npc.name, True, WHITE)
            self.screen.blit(text, (screen_x - text.get_width()//2, screen_y - 30))

        # Render player
        screen_x = self.player.x - self.camera_x
        screen_y = self.player.y - self.camera_y
        player_sprite = self.sprite_gen.create_player_sprite(self.player.direction, self.player.animation_frame)
        self.screen.blit(player_sprite, (screen_x - 12, screen_y - 12))

        self._render_ui()
        pygame.display.flip()

    def _render_ui(self):
        # Status bar
        status_text = f"HP: {self.player.health}/{self.player.max_health} | Lv.{self.player.level} | Gold: {self.player.gold} | Items: {len(self.player.inventory)}"
        status = self.font.render(status_text, True, YELLOW)
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 35))
        self.screen.blit(status, (10, 5))

        # Controls
        controls = self.small_font.render("WASD:移动 F:交互 I:物品 C:合成 Q:任务 A:成就 ESC:退出", True, WHITE)
        self.screen.blit(controls, (10, SCREEN_HEIGHT - 25))

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
            name = self.font.render(self.dialogue_npc, True, YELLOW)
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
