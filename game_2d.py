"""2D Graphical version of The Lost Treasure Hunter - Stardew Valley style"""
import pygame
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Initialize Pygame
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

@dataclass
class Player:
    x: float
    y: float
    speed: float = 3.0
    inventory: List[str] = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

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

class Game2D:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("迷失的宝藏猎人 - The Lost Treasure Hunter")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.player = Player(x=400, y=300)
        self.camera_x = 0
        self.camera_y = 0

        # Font
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)

        # Game world
        self.tiles = self._create_world()
        self.items = self._create_items()
        self.npcs = self._create_npcs()

        # UI state
        self.show_dialogue = False
        self.dialogue_text = ""
        self.dialogue_npc = ""
        self.show_inventory = False
        self.nearby_item = None

    def _create_world(self) -> List[List[int]]:
        """Create tile-based world map. 0=grass, 1=wall, 2=floor, 3=water"""
        # Simple cabin and forest area
        world = []
        for y in range(30):
            row = []
            for x in range(40):
                # Cabin area (center)
                if 15 <= x <= 25 and 10 <= y <= 18:
                    if x == 15 or x == 25 or y == 10 or y == 18:
                        row.append(1)  # Walls
                    else:
                        row.append(2)  # Floor
                # Forest area
                elif (x + y) % 7 == 0:
                    row.append(1)  # Trees
                # Water area (bottom)
                elif y > 25:
                    row.append(3)  # Water
                else:
                    row.append(0)  # Grass
            world.append(row)
        return world

    def _create_items(self) -> List[Item]:
        """Create items in the world"""
        return [
            Item(x=20*TILE_SIZE, y=14*TILE_SIZE, name="火把", color=YELLOW),
            Item(x=22*TILE_SIZE, y=14*TILE_SIZE, name="古老的地图", color=BROWN),
            Item(x=18*TILE_SIZE, y=16*TILE_SIZE, name="生锈的钥匙", color=GRAY),
            Item(x=10*TILE_SIZE, y=8*TILE_SIZE, name="治疗药水", color=RED),
            Item(x=30*TILE_SIZE, y=20*TILE_SIZE, name="远古神像", color=BLUE),
        ]

    def _create_npcs(self) -> List[NPC]:
        """Create NPCs in the world"""
        return [
            NPC(x=18*TILE_SIZE, y=12*TILE_SIZE, name="斗桨先生", color=BLUE,
                dialogue="年轻人，此地凶险，亦藏机缘。心有所向，不妨一问。\n按 F 键与我对话，WASD 移动，F 键拾取物品。"),
        ]

    def handle_input(self):
        """Handle keyboard and mouse input"""
        keys = pygame.key.get_pressed()

        # WASD movement
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.player.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.player.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.player.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.player.speed

        # Move player with collision detection
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if not self._check_collision(new_x, new_y):
            self.player.x = new_x
            self.player.y = new_y

        # Update camera to follow player
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2

        # Event handling
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
                elif event.key == pygame.K_SPACE:
                    self.show_dialogue = False

    def _check_collision(self, x: float, y: float) -> bool:
        """Check if position collides with walls"""
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)

        if 0 <= tile_y < len(self.tiles) and 0 <= tile_x < len(self.tiles[0]):
            return self.tiles[tile_y][tile_x] in [1, 3]  # Wall or water
        return True

    def _handle_f_key(self):
        """Handle F key press for interactions"""
        # Check for nearby items
        for item in self.items:
            if not item.picked_up:
                dist = ((self.player.x - item.x) ** 2 + (self.player.y - item.y) ** 2) ** 0.5
                if dist < 50:
                    item.picked_up = True
                    self.player.inventory.append(item.name)
                    return

        # Check for nearby NPCs
        for npc in self.npcs:
            dist = ((self.player.x - npc.x) ** 2 + (self.player.y - npc.y) ** 2) ** 0.5
            if dist < 50:
                self.show_dialogue = True
                self.dialogue_text = npc.dialogue
                self.dialogue_npc = npc.name
                return

    def _check_nearby_item(self):
        """Check if player is near an item"""
        self.nearby_item = None
        for item in self.items:
            if not item.picked_up:
                dist = ((self.player.x - item.x) ** 2 + (self.player.y - item.y) ** 2) ** 0.5
                if dist < 50:
                    self.nearby_item = item
                    return

    def render(self):
        """Render the game"""
        self.screen.fill(BLACK)

        # Render tiles
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y

                if -TILE_SIZE < screen_x < SCREEN_WIDTH and -TILE_SIZE < screen_y < SCREEN_HEIGHT:
                    if tile == 0:  # Grass
                        pygame.draw.rect(self.screen, GREEN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif tile == 1:  # Wall/Tree
                        pygame.draw.rect(self.screen, DARK_GREEN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif tile == 2:  # Floor
                        pygame.draw.rect(self.screen, BROWN, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif tile == 3:  # Water
                        pygame.draw.rect(self.screen, BLUE, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

        # Render items
        for item in self.items:
            if not item.picked_up:
                screen_x = item.x - self.camera_x
                screen_y = item.y - self.camera_y
                pygame.draw.circle(self.screen, item.color, (int(screen_x), int(screen_y)), 8)
                # Item name
                text = self.font.render(item.name, True, WHITE)
                self.screen.blit(text, (screen_x - text.get_width()//2, screen_y - 20))

        # Render NPCs
        for npc in self.npcs:
            screen_x = npc.x - self.camera_x
            screen_y = npc.y - self.camera_y
            pygame.draw.rect(self.screen, npc.color, (screen_x - 12, screen_y - 12, 24, 24))
            # NPC name
            text = self.font.render(npc.name, True, WHITE)
            self.screen.blit(text, (screen_x - text.get_width()//2, screen_y - 30))

        # Render player
        screen_x = self.player.x - self.camera_x
        screen_y = self.player.y - self.camera_y
        pygame.draw.circle(self.screen, RED, (int(screen_x), int(screen_y)), 12)

        # Render UI
        self._render_ui()

        pygame.display.flip()

    def _render_ui(self):
        """Render UI elements"""
        # Inventory display
        if self.show_inventory:
            # Semi-transparent background
            s = pygame.Surface((400, 300))
            s.set_alpha(200)
            s.fill(BLACK)
            self.screen.blit(s, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150))

            # Title
            title = self.title_font.render("物品栏", True, YELLOW)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 130))

            # Items
            y_offset = SCREEN_HEIGHT//2 - 80
            if self.player.inventory:
                for item in self.player.inventory:
                    text = self.font.render(f"• {item}", True, WHITE)
                    self.screen.blit(text, (SCREEN_WIDTH//2 - 150, y_offset))
                    y_offset += 30
            else:
                text = self.font.render("物品栏是空的", True, GRAY)
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))

            # Close hint
            hint = self.font.render("按 I 关闭", True, GRAY)
            self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT//2 + 100))

        # Dialogue box
        if self.show_dialogue:
            # Semi-transparent background
            s = pygame.Surface((800, 200))
            s.set_alpha(220)
            s.fill(BLACK)
            self.screen.blit(s, (SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT - 250))

            # NPC name
            name = self.font.render(self.dialogue_npc, True, YELLOW)
            self.screen.blit(name, (SCREEN_WIDTH//2 - 380, SCREEN_HEIGHT - 235))

            # Dialogue text (word wrap)
            y_offset = SCREEN_HEIGHT - 200
            for line in self.dialogue_text.split('\n'):
                text = self.font.render(line, True, WHITE)
                self.screen.blit(text, (SCREEN_WIDTH//2 - 380, y_offset))
                y_offset += 30

            # Close hint
            hint = self.font.render("按 空格 关闭", True, GRAY)
            self.screen.blit(hint, (SCREEN_WIDTH//2 + 300, SCREEN_HEIGHT - 80))

        # Check nearby item
        self._check_nearby_item()
        if self.nearby_item:
            hint = self.font.render(f"按 F 拾取 {self.nearby_item.name}", True, YELLOW)
            self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 50))

        # Controls hint
        controls = self.font.render("WASD: 移动 | F: 交互/拾取 | I: 物品栏 | ESC: 退出", True, WHITE)
        self.screen.blit(controls, (10, SCREEN_HEIGHT - 30))

        # Inventory count
        inv_text = self.font.render(f"物品: {len(self.player.inventory)}", True, YELLOW)
        self.screen.blit(inv_text, (SCREEN_WIDTH - 150, 10))

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_input()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game2D()
    game.run()
