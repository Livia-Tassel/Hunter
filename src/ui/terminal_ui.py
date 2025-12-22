"""Enhanced terminal UI using rich library"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from typing import Optional, List
import time

console = Console()

class GameUI:
    def __init__(self):
        self.console = console
        self.screen_width = 80

    def clear(self):
        self.console.clear()

    def print_header(self, title: str):
        header = Panel(
            Text(title, style="bold yellow", justify="center"),
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(header)

    def print_message(self, message: str, style: str = "white", slow: bool = False):
        if slow:
            for char in message:
                self.console.print(char, end="", style=style)
                time.sleep(0.02)
            self.console.print()
        else:
            self.console.print(message, style=style)

    def print_room(self, room_name: str, description: str, items: List[str],
                   npcs: List[str], exits: List[str]):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="description"),
            Layout(name="details", size=8)
        )

        layout["header"].update(Panel(f"[bold cyan]{room_name}[/]", border_style="cyan"))
        layout["description"].update(Panel(description, border_style="blue"))

        details_table = Table(show_header=False, box=None, padding=(0, 2))
        details_table.add_column("Label", style="bold green")
        details_table.add_column("Content")

        if items:
            details_table.add_row("物品:", ", ".join([f"[blue]{i}[/]" for i in items]))
        if npcs:
            details_table.add_row("人物:", ", ".join([f"[magenta]{n}[/]" for n in npcs]))
        details_table.add_row("出口:", ", ".join([f"[cyan]{e}[/]" for e in exits]) if exits else "[yellow]无[/]")

        layout["details"].update(Panel(details_table, border_style="green"))
        self.console.print(layout)

    def print_inventory(self, items: List[tuple], health: int, max_health: int,
                       level: int, exp: int):
        table = Table(title="[bold yellow]物品栏[/]", border_style="blue")
        table.add_column("物品", style="cyan")
        table.add_column("描述", style="white")
        table.add_column("类型", style="green")

        for name, desc, item_type in items:
            table.add_row(name, desc[:40] + "..." if len(desc) > 40 else desc, item_type)

        stats = f"[red]生命: {health}/{max_health}[/] | [yellow]等级: {level}[/] | [green]经验: {exp}[/]"

        self.console.print(Panel(stats, border_style="yellow"))
        self.console.print(table)

    def print_combat(self, player_hp: int, player_max_hp: int,
                    enemy_name: str, enemy_hp: int, enemy_max_hp: int):
        layout = Layout()
        layout.split_row(
            Layout(name="player"),
            Layout(name="enemy")
        )

        player_bar = self._create_health_bar("你", player_hp, player_max_hp, "green")
        enemy_bar = self._create_health_bar(enemy_name, enemy_hp, enemy_max_hp, "red")

        layout["player"].update(Panel(player_bar, border_style="green"))
        layout["enemy"].update(Panel(enemy_bar, border_style="red"))

        self.console.print(layout)

    def _create_health_bar(self, name: str, hp: int, max_hp: int, color: str) -> str:
        percentage = hp / max_hp if max_hp > 0 else 0
        bar_length = 20
        filled = int(bar_length * percentage)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"[bold]{name}[/]\n[{color}]{bar}[/] {hp}/{max_hp}"

    def print_ascii_art(self, art: str):
        self.console.print(Panel(art, border_style="yellow"))

    def print_dialogue(self, npc_name: str, text: str):
        panel = Panel(
            f"[white]{text}[/]",
            title=f"[bold magenta]{npc_name}[/]",
            border_style="magenta",
            padding=(1, 2)
        )
        self.console.print(panel)

    def print_help(self, commands: dict):
        table = Table(title="[bold yellow]游戏指令[/]", border_style="cyan")
        table.add_column("指令", style="green", width=30)
        table.add_column("说明", style="white")

        for cmd, desc in commands.items():
            table.add_row(cmd, desc)

        self.console.print(table)

    def get_input(self, prompt: str = "> ") -> str:
        return self.console.input(f"[green]{prompt}[/]").strip().lower()

    def print_error(self, message: str):
        self.console.print(f"[bold red]✗[/] {message}")

    def print_success(self, message: str):
        self.console.print(f"[bold green]✓[/] {message}")

    def print_warning(self, message: str):
        self.console.print(f"[bold yellow]⚠[/] {message}")

ui = GameUI()
