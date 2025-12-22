"""Main entry point for The Lost Treasure Hunter game"""
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game_engine import GameEngine

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "saving")
    os.makedirs(save_dir, exist_ok=True)

    save_file = os.path.join(save_dir, "adventure_save.json")
    sounds_dir = os.path.join(script_dir, "sounds")

    game = GameEngine(save_file, sounds_dir)
    game.start_game()

if __name__ == "__main__":
    main()
