"""Main game engine"""
import os
import time
from typing import Optional
from .core.entities import Player
from .ui.terminal_ui import ui
from .systems.audio import init_audio
from .systems.game_state import GameState
from .systems.combat import CombatSystem, QuestSystem, Quest
from .content.game_data import create_items, create_npcs, create_rooms, ASCII_ARTS

class GameEngine:
    def __init__(self, save_file: str, sounds_dir: str):
        self.save_file = save_file
        self.sounds_dir = sounds_dir
        self.audio = init_audio(sounds_dir)
        self.game_state = GameState(save_file)
        self.combat_system = CombatSystem(self.audio)
        self.quest_system = QuestSystem()
        self.is_running = True
        self._setup_world()

    def _setup_world(self):
        self.game_state.items = create_items()
        self.game_state.npcs = create_npcs()
        self.game_state.rooms = create_rooms(self.game_state.items, self.game_state.npcs)
        self.game_state.player = Player(current_room_id="cabin")

    def start_game(self):
        ui.clear()
        ui.print_header("迷失的宝藏猎人 (The Lost Treasure Hunter)")
        ui.print_message("欢迎来到《迷失的宝藏猎人》！输入 'help' 查看指令。", "green")
        self.look_around()
        self._handle_initial_dialogue()

        while self.is_running:
            try:
                command = ui.get_input()
                if command:
                    self.process_command(command)
                    self._check_game_state()
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
            "help": lambda: self.show_help(),
            "h": lambda: self.show_help(),
            "save": lambda: self.save_game(),
            "load": lambda: self.load_game(),
            "quests": lambda: self.quest_system.show_quests(),
            "quit": lambda: self.quit_game(),
            "q": lambda: self.quit_game(),
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
        exits = list(current_room.exits.keys())

        ui.print_room(current_room.display_name, current_room.description, items, npcs, exits)

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
                if self.audio:
                    self.audio.play_sound("fire_crackle")
                return

        if item.name == "治疗药水":
            player.heal(50)
            ui.print_success("你喝下治疗药水，好多了！")
            ui.print_message(f"生命值: {player.health}/{player.max_health}", "green")
            player.remove_from_inventory(item.name)
            if self.audio:
                self.audio.play_sound("item_pickup")
            return

        if item.name == "撬棍" and target and "石棺" in target.lower():
            if current_room.name == "cave_chamber" and not current_room.properties.get('coffin_opened'):
                ui.print_success("你用[撬棍]撬开了[石棺]！")
                ui.print_message("里面是空的！旁边有些[金币]。", "white")
                current_room.properties['coffin_opened'] = True
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
            "go [方向]": "向指定方向移动",
            "look / l": "查看当前环境",
            "examine [目标]": "仔细检查物品或NPC",
            "search [目标]": "搜索特定位置",
            "take [物品]": "拾取物品",
            "drop [物品]": "丢弃物品",
            "inventory / i": "查看物品栏",
            "use [物品] (on [目标])": "使用物品",
            "unlock [目标] with [物品]": "用物品解锁",
            "open [目标]": "打开某物",
            "talk to [NPC] (about [话题])": "与NPC对话",
            "quests": "查看任务",
            "save": "保存游戏",
            "load": "读取游戏",
            "help / h": "显示帮助",
            "quit / q": "退出游戏",
        }
        ui.print_help(commands)

    def save_game(self):
        if self.game_state.save_game():
            ui.print_success(f"游戏进度已保存到 {self.save_file}")
            if self.audio:
                self.audio.play_sound("puzzle_solve")
        else:
            ui.print_error("保存失败！")

    def load_game(self):
        if self.game_state.load_game():
            ui.print_success("游戏进度已成功读取！")
            if self.audio:
                self.audio.play_sound("puzzle_solve")
            self.look_around()
        else:
            ui.print_error("读取失败！")

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
