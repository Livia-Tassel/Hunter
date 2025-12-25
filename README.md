# The Lost Treasure Hunter - Reconstructed

## Overview

This is a fully reconstructed version of "迷失的宝藏猎人 (The Lost Treasure Hunter)" - a Chinese-language text adventure game with enhanced terminal UI, modular architecture, and additional gameplay features.

## What's New

### Enhanced Terminal UI
- Beautiful terminal interface using the `rich` library
- Panels and borders for better visual organization
- Color-coded text for different game elements
- Formatted tables for inventory and help menus
- Health bars and combat displays

### Modular Architecture
```
src/
├── core/           # Core game entities (Player, NPC, Item, Room)
├── ui/             # Terminal UI system with rich
├── systems/        # Game systems (audio, combat, quests, save/load)
├── content/        # Game data (items, rooms, NPCs, ASCII art)
└── game_engine.py  # Main game engine
```

### New Gameplay Features
- **Enhanced Combat System**: Turn-based combat with damage calculation
- **Quest System**: Track objectives and earn rewards
- **Character Stats**: Strength, intelligence, defense attributes
- **Experience & Leveling**: Gain experience and level up
- **Better Inventory Management**: Categorized items with detailed display

## Installation

### Using Virtual Environment (Recommended)

```bash
# The virtual environment is already set up
source venv/bin/activate

# Dependencies are already installed:
# - rich (terminal UI)
# - pygame (audio system)
```

## Running the Game

```bash
# Activate virtual environment
source venv/bin/activate

# Run the new modular version
python main.py

# Or run the original version
python "The Lost Treasure Hunter.py"
```

## Project Structure

### Core Modules

**src/core/entities.py**
- `Item`: Game items with properties and effects
- `Room`: Locations with exits, items, NPCs
- `NPC`: Non-player characters with dialogue
- `Player`: Player character with stats and inventory

**src/ui/terminal_ui.py**
- `GameUI`: Enhanced terminal interface using rich
- Formatted displays for rooms, inventory, combat, dialogue

**src/systems/audio.py**
- `AudioSystem`: Sound effects and ambient audio
- macOS TTS integration for NPC dialogue

**src/systems/game_state.py**
- `GameState`: Save/load game progress
- JSON-based persistence

**src/systems/combat.py**
- `CombatSystem`: Turn-based combat mechanics
- `QuestSystem`: Quest tracking and completion

**src/content/game_data.py**
- All game content (items, rooms, NPCs)
- ASCII art definitions

**src/game_engine.py**
- Main game loop and command processing
- Integration of all systems

## Game Commands

All original commands are preserved:
- `go [方向]` - Move in a direction
- `look / l` - Look around
- `examine [目标]` - Examine something
- `take [物品]` - Take an item
- `use [物品] (on [目标])` - Use an item
- `talk to [NPC] (about [话题])` - Talk to NPC
- `inventory / i` - View inventory
- `save / load` - Save/load game
- `help` - Show help
- `quit` - Quit game

New commands:
- `quests` - View active quests

## Features Preserved

All original game features are maintained:
- ✅ All rooms, items, NPCs, and puzzles
- ✅ Chinese language interface
- ✅ Save/load functionality
- ✅ Audio system with pygame
- ✅ macOS TTS for NPC dialogue
- ✅ ASCII art displays
- ✅ Complete game storyline

## Technical Improvements

1. **Modular Design**: Clean separation of concerns
2. **Type Hints**: Better code documentation with dataclasses
3. **Enhanced UI**: Professional terminal interface
4. **Extensible Systems**: Easy to add new features
5. **Better Error Handling**: More robust code
6. **Virtual Environment**: Isolated dependencies

## Development

The game uses a virtual environment to keep dependencies isolated:

```bash
# Activate environment
source venv/bin/activate

# Install new dependencies
pip install package-name

# Deactivate when done
deactivate
```

## Compatibility

- **Python**: 3.7+
- **Platform**: macOS, Linux, Windows
- **Dependencies**: rich, pygame (optional)
- **Original Game**: Fully backward compatible

## Notes

- Save files are compatible between versions
- The original game file is preserved as "The Lost Treasure Hunter.py"
- Audio files should be placed in the `sounds/` directory
- Game saves are stored in `saving/adventure_save.json`

## Automated Testing

The game includes an automated test script that simulates a complete playthrough:

```bash
# Run automated walkthrough test
python test_walkthrough.py

# Verbose mode (show all commands)
python test_walkthrough.py -v

# Custom delay between commands
python test_walkthrough.py -d 0.1
```

The test script:
- Loads commands from `saving/official_walkthrough.txt`
- Executes all game interactions automatically
- Fights all monsters in auto-combat mode
- Verifies the win condition is achieved
- Reports player stats and exploration progress

---

**Reconstructed with modular architecture and enhanced terminal UI**
