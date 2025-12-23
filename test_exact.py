"""Test with exact game code"""
import pygame
pygame.init()

# EXACT code from game
chinese_fonts = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS', 'Arial']
font = pygame.font.SysFont(chinese_fonts, 24)

print(f"Font loaded: {type(font)}")
print(f"Font size: {font.get_height()}")

# Test rendering
test_texts = [
    "物品栏",
    "成就",
    "任务",
    "合成配方",
    "斗桨先生",
    "按 F 拾取"
]

print("\nRendering tests:")
for text in test_texts:
    try:
        surface = font.render(text, True, (255, 255, 255))
        print(f"✓ '{text}': {surface.get_width()}px x {surface.get_height()}px")
        if surface.get_width() == 0:
            print(f"  WARNING: Width is 0! Text not rendering!")
    except Exception as e:
        print(f"✗ '{text}': ERROR - {e}")

# Test with anti-aliasing off
print("\nTest without anti-aliasing:")
surface = font.render("物品栏", False, (255, 255, 255))
print(f"Width: {surface.get_width()}px")

pygame.quit()
