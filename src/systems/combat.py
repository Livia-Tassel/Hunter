"""Combat and quest systems"""
from typing import Optional, List, Dict
from ..core.entities import Player, NPC
from ..ui.terminal_ui import ui
import random
import time

class CombatSystem:
    def __init__(self, audio_system=None, auto_mode: bool = False):
        self.audio = audio_system
        self.in_combat = False
        self.auto_mode = auto_mode  # 自动战斗模式（用于测试）

    def start_combat(self, player: Player, enemy: NPC) -> bool:
        """Returns True if player wins, False if player loses"""
        self.in_combat = True
        ui.print_message(f"\n[bold red]战斗开始！[/] 你遭遇了 {enemy.name}！", "red")
        
        if not self.auto_mode:
            time.sleep(1)

        while player.health > 0 and enemy.health > 0:
            ui.print_combat(player.health, player.max_health, enemy.name, enemy.health, enemy.max_health)

            # 自动模式下自动攻击
            if self.auto_mode:
                action = "攻击"
            else:
                action = ui.get_input("\n[攻击/逃跑] > ")

            if action in ["逃跑", "flee", "run"]:
                if random.random() < 0.5:
                    ui.print_success("你成功逃跑了！")
                    self.in_combat = False
                    return False
                else:
                    ui.print_warning("逃跑失败！")

            player_damage = self._calculate_damage(player.strength, enemy.defense_power)
            enemy.health -= player_damage
            ui.print_message(f"你对 {enemy.name} 造成了 [bold red]{player_damage}[/] 点伤害！", "green")

            if self.audio:
                self.audio.play_sound("combat_hit", volume=0.5)

            time.sleep(0.5)

            if enemy.health <= 0:
                ui.print_monster_defeated(enemy.name, enemy.attack_power * 10, enemy.attack_power * 5)
                old_level = player.level
                player.add_experience(enemy.attack_power * 10)

                # Check for level up
                if player.level > old_level:
                    ui.print_level_up(player.level)
                    if self.audio:
                        self.audio.play_sound("level_up")

                if self.audio:
                    self.audio.play_sound("puzzle_solve")

                self.in_combat = False
                return True

            enemy_damage = self._calculate_damage(enemy.attack_power, player.defense)
            player.take_damage(enemy_damage)
            ui.print_message(f"{enemy.name} 对你造成了 [bold red]{enemy_damage}[/] 点伤害！", "red")

            time.sleep(0.5)

            if player.health <= 0:
                ui.print_error("\n你被击败了...")
                self.in_combat = False
                return False

        self.in_combat = False
        return player.health > 0

    def _calculate_damage(self, attack: int, defense: int) -> int:
        base_damage = max(1, attack - defense // 2)
        variance = random.randint(-2, 2)
        return max(1, base_damage + variance)

class Quest:
    def __init__(self, quest_id: str, name: str, description: str,
                 objectives: List[str], rewards: Dict[str, int]):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.completed_objectives = [False] * len(objectives)
        self.rewards = rewards
        self.completed = False

    def complete_objective(self, index: int):
        if 0 <= index < len(self.objectives):
            self.completed_objectives[index] = True
            if all(self.completed_objectives):
                self.completed = True

    def is_completed(self) -> bool:
        return self.completed

    def get_progress(self) -> str:
        completed = sum(self.completed_objectives)
        total = len(self.objectives)
        return f"{completed}/{total}"

class QuestSystem:
    def __init__(self):
        self.active_quests: List[Quest] = []
        self.completed_quests: List[Quest] = []

    def add_quest(self, quest: Quest):
        self.active_quests.append(quest)
        ui.print_success(f"新任务：{quest.name}")
        ui.print_message(quest.description, "white")

    def complete_quest(self, quest_id: str, player: Player) -> bool:
        for quest in self.active_quests:
            if quest.quest_id == quest_id and quest.is_completed():
                self.active_quests.remove(quest)
                self.completed_quests.append(quest)

                ui.print_success(f"任务完成：{quest.name}")

                if "experience" in quest.rewards:
                    player.add_experience(quest.rewards["experience"])
                    ui.print_message(f"获得 {quest.rewards['experience']} 点经验！", "yellow")

                if "score" in quest.rewards:
                    player.score += quest.rewards["score"]

                if "gold" in quest.rewards:
                    player.add_gold(quest.rewards["gold"])
                    ui.print_message(f"获得 {quest.rewards['gold']} 金币！", "yellow")

                return True
        return False

    def show_quests(self):
        if not self.active_quests:
            ui.print_warning("没有进行中的任务")
            return

        ui.print_message("\n[bold yellow]当前任务：[/]", "yellow")
        for quest in self.active_quests:
            ui.print_message(f"\n[cyan]{quest.name}[/] - 进度: {quest.get_progress()}", "white")
            for i, obj in enumerate(quest.objectives):
                status = "✓" if quest.completed_objectives[i] else "○"
                ui.print_message(f"  {status} {obj}", "white")
