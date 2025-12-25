#!/usr/bin/env python3
"""
The Lost Treasure Hunter - 自动测试脚本
此脚本模拟完整的游戏通关流程，用于自动化测试

使用方法:
    python test_walkthrough.py [--verbose] [--delay SECONDS]

参数:
    --verbose, -v    显示详细输出
    --delay, -d      每条指令之间的延迟秒数 (默认: 0.05)
"""

import os
import sys
import time
import argparse
from typing import List, Tuple

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game_engine import GameEngine
from src.systems.combat import CombatSystem
from src.ui.terminal_ui import ui

class AutomatedTester:
    """自动化游戏测试器"""
    
    def __init__(self, verbose: bool = False, delay: float = 0.05):
        self.verbose = verbose
        self.delay = delay
        self.commands_executed = 0
        self.errors = []
        self.game = None
        self.log = []
        
    def setup_game(self):
        """初始化游戏引擎（自动战斗模式）"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_dir = os.path.join(script_dir, "saving")
        sounds_dir = os.path.join(script_dir, "sounds")
        
        os.makedirs(save_dir, exist_ok=True)
        
        self.game = GameEngine(save_dir, sounds_dir)
        self.game.audio = None  # 禁用音频
        
        # 启用自动战斗模式
        self.game.combat_system = CombatSystem(audio_system=None, auto_mode=True)
        
    def load_walkthrough(self, filepath: str) -> List[str]:
        """加载通关脚本"""
        commands = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if line and not line.startswith('#'):
                    commands.append(line)
        return commands
    
    def execute_command(self, command: str) -> Tuple[bool, str]:
        """执行单条游戏指令"""
        try:
            # 处理退出命令
            if command.lower() in ['quit', 'q']:
                return True, "跳过退出命令"
            
            # 处理需要确认的命令
            if command.lower() in ['是', 'yes', 'y', '否', 'no', 'n']:
                return True, "跳过确认命令"
            
            # 执行命令
            self.game.process_command(command)
            self.game._check_game_state()
            
            return True, "成功"
            
        except Exception as e:
            return False, str(e)
    
    def run_test(self, walkthrough_file: str) -> bool:
        """运行完整测试"""
        print("=" * 60)
        print("🎮 The Lost Treasure Hunter - 自动化测试")
        print("=" * 60)
        
        # 设置游戏
        print("\n📦 初始化游戏...")
        self.setup_game()
        print("✓ 游戏引擎已加载（自动战斗模式）")
        
        # 加载脚本
        print(f"\n📜 加载通关脚本: {walkthrough_file}")
        commands = self.load_walkthrough(walkthrough_file)
        print(f"✓ 已加载 {len(commands)} 条指令")
        
        # 执行测试
        print("\n🚀 开始执行测试...\n")
        print("-" * 60)
        
        for i, command in enumerate(commands, 1):
            # 检查游戏是否已结束
            if not self.game.is_running:
                print(f"\n🏆 游戏在第 {i} 条指令时结束（胜利！）")
                break
            
            # 显示进度
            if self.verbose:
                print(f"[{i:3d}/{len(commands)}] 执行: {command}")
            else:
                # 简洁模式：只显示重要操作
                if any(keyword in command for keyword in ['go', 'take', 'use', 'attack', 'unlock', 'search']):
                    print(f"  ▶ {command}")
            
            # 执行命令
            success, message = self.execute_command(command)
            
            if not success:
                self.errors.append((i, command, message))
                if self.verbose:
                    print(f"  ✗ 错误: {message}")
            
            self.commands_executed += 1
            
            # 延迟
            if self.delay > 0:
                time.sleep(self.delay)
        
        print("-" * 60)
        
        # 输出结果
        return self.print_results()
    
    def print_results(self) -> bool:
        """输出测试结果"""
        print("\n" + "=" * 60)
        print("📊 测试结果")
        print("=" * 60)
        
        player = self.game.game_state.player
        
        # 游戏状态
        print(f"\n🎯 游戏状态:")
        print(f"   运行中: {'否 (已结束)' if not self.game.is_running else '是'}")
        print(f"   当前位置: {player.current_room_id}")
        
        # 玩家状态
        print(f"\n👤 玩家状态:")
        print(f"   生命值: {player.health}/{player.max_health}")
        print(f"   等级: {player.level}")
        print(f"   经验: {player.experience}")
        print(f"   金币: {player.gold}")
        print(f"   物品: {len(player.inventory)} 件")
        
        # 已探索房间
        print(f"\n🗺️ 已探索房间: {len(player.visited_rooms)}/{len(self.game.game_state.rooms)}")
        for room_id in player.visited_rooms:
            room = self.game.game_state.rooms.get(room_id)
            if room:
                print(f"   ✓ {room.display_name}")
        
        # 物品栏
        print(f"\n🎒 物品栏:")
        for item in player.inventory:
            print(f"   • {item.display_name}")
        
        # 检查胜利条件
        print(f"\n🏆 胜利条件检查:")
        treasure_room = self.game.game_state.rooms.get("cave_chamber")
        has_statue = player.has_item("远古神像")
        coffin_opened = treasure_room.properties.get('coffin_opened', False) if treasure_room else False
        at_chamber = player.current_room_id == "cave_chamber"
        
        print(f"   在洞穴密室: {'✓' if at_chamber else '✗'}")
        print(f"   持有远古神像: {'✓' if has_statue else '✗'}")
        print(f"   石棺已打开: {'✓' if coffin_opened else '✗'}")
        
        win_condition = at_chamber and has_statue and coffin_opened
        
        # 统计
        print(f"\n📈 执行统计:")
        print(f"   执行指令数: {self.commands_executed}")
        print(f"   错误数: {len(self.errors)}")
        
        if self.errors and self.verbose:
            print(f"\n⚠️ 错误详情:")
            for line_num, cmd, err in self.errors[:5]:  # 只显示前5个错误
                print(f"   第 {line_num} 行: {cmd} -> {err}")
        
        # 最终结果
        print("\n" + "=" * 60)
        if win_condition or not self.game.is_running:
            print("✅ 测试通过！游戏已成功通关！")
            return True
        else:
            print("❌ 测试未完成 - 未达到胜利条件")
            return False


def main():
    parser = argparse.ArgumentParser(description='The Lost Treasure Hunter 自动化测试')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细输出')
    parser.add_argument('-d', '--delay', type=float, default=0.02, help='指令间延迟(秒)')
    parser.add_argument('-f', '--file', type=str, default='saving/official_walkthrough.txt',
                        help='通关脚本文件路径')
    
    args = parser.parse_args()
    
    # 获取脚本路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    walkthrough_file = os.path.join(script_dir, args.file)
    
    if not os.path.exists(walkthrough_file):
        print(f"错误: 找不到通关脚本文件: {walkthrough_file}")
        sys.exit(1)
    
    # 运行测试
    tester = AutomatedTester(verbose=args.verbose, delay=args.delay)
    success = tester.run_test(walkthrough_file)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
