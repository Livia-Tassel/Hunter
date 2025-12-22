# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"迷失的宝藏猎人 (The Lost Treasure Hunter)" is a Chinese-language text adventure game built in Python. It's a single-file interactive fiction game featuring room exploration, item management, NPC dialogue, puzzle solving, and optional audio/TTS features.

## Running the Game

```bash
python3 "The Lost Treasure Hunter.py"
```

The game requires Python 3 and optionally pygame for sound effects:
```bash
pip install pygame
```

## Game Architecture

### Core Classes

- **Game**: Main game controller managing world state, command processing, and game loop
- **Player**: Tracks inventory, health, current location, and game history
- **Room**: Represents locations with items, NPCs, exits, properties, and ambient sounds
- **Item**: Game objects with use mechanics and ASCII art
- **NPC**: Non-player characters with dialogue trees and optional TTS voices

### Key Game Systems

**Command Processing** (line 533-598): Text parser handles natural language commands like "go 北", "use 火把 on 壁炉", "talk to 斗桨先生 about 宝藏", "unlock 门 with 生锈的钥匙"

**Save/Load System** (lines 845-872): JSON-based persistence in `saving/adventure_save.json` stores player state, inventory, room states, and puzzle progress

**Puzzle State Management**: Room properties track puzzle states (e.g., `fireplace_lit`, `door_locked`, `coffin_opened`). Puzzles are solved through item interactions and state changes.

**Audio System** (lines 26-43, 190-232): Optional pygame mixer for ambient sounds and effects. Falls back to terminal beeps if pygame unavailable. Ambient sounds loop per-room on channel 0.

**TTS Integration** (lines 251-273): macOS-specific `say` command for NPC dialogue using Chinese voices (e.g., "Ting-Ting")

### World Structure

The game world consists of interconnected rooms:
- **cabin**: Starting location with fireplace puzzle and NPC "斗桨先生"
- **forest_path**: Contains hidden key in leaves
- **dark_cellar_entrance**: Locked door requiring key and light source
- **cellar**: Contains crowbar and ancient statue
- **deep_forest**: Hidden cave entrance revealed on visit
- **cave_entrance**: Contains dusty book
- **cave_chamber**: Final treasure room with coffin puzzle

Win condition (line 874-880): Player must be in cave_chamber with ancient statue in inventory and coffin opened.

## Development Commands

**Run the game:**
```bash
python3 "The Lost Treasure Hunter.py"
```

**Test autoplay (automated walkthrough):**
```bash
# The game will read commands from saving/walkthrough.txt
# In-game command: autoplay walkthrough.txt
```

**Check save file location:**
```bash
cat "saving/adventure_save.json"
```

## Important Implementation Details

**File Paths**: The game dynamically constructs paths using `__file__` and creates a `saving/` directory for save files (lines 169-185). All file operations should maintain this structure.

**Color System**: ANSI escape codes defined in Colors class (lines 10-19). Use `c_text()` helper for colored output.

**Chinese Language**: All game text, commands, and dialogue are in Chinese. Room names use English internally but display Chinese. Direction commands are in Chinese (北/南/东/西/上/下).

**Item Interaction Pattern**: Items have `use_on` targets and `effect_description`. Special items (火把, 撬棍, 生锈的钥匙) have hardcoded interaction logic in `use_item()` and `unlock_target_with_item()`.

**Room Properties**: Rooms use a flexible `properties` dict for puzzle state. Always check and update properties when implementing new puzzles.

**NPC Dialogue**: Stored in nested dicts with topic keys. The NPC "斗桨先生" has extensive dialogue including world lore, hints, and a special "星辰的低语" topic mentioning "张本意涵" (line 413).

**ASCII Art**: Defined in ASCII_ARTS dict (lines 49-151). Art is displayed on examine or room entry. Some art changes based on state (fireplace_lit vs fireplace_cold).

## Code Conventions

- Chinese variable names in strings, English in code identifiers
- Properties stored as dicts, not hardcoded attributes
- Sound effects are optional - always check SOUND_ENABLED
- Use `display_message()` for all user-facing text with color/sound parameters
- Command parsing uses lowercase normalization and space-split tokenization
- Room exits use Chinese direction names as keys
