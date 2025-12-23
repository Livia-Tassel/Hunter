"""Visual test - open window and display Chinese text"""
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Chinese Font Test")
clock = pygame.time.Clock()

# Use same font loading as game
chinese_fonts = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS', 'Arial']
font = pygame.font.SysFont(chinese_fonts, 32)
small_font = pygame.font.SysFont(chinese_fonts, 20)

print(f"Font loaded successfully")
print(f"Testing Chinese text rendering...")

# Test texts
test_texts = [
    "物品栏",
    "成就",
    "任务",
    "合成配方",
    "斗桨先生",
    "按 F 拾取 火把"
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((0, 0, 0))

    # Draw title
    title = font.render("Chinese Font Test - 中文字体测试", True, (255, 255, 0))
    screen.blit(title, (50, 50))

    # Draw test texts
    y = 120
    for text in test_texts:
        surface = small_font.render(text, True, (255, 255, 255))
        screen.blit(surface, (50, y))

        # Show dimensions
        info = small_font.render(f"({surface.get_width()}x{surface.get_height()}px)", True, (100, 100, 100))
        screen.blit(info, (300, y))
        y += 40

    # Instructions
    inst = small_font.render("Press ESC to close", True, (200, 200, 200))
    screen.blit(inst, (50, 500))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
