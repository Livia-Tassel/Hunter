"""Quick test to find working Chinese font"""
import pygame
pygame.init()

print("Testing font loading methods...\n")

# Method 1: Try match_font
print("Method 1: pygame.font.match_font()")
for font_name in ['PingFang SC', 'PingFangSC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS']:
    matched = pygame.font.match_font(font_name)
    print(f"  {font_name}: {matched}")

# Method 2: Try get_fonts and find Chinese ones
print("\nMethod 2: Available fonts with Chinese support")
all_fonts = pygame.font.get_fonts()
chinese_keywords = ['ping', 'fang', 'hei', 'song', 'kai', 'yuan', 'sti', 'st']
chinese_fonts = [f for f in all_fonts if any(k in f.lower() for k in chinese_keywords)]
print(f"Found {len(chinese_fonts)} potential Chinese fonts:")
for f in chinese_fonts[:15]:
    print(f"  - {f}")

# Method 3: Test actual rendering
print("\nMethod 3: Test actual rendering")
test_text = "测试中文"
for font_name in chinese_fonts[:5]:
    try:
        font = pygame.font.SysFont(font_name, 24)
        surface = font.render(test_text, True, (255, 255, 255))
        # Check if it's actually rendering (not just boxes)
        # Boxes typically have consistent width
        char_width = surface.get_width() / len(test_text)
        print(f"  {font_name}: width={surface.get_width()}px, per char={char_width:.1f}px")
    except Exception as e:
        print(f"  {font_name}: ERROR - {e}")

pygame.quit()
