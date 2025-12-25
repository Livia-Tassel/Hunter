"""Main game engine with all enhanced features"""
import os
import random
import time
from typing import Optional, Dict, List
from .core.entities import Player
from .ui.terminal_ui import ui
from .systems.audio import init_audio
from .systems.game_state import GameState
from .systems.combat import CombatSystem, QuestSystem, Quest
from .systems.achievements import AchievementSystem, CraftingSystem, init_crafting_recipes
from .content.game_data import create_items, create_npcs, create_rooms, ASCII_ARTS

class GameEngine:
    def __init__(self, save_dir: str, sounds_dir: str):
        self.save_dir = save_dir
        self.sounds_dir = sounds_dir
        self.audio = init_audio(sounds_dir)
        self.game_state = GameState(save_dir)
        self.combat_system = CombatSystem(self.audio)
        self.quest_system = QuestSystem()
        self.achievement_system = AchievementSystem()
        self.crafting_system = CraftingSystem()
        self.flavor_events = self._init_flavor_events()
        self.intro_quest: Optional[Quest] = None
        self.is_running = True
        self.command_aliases = {
            'n': 'go 北', 's': 'go 南', 'e': 'go 东', 'w': 'go 西',
            't': 'take', 'd': 'drop', 'u': 'use', 'x': 'examine',
        }
        self.hints = self._init_hints()
        self._setup_world()

    def _setup_world(self):
        self.game_state.items = create_items()
        self.game_state.npcs = create_npcs()
        self.game_state.rooms = create_rooms(self.game_state.items, self.game_state.npcs)
        self.game_state.player = Player(current_room_id="cabin")
        starting_room = self.game_state.rooms.get("cabin")
        if starting_room:
            self.game_state.player.visit_room("cabin", starting_room.display_name)
        self._init_intro_quest()
        init_crafting_recipes(self.crafting_system)

    def _init_hints(self) -> Dict[str, List[str]]:
        """Initialize contextual hints for each room"""
        return {
            "cabin": ["尝试检查壁炉和桌子", "和斗桨先生对话了解更多信息", "别忘了拿走有用的物品"],
            "forest_path": ["仔细搜索枯叶堆", "森林深处可能有秘密"],
            "dark_cellar_entrance": ["你需要钥匙和光源", "门可以用钥匙解锁"],
            "cellar": ["搜索木箱可能有惊喜", "神像看起来很重要"],
            "deep_forest": ["仔细观察周围环境", "洞穴入口可能被隐藏了"],
            "cave_entrance": ["洞穴深处可能有宝藏", "注意墙上的符号"],
            "cave_chamber": ["石棺需要工具才能打开", "这里就是最终目标"],
        }

    def _init_flavor_events(self) -> Dict[str, List[str]]:
        """Lightweight flavor events to keep rooms feeling alive"""
        return {
            "forest_path": [
                "一阵风吹过，枯叶沙沙作响，隐约露出斑驳的石板。",
                "远处传来鸟鸣，又很快归于寂静。"
            ],
            "cabin": [
                "尘土从屋梁落下，仿佛在催促你快些行动。",
                "斗桨先生的目光似乎在关注你的举动。"
            ],
            "cave_entrance": [
                "洞壁上的符号仿佛在微微发光，像是在呼吸。",
                "一股凉风拂过，你听到似有若无的回声。"
            ],
            "cave_chamber": [
                "石棺旁的尘埃上有划痕，似乎有人来过。",
                "金币闪着暗淡的光，隐约映出你的身影。"
            ],
        }

    def _init_intro_quest(self):
        """Add quests to guide players through the game"""
        # Main intro quest
        quest = Quest(
            quest_id="intro_path",
            name="重燃火种",
            description="点亮光源并找到地下室的秘密。",
            objectives=["点燃火把", "解锁地下室", "取得远古神像"],
            rewards={"experience": 60, "score": 20}
        )
        self.quest_system.add_quest(quest)
        self.intro_quest = quest

        # Forest exploration quest
        forest_quest = Quest(
            quest_id="forest_explorer",
            name="森林探险者",
            description="探索森林的每一个角落。",
            objectives=["探索森林小径", "进入森林深处", "发现隐藏的洞穴"],
            rewards={"experience": 40, "score": 15, "gold": 50}
        )
        self.quest_system.add_quest(forest_quest)

        # Monster hunter quest
        monster_quest = Quest(
            quest_id="monster_hunter",
            name="怪物猎人",
            description="击败游荡在这片土地上的危险生物。",
            objectives=["击败洞穴蝙蝠", "击败森林狼", "击败骷髅守卫"],
            rewards={"experience": 100, "score": 30, "gold": 100}
        )
        self.quest_system.add_quest(monster_quest)

    def _log_action(self, description: str):
        """Record an action in the player's journal"""
        if self.game_state.player:
            self.game_state.player.record_action(description)

    def _maybe_trigger_flavor_event(self, room):
        """Show occasional flavor text to keep areas lively"""
        events = self.flavor_events.get(room.name, [])
        if events and random.random() < 0.35:
            ui.print_message(random.choice(events), "dim")

    def _update_intro_objective(self, index: int):
        """Mark intro quest progress when applicable"""
        if not self.intro_quest:
            return
        before = self.intro_quest.completed_objectives[index] if 0 <= index < len(self.intro_quest.completed_objectives) else False
        self.intro_quest.complete_objective(index)
        if self.intro_quest.completed_objectives[index] and not before:
            self._log_action(f"任务进度：{self.intro_quest.name} - {self.intro_quest.objectives[index]}")
        if self.intro_quest.is_completed():
            if self.quest_system.complete_quest(self.intro_quest.quest_id, self.game_state.player):
                self._log_action(f"任务完成：{self.intro_quest.name}")

    def start_game(self):
        ui.clear()
        ui.print_header("迷失的宝藏猎人 (The Lost Treasure Hunter)")
        ui.print_message("欢迎来到《迷失的宝藏猎人》！输入 'help' 查看指令。", "green")
        if self.intro_quest:
            ui.print_success(f"新任务：{self.intro_quest.name}")
            ui.print_message(self.intro_quest.description, "white")
        self.look_around()
        self._handle_initial_dialogue()

        while self.is_running:
            try:
                # Show status bar
                player = self.game_state.player
                current_room = self.game_state.rooms.get(player.current_room_id)
                if current_room:
                    ui.print_status_bar(
                        player.health, player.max_health, player.level,
                        player.experience, current_room.display_name, player.gold
                    )

                command = ui.get_input()
                if command:
                    # Handle command aliases
                    if command in self.command_aliases:
                        command = self.command_aliases[command]

                    self.process_command(command)
                    self._check_game_state()

                    # Auto-save check
                    if self.game_state.should_auto_save():
                        if self.game_state.auto_save():
                            ui.print_message("游戏已自动保存", "dim")

            except KeyboardInterrupt:
                ui.print_warning("\n游戏已中断")
                self.is_running = False
            except Exception as e:
                ui.print_error(f"发生错误: {e}")

        if self.audio:
            self.audio.stop_ambient()

    def _handle_initial_dialogue(self):
        current_room = self.game_state.rooms.get(self.game_state.player.current_room_id)
        if current_room and current_room.name == "cabin":
            for npc in current_room.npcs:
                if npc.name == "斗桨先生":
                    ui.print_message(f"\n{npc.name}站在小屋的阴影中，他缓缓开口：", "white")
                    time.sleep(0.5)
                    dialogue = npc.talk("世界观")
                    ui.print_dialogue(npc.name, dialogue)
                    if self.audio and npc.tts_voice_name:
                        self.audio.speak_mac(dialogue, npc.tts_voice_name)
                    time.sleep(0.5)
                    break

    def process_command(self, command: str):
        parts = command.split()
        action = parts[0] if parts else ""
        target = " ".join(parts[1:]) if len(parts) > 1 else None

        commands = {
            "go": lambda: self.move_player(target) if target else ui.print_warning("去哪个方向？"),
            "look": lambda: self.examine_target(target) if target else self.look_around(),
            "l": lambda: self.examine_target(target) if target else self.look_around(),
            "examine": lambda: self.examine_target(target) if target else ui.print_warning("检查什么？"),
            "take": lambda: self.take_item(target) if target else ui.print_warning("拿什么？"),
            "drop": lambda: self.drop_item(target) if target else ui.print_warning("丢什么？"),
            "use": lambda: self._handle_use_command(parts),
            "inventory": lambda: self.show_inventory(),
            "i": lambda: self.show_inventory(),
            "search": lambda: self.search_target(target) if target else ui.print_warning("搜索什么？"),
            "talk": lambda: self._handle_talk_command(parts),
            "unlock": lambda: self._handle_unlock_command(parts),
            "open": lambda: self.open_target(target) if target else ui.print_warning("打开什么？"),
            "attack": lambda: self.attack_monster(target) if target else self.attack_monster(),
            "stats": lambda: self.show_stats(),
            "help": lambda: self.show_help(),
            "h": lambda: self.show_help(),
            "save": lambda: self.save_game(),
            "load": lambda: self.load_game(),
            "quests": lambda: self.quest_system.show_quests(),
            "quit": lambda: self.quit_game(),
            "q": lambda: self.quit_game(),
            "hint": lambda: self.show_hint(),
            "map": lambda: self.show_map(),
            "achievements": lambda: self.show_achievements(),
            "craft": lambda: self.show_craft_menu(),
            "journal": lambda: self.show_journal(),
            "rest": lambda: self.rest(),
            "travel": lambda: self.fast_travel(target) if target else self.show_travel_menu(),
        }

        current_room = self.game_state.rooms.get(self.game_state.player.current_room_id)
        if current_room and action in current_room.exits:
            self.move_player(action)
        elif action in commands:
            commands[action]()
        else:
            ui.print_error(f"我不明白 '{command}'. 输入 'help' 查看指令。")

    def _handle_use_command(self, parts):
        if len(parts) < 2:
            ui.print_warning("用什么物品？")
            return
        if "on" in parts:
            on_idx = parts.index("on")
            item_name = " ".join(parts[1:on_idx])
            target = " ".join(parts[on_idx+1:])
            self.use_item(item_name, target)
        else:
            self.use_item(" ".join(parts[1:]))

    def _handle_talk_command(self, parts):
        if len(parts) < 3 or parts[1] != "to":
            ui.print_warning("和谁说话？格式: talk to [NPC] (about [话题])")
            return
        npc_parts = []
        topic = "default"
        for i in range(2, len(parts)):
            if parts[i] == "about" and i + 1 < len(parts):
                topic = " ".join(parts[i+1:])
                break
            npc_parts.append(parts[i])
        npc_name = " ".join(npc_parts)
        self.talk_to_npc(npc_name, topic)

    def _handle_unlock_command(self, parts):
        if "with" not in parts:
            ui.print_warning("用什么解锁？格式: unlock [目标] with [物品]")
            return
        with_idx = parts.index("with")
        target = " ".join(parts[1:with_idx])
        item = " ".join(parts[with_idx+1:])
        self.unlock_target(target, item)

    def look_around(self):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            ui.print_error(f"错误：当前房间 '{player.current_room_id}' 未找到!")
            return

        if self.audio:
            self.audio.stop_ambient()
            if current_room.ambient_sound:
                self.audio.play_sound(current_room.ambient_sound, loop=True, volume=0.3)

        if current_room.ascii_art_on_enter and not current_room.visited_art_shown:
            ui.print_ascii_art(ASCII_ARTS.get(current_room.ascii_art_on_enter, ""))
            current_room.visited_art_shown = True

        items = [item.display_name for item in current_room.items]
        npcs = [npc.name for npc in current_room.npcs]
        monsters = [monster.name for monster in current_room.monsters] if current_room.monsters else []
        exits = list(current_room.exits.keys())

        ui.print_room(current_room.display_name, current_room.description, items, npcs, exits)

        # Show monsters if present
        if monsters:
            ui.print_warning(f"⚔️ 怪物: {', '.join(monsters)}")

        self._maybe_trigger_flavor_event(current_room)
        self._check_monsters(current_room)

    def move_player(self, direction: str):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        direction_lower = direction.lower()
        if direction_lower not in current_room.exits:
            ui.print_error(f"不能往 {direction} 走。")
            if self.audio:
                self.audio.play_sound("action_fail")
            return

        next_room_id = current_room.exits[direction_lower]
        next_room = self.game_state.rooms.get(next_room_id)
        if not next_room:
            ui.print_error(f"错误：目标房间 '{next_room_id}' 未定义！")
            return

        if current_room.name == "dark_cellar_entrance" and direction_lower == "下":
            if current_room.properties.get('door_locked', True):
                ui.print_warning("门是锁着的。")
                if self.audio:
                    self.audio.play_sound("action_fail")
                return
            if not player.has_item("点燃的火把"):
                ui.print_warning("太暗了，需要光源。")
                if self.audio:
                    self.audio.play_sound("action_fail")
                return

        if current_room.name == "deep_forest" and direction_lower == "进入洞穴":
            if current_room.properties.get('cave_hidden', True):
                ui.print_warning("这里没什么特别的。")
                return

        if self.audio:
            self.audio.play_sound("footsteps_stone", volume=0.5)

        player.current_room_id = next_room_id
        player.visit_room(next_room_id, next_room.display_name)

        # Check explorer achievement
        if len(player.visited_rooms) >= len(self.game_state.rooms):
            if self.achievement_system.unlock("explorer"):
                ui.print_success("🏆 成就解锁：探险家")

        self._log_action(f"移动至 {next_room.display_name}")
        self.look_around()

        if next_room.name == "deep_forest" and next_room.properties.get('cave_hidden', True):
            ui.print_success("仔细观察后，你注意到一个被藤蔓遮掩的[洞穴入口]！")
            next_room.properties['cave_hidden'] = False
            if self.audio:
                self.audio.play_sound("puzzle_solve")

    def take_item(self, item_name: str):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        item_name_lower = item_name.lower()
        item_to_take = None
        for item in current_room.items:
            if item.name == item_name_lower or item.display_name.lower() == item_name_lower:
                item_to_take = item
                break

        if not item_to_take:
            ui.print_error(f"这里没有 '{item_name}'。")
            if self.audio:
                self.audio.play_sound("action_fail")
            return

        if not item_to_take.takeable:
            ui.print_warning(f"不能拾取 [{item_to_take.display_name}].")
            return

        current_room.remove_item(item_to_take.name)
        player.add_to_inventory(item_to_take)
        ui.print_success(f"你将 [{item_to_take.display_name}] 加入了物品栏。")
        self._log_action(f"拾取 {item_to_take.display_name}")

        # Check achievements
        if len(player.inventory) >= 10:
            if self.achievement_system.unlock("collector"):
                ui.print_success("🏆 成就解锁：收藏家")

        if item_to_take.name == "远古神像":
            if self.achievement_system.unlock("treasure_hunter"):
                ui.print_success("🏆 成就解锁：寻宝猎人")
            self._update_intro_objective(2)

        if self.audio:
            self.audio.play_sound("item_pickup")

    def drop_item(self, item_name: str):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        item = player.remove_from_inventory(item_name)
        if item:
            current_room.add_item(item)
            ui.print_message(f"你丢下了 [{item.display_name}].", "white")
            self._log_action(f"丢弃 {item.display_name} 在 {current_room.display_name}")
        else:
            ui.print_error(f"物品栏里没有 '{item_name}'。")

    def use_item(self, item_name: str, target: Optional[str] = None):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        item = None
        for inv_item in player.inventory:
            if inv_item.name == item_name.lower() or inv_item.display_name.lower() == item_name.lower():
                item = inv_item
                break

        if not item:
            ui.print_error(f"你没有 [{item_name}].")
            if self.audio:
                self.audio.play_sound("action_fail")
            return

        if item.name == "火把" and target and "壁炉" in target.lower():
            if current_room.name == "cabin" and not current_room.properties.get("fireplace_lit"):
                ui.print_success("你用[壁炉]点燃了[火把]！")
                current_room.properties["fireplace_lit"] = True
                player.remove_from_inventory(item.name)
                player.add_to_inventory(self.game_state.items["点燃的火把"])
                self._log_action("点燃了火把")
                self._update_intro_objective(0)
                if self.audio:
                    self.audio.play_sound("fire_crackle")
                return

        if item.name == "治疗药水":
            player.heal(50)
            ui.print_success("你喝下治疗药水，好多了！")
            ui.print_message(f"生命值: {player.health}/{player.max_health}", "green")
            player.remove_from_inventory(item.name)
            self._log_action("使用治疗药水")
            if self.audio:
                self.audio.play_sound("item_pickup")
            return

        if item.name == "撬棍" and target and "石棺" in target.lower():
            if current_room.name == "cave_chamber" and not current_room.properties.get('coffin_opened'):
                ui.print_success("你用[撬棍]撬开了[石棺]！")
                ui.print_message("里面是空的！旁边有些[金币]。", "white")
                current_room.properties['coffin_opened'] = True
                self._log_action("撬开石棺")
                if self.audio:
                    self.audio.play_sound("puzzle_solve")
                return

        ui.print_warning(f"使用了 [{item.display_name}]. 没什么反应。")

    def examine_target(self, target: str):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        target_lower = target.lower()

        for item in player.inventory:
            if item.name == target_lower or item.display_name.lower() == target_lower:
                ui.print_message(f"你仔细检查了 [{item.display_name}]:", "white")
                ui.print_message(item.description, "white")
                if item.ascii_art_name and item.ascii_art_name in ASCII_ARTS:
                    ui.print_ascii_art(ASCII_ARTS[item.ascii_art_name])
                return

        for item in current_room.items:
            if item.name == target_lower or item.display_name.lower() == target_lower:
                ui.print_message(f"你看到一个 [{item.display_name}]:", "white")
                ui.print_message(item.description, "white")
                if item.ascii_art_name and item.ascii_art_name in ASCII_ARTS:
                    ui.print_ascii_art(ASCII_ARTS[item.ascii_art_name])
                return

        for npc in current_room.npcs:
            if npc.name.lower() == target_lower:
                ui.print_message(f"你仔细观察 {npc.name}:", "white")
                ui.print_message(npc.description, "white")
                return

        ui.print_warning(f"这里没有 '{target}' 可以检查。")

    def search_target(self, target: str):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        target_lower = target.lower()

        if current_room.name == "forest_path" and "枯叶" in target_lower:
            if not current_room.properties.get('leaves_searched'):
                ui.print_message("你在枯叶堆里翻找...", "white")
                current_room.properties['leaves_searched'] = True
                key = self.game_state.items.get('生锈的钥匙')
                if key and not current_room.has_item(key.name) and not player.has_item(key.name):
                    current_room.add_item(key)
                    ui.print_success("在枯叶下，你发现了一把[生锈的钥匙]！")
                    self._log_action("在枯叶堆找到生锈的钥匙")
                    if self.audio:
                        self.audio.play_sound("item_pickup")
                return

        if current_room.name == "cellar" and "木箱" in target_lower:
            if not current_room.properties.get('crates_searched'):
                ui.print_message("你搜索了木箱...", "white")
                current_room.properties['crates_searched'] = True
                crowbar = self.game_state.items.get('撬棍')
                if crowbar and not current_room.has_item(crowbar.name) and not player.has_item(crowbar.name):
                    current_room.add_item(crowbar)
                    ui.print_success("在一个箱子里找到了一根[撬棍]！")
                    self._log_action("在地下室木箱找到撬棍")
                    if self.audio:
                        self.audio.play_sound("item_pickup")
                return

        ui.print_warning(f"你搜索了 {target}，但什么也没找到。")

    def talk_to_npc(self, npc_name: str, topic: str = "default"):
        current_room = self.game_state.rooms.get(self.game_state.player.current_room_id)
        if not current_room:
            return

        npc = None
        for n in current_room.npcs:
            if n.name.lower() == npc_name.lower():
                npc = n
                break

        if not npc:
            ui.print_error(f"这里没有 '{npc_name}' 可以对话。")
            return

        dialogue = npc.talk(topic)
        ui.print_dialogue(npc.name, dialogue)
        self._log_action(f"与 {npc.name} 对话")

        if self.audio and npc.tts_voice_name:
            self.audio.speak_mac(dialogue, npc.tts_voice_name)

    def unlock_target(self, target: str, item_name: str):
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        item = None
        for inv_item in player.inventory:
            if inv_item.name == item_name.lower() or inv_item.display_name.lower() == item_name.lower():
                item = inv_item
                break

        if not item:
            ui.print_error(f"你没有 [{item_name}].")
            return

        if current_room.name == "dark_cellar_entrance" and "门" in target.lower():
            if current_room.properties.get('door_locked', True):
                if item.name == "生锈的钥匙":
                    ui.print_success("你用[生锈的钥匙]打开了[门]！")
                    current_room.properties['door_locked'] = False
                    current_room.add_exit("下", "cellar")
                    self._log_action("解锁地下室入口")
                    self._update_intro_objective(1)
                    if self.audio:
                        self.audio.play_sound("door_unlock")
                else:
                    ui.print_error(f"[{item.display_name}] 打不开这扇门。")
            else:
                ui.print_warning("门已开。")
            return

        ui.print_error(f"不能用 [{item.display_name}] 解锁 '{target}'。")

    def open_target(self, target: str):
        current_room = self.game_state.rooms.get(self.game_state.player.current_room_id)
        if not current_room:
            return

        if current_room.name == "dark_cellar_entrance" and "门" in target.lower():
            if not current_room.properties.get('door_locked', True):
                ui.print_message("门已开。", "white")
                if self.audio:
                    self.audio.play_sound("door_open")
            else:
                ui.print_warning("门锁着。")
            return

        ui.print_error(f"尝试打开 '{target}' 失败。")

    def show_inventory(self):
        player = self.game_state.player
        if not player.inventory:
            ui.print_warning("你的物品栏是空的。")
            return

        items = [(item.display_name, item.description, item.item_type) for item in player.inventory]
        ui.print_inventory(items, player.health, player.max_health, player.level, player.experience)

    def show_help(self):
        commands = {
            "go [方向] / n/s/e/w": "向指定方向移动",
            "look / l": "查看当前环境",
            "examine [目标] / x": "仔细检查物品或NPC",
            "search [目标]": "搜索特定位置",
            "take [物品] / t": "拾取物品",
            "drop [物品] / d": "丢弃物品",
            "inventory / i": "查看物品栏",
            "use [物品] (on [目标]) / u": "使用物品",
            "unlock [目标] with [物品]": "用物品解锁",
            "open [目标]": "打开某物",
            "attack [怪物]": "攻击房间内的怪物",
            "talk to [NPC] (about [话题])": "与NPC对话",
            "stats": "查看角色属性",
            "quests": "查看任务",
            "hint": "获取当前位置的提示",
            "map": "查看地图",
            "achievements": "查看成就",
            "craft": "查看合成配方",
            "journal": "查看最近的冒险记录",
            "rest": "在安全的地方休息恢复生命",
            "travel [地点]": "快速旅行",
            "save": "保存游戏",
            "load": "读取游戏",
            "help / h": "显示帮助",
            "quit / q": "退出游戏",
        }
        ui.print_help(commands)

    def show_hint(self):
        """Show contextual hint for current room"""
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        hints = self.hints.get(current_room.name, ["探索周围环境，寻找线索"])
        import random
        hint = random.choice(hints)
        ui.print_hint(hint)

    def show_map(self):
        """Show mini-map of explored areas"""
        player = self.game_state.player
        visited = {room_id: True for room_id in player.visited_rooms}
        ui.print_mini_map(player.current_room_id, visited, {})

    def show_achievements(self):
        """Show all achievements"""
        achievements = self.achievement_system.get_all()
        ui.print_achievements(achievements)
        unlocked = self.achievement_system.get_unlocked_count()
        total = len(achievements)
        ui.print_message(f"\n已解锁: {unlocked}/{total}", "yellow")

    def show_craft_menu(self):
        """Show crafting menu and handle crafting"""
        player = self.game_state.player
        recipes = self.crafting_system.get_available_recipes(player)

        if not recipes:
            ui.print_warning("没有可用的合成配方")
            return

        ui.print_crafting_menu(recipes)
        ui.print_message("\n输入配方编号进行合成，或输入 'cancel' 取消", "white")

        choice = ui.get_input("选择 > ")
        if choice == "cancel":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(recipes):
                recipe_name = list(self.crafting_system.recipes.keys())[idx]
                result = self.crafting_system.craft(recipe_name, player, self.game_state.items)
                if result:
                    player.add_to_inventory(result)
                    ui.print_success(f"成功合成了 [{result.display_name}]！")

                    # Check crafting achievement
                    if self.crafting_system.crafted_count >= 5:
                        if self.achievement_system.unlock("crafter"):
                            ui.print_success("🏆 成就解锁：工匠")

                    if self.audio:
                        self.audio.play_sound("puzzle_solve")
                else:
                    ui.print_error("合成失败！缺少必要材料。")
        except (ValueError, IndexError):
            ui.print_error("无效的选择")

    def show_travel_menu(self):
        """Show fast travel menu"""
        player = self.game_state.player
        ui.print_message("\n[bold cyan]快速旅行[/]", "cyan")
        ui.print_message("已解锁的地点：", "white")

        for idx, room_id in enumerate(player.visited_rooms, 1):
            room = self.game_state.rooms.get(room_id)
            if room:
                ui.print_message(f"  [{idx}] {room.display_name}", "cyan")

        ui.print_message("\n输入编号进行传送，或输入 'cancel' 取消", "white")
        choice = ui.get_input("选择 > ")

        if choice == "cancel":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(player.visited_rooms):
                target_room_id = player.visited_rooms[idx]
                self.fast_travel(target_room_id)
        except (ValueError, IndexError):
            ui.print_error("无效的选择")

    def fast_travel(self, target_room_id: str):
        """Fast travel to a visited room"""
        player = self.game_state.player

        if target_room_id not in player.visited_rooms:
            ui.print_error("你还没有去过那个地方！")
            return

        if target_room_id == player.current_room_id:
            ui.print_warning("你已经在这里了！")
            return

        target_room = self.game_state.rooms.get(target_room_id)
        if not target_room:
            ui.print_error("目标地点不存在！")
            return

        ui.print_message(f"传送中... . . .", "cyan")
        time.sleep(0.5)
        player.current_room_id = target_room_id
        player.visit_room(target_room_id, target_room.display_name)
        ui.print_success(f"已传送到 {target_room.display_name}")
        self._log_action(f"快速旅行到 {target_room.display_name}")

        if self.audio:
            self.audio.play_sound("puzzle_solve")

        self.look_around()

    def show_journal(self):
        """Display recent action log"""
        player = self.game_state.player
        entries = player.history[-10:]
        if not entries:
            ui.print_warning("暂时没有可显示的冒险记录。")
            return
        ui.print_journal(entries)

    def attack_monster(self, monster_name: Optional[str] = None):
        """Attack a monster in the current room"""
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        if not current_room.monsters:
            ui.print_warning("这里没有可以攻击的怪物。")
            return

        # Find target monster
        target = None
        if monster_name:
            for monster in current_room.monsters:
                if monster.name.lower() == monster_name.lower():
                    target = monster
                    break
            if not target:
                ui.print_error(f"找不到怪物 '{monster_name}'")
                return
        else:
            target = current_room.monsters[0]

        # Start combat
        if self.combat_system.start_combat(player, target):
            # Monster defeated
            current_room.monsters.remove(target)
            gold_reward = target.attack_power * 5
            player.add_gold(gold_reward)
            ui.print_success(f"获得 {gold_reward} 金币！")
            self._log_action(f"击败了 {target.name}")

            # Check monster hunter achievement
            if not hasattr(self, '_monsters_defeated'):
                self._monsters_defeated = 0
            self._monsters_defeated += 1
            if self._monsters_defeated >= 3:
                if self.achievement_system.unlock("survivor"):
                    ui.print_success("🏆 成就解锁：怪物猎人")

    def show_stats(self):
        """Show character stats using enhanced panel"""
        player = self.game_state.player
        ui.print_stats_panel(
            player.health, player.max_health, player.level,
            player.experience, player.strength, player.intelligence,
            player.defense, player.gold, player.score
        )

    def _check_monsters(self, room):
        """Check for monsters and trigger combat if needed"""
        if not room.monsters:
            return

        for monster in room.monsters[:]:  # Copy list to avoid modification during iteration
            if monster.hostile:
                ui.print_warning(f"\n⚔️ 警告：{monster.name} 注意到了你！")
                ui.print_message(f"你可以输入 'attack' 进行攻击，或尝试 'go [方向]' 逃离。", "yellow")
                break

    def rest(self):
        """Rest to recover health when safe"""
        player = self.game_state.player
        current_room = self.game_state.rooms.get(player.current_room_id)
        if not current_room:
            return

        # Check if monsters present
        if current_room.monsters:
            ui.print_warning("有怪物在附近，无法休息！")
            return

        if current_room.name != "cabin":
            ui.print_warning("这里不安全，无法放心休息。")
            return

        heal_amount = 25 if current_room.properties.get("fireplace_lit") else 15
        before = player.health
        player.heal(heal_amount)
        recovered = player.health - before
        ui.print_success(f"你休息片刻，恢复了 {recovered} 点生命值。")
        self._log_action("在小屋休息恢复体力")
        if self.audio:
            self.audio.play_sound("fire_crackle")

    def save_game(self):
        """Save game with slot selection"""
        saves = self.game_state.list_saves()

        ui.print_message("\n[bold cyan]保存游戏[/]", "cyan")
        ui.print_message("选择存档槽位：", "white")

        for save in saves:
            if save['exists']:
                ui.print_message(f"  [{save['slot']}] {save['location']} - Lv.{save['level']}", "yellow")
            else:
                ui.print_message(f"  [{save['slot']}] <空>", "dim")

        ui.print_message("\n输入槽位编号 (1-3)，或输入 'cancel' 取消", "white")
        choice = ui.get_input("选择 > ")

        if choice == "cancel":
            return

        try:
            slot = int(choice)
            if 1 <= slot <= 3:
                if self.game_state.save_game(slot=slot):
                    ui.print_success(f"游戏进度已保存到槽位 {slot}")
                    if self.audio:
                        self.audio.play_sound("puzzle_solve")
                else:
                    ui.print_error("保存失败！")
            else:
                ui.print_error("无效的槽位编号")
        except ValueError:
            ui.print_error("无效的输入")

    def load_game(self):
        """Load game with slot selection"""
        saves = self.game_state.list_saves()

        ui.print_message("\n[bold cyan]读取游戏[/]", "cyan")
        ui.print_message("选择存档槽位：", "white")

        available_saves = [s for s in saves if s['exists']]
        if not available_saves:
            ui.print_warning("没有可用的存档")
            return

        for save in saves:
            if save['exists']:
                ui.print_message(f"  [{save['slot']}] {save['location']} - Lv.{save['level']}", "yellow")
            else:
                ui.print_message(f"  [{save['slot']}] <空>", "dim")

        ui.print_message("\n输入槽位编号 (1-3)，或输入 'cancel' 取消", "white")
        choice = ui.get_input("选择 > ")

        if choice == "cancel":
            return

        try:
            slot = int(choice)
            if 1 <= slot <= 3:
                if self.game_state.load_game(slot=slot):
                    ui.print_success("游戏进度已成功读取！")
                    if self.audio:
                        self.audio.play_sound("puzzle_solve")
                    self.look_around()
                else:
                    ui.print_error("读取失败！")
            else:
                ui.print_error("无效的槽位编号")
        except ValueError:
            ui.print_error("无效的输入")

    def quit_game(self):
        ui.print_warning("你确定要退出游戏吗？(是/否)")
        confirm = ui.get_input()
        if confirm in ["是", "yes", "y"]:
            ui.print_message("感谢游玩！再见。", "magenta")
            self.is_running = False

    def _check_game_state(self):
        player = self.game_state.player
        if player.health <= 0:
            ui.print_error("\n你的生命值耗尽了...游戏结束。")
            ui.print_ascii_art(ASCII_ARTS.get("game_over", ""))
            self.is_running = False
            return

        if self._check_win_condition():
            ui.print_success("\n恭喜！你找到了远古神像并打开了石棺，揭开了宝藏的秘密！游戏胜利！")
            ui.print_ascii_art(ASCII_ARTS.get("treasure_chest_open", ""))
            if self.audio:
                self.audio.play_sound("puzzle_solve")
            self.is_running = False

    def _check_win_condition(self) -> bool:
        player = self.game_state.player
        treasure_room = self.game_state.rooms.get("cave_chamber")
        return (player.current_room_id == "cave_chamber" and
                treasure_room and treasure_room.properties.get('coffin_opened') and
                player.has_item("远古神像"))
