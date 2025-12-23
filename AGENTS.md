# Repository Guidelines

## Project Structure & Module Organization
- Gameplay lives in `src/game_engine.py` orchestrating `core` entities, `systems` (audio, combat, quests, achievements, saves), `ui/terminal_ui.py` (rich-based terminal UI), and `content/game_data.py` (rooms, NPCs, items, ASCII art).
- Entry points: `main.py` (modular version) and `"The Lost Treasure Hunter.py"` (original script). Save data lands in `saving/adventure_save.json`; optional audio files reside in `sounds/`.
- Legacy experiments (`game_2d*.py`, `find_font.py`) and font test scripts sit at repo root. Tests and helpers are Python scripts rather than a test runner.

## Build, Test, and Development Commands
- Activate environment: `source venv/bin/activate` (dependencies already installed: `rich`, `pygame`).
- Run modular game: `python main.py`. Original: `python "The Lost Treasure Hunter.py"`.
- Font/render checks: `python test_fonts.py` (headless), `python test_exact.py` (glyph widths), `python test_visual.py` (opens a pygame window; requires display).
- When adding dependencies, pin them and update `venv` via `pip install <pkg>` inside the activated environment.

## Coding Style & Naming Conventions
- Python 3.7+ with 4-space indentation, type hints, and dataclasses (see `src/core/entities.py`). Use `snake_case` for functions/variables and `CapWords` for classes.
- Keep game content strings in Chinese where appropriate; normalize item/room keys to lowercase. Favor `os.path` utilities for file paths and avoid hard-coded absolute paths.
- UI changes should flow through `ui/terminal_ui.py` using `rich`; prefer small, composable helpers over inline prints inside systems.

## Testing Guidelines
- Prefer fast checks first (`python test_fonts.py`); run `test_visual.py` only when a GUI is available. For gameplay changes, smoke-test via `python main.py` to verify movement, inventory, combat, quests, and save/load.
- Add new tests as runnable scripts in the repo root or under `tests/` and document their invocation. Keep save files in `saving/` out of version control when possible.

## Commit & Pull Request Guidelines
- Match existing history: concise, present-tense summaries (e.g., `fix combat reward loop`, `add ambient sound fallbacks`). Keep subjects under ~72 characters and avoid noise prefixes.
- Pull requests should include: scope summary, notable gameplay/UI changes, test commands/output, and any new assets or data files added to `content/` or `sounds/`.
- Link related issues or quests if available. Screenshots or short clips of terminal output are helpful for UI or combat changes; otherwise paste key logs.

## Security & Configuration Tips
- Do not commit generated saves or system-specific font caches. Keep secrets (API keys, OS credentials) out of code and config; audio/voice features rely only on local assets.
- Ensure new data files referenced in `content/game_data.py` exist and paths are relative to the repo root to keep the game portable across OSes.
