"""Test script to check Chinese font support in pygame"""
import pygame
pygame.init()

print("Testing Chinese font support...\n")

# Test different font loading methods
test_fonts = [
    'PingFang SC',
    'Heiti SC',
    'STHeiti',
    'Arial Unicode MS',
    'SimHei',
    'Microsoft YaHei'
]

print("Available system fonts:")
available_fonts = pygame.font.get_fonts()
chinese_fonts = [f for f in available_fonts if any(x in f.lower() for x in ['ping', 'hei', 'song', 'kai', 'yuan', 'fang', 'microsoft', 'sim'])]
for font in chinese_fonts[:10]:
    print(f"  - {font}")

print("\nTesting font loading:")
for font_name in test_fonts:
    try:
        font = pygame.font.SysFont(font_name, 24)
        print(f"✓ {font_name}: {font.get_name()}")
    except Exception as e:
        print(f"✗ {font_name}: {e}")

print("\nTesting Chinese character rendering:")
test_text = "物品栏 成就 任务"
for font_name in test_fonts:
    try:
        font = pygame.font.SysFont(font_name, 24)
        surface = font.render(test_text, True, (255, 255, 255))
        print(f"✓ {font_name}: Can render '{test_text}' ({surface.get_width()}px wide)")
    except Exception as e:
        print(f"✗ {font_name}: {e}")

pygame.quit()
