# text_adventure_game.py (The Lost Treasure Hunter.py)

import json
import os
import textwrap
import time
import platform # <--- 新增：用于检测操作系统

# --- 颜色定义 (ANSI 转义码) ---
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'    # 用于物品
    MAGENTA = '\033[95m' # 用于NPC或重要提示
    CYAN = '\033[96m'    # 用于出口或地点
    WHITE = '\033[97m'

def c_text(text, color, bold=False):
    """为文本添加颜色和粗体"""
    return f"{Colors.BOLD if bold else ''}{color}{text}{Colors.RESET}"

# --- Pygame Mixer 初始化 (用于音效) ---
SOUND_ENABLED = True
AMBIENT_CHANNEL = None 

try:
    import pygame
    pygame.mixer.init()
    if pygame.mixer.get_num_channels() > 0:
        AMBIENT_CHANNEL = pygame.mixer.Channel(0)
    else: 
        AMBIENT_CHANNEL = None 
    print(f"{Colors.GREEN}Pygame Mixer 初始化成功，音效功能已启用。{Colors.RESET}")
except ImportError:
    print(f"{Colors.YELLOW}警告：未找到 Pygame 库。更丰富的音效功能将不可用。请尝试 `pip install pygame`{Colors.RESET}")
    SOUND_ENABLED = False
except pygame.error as e:
    print(f"{Colors.YELLOW}警告：Pygame Mixer 初始化失败: {e}。音效功能将不可用。{Colors.RESET}")
    SOUND_ENABLED = False
    AMBIENT_CHANNEL = None

# --- 常量和配置 ---
GAME_TITLE = "迷失的宝藏猎人 (The Lost Treasure Hunter)"

# --- ASCII 艺术定义 ---
ASCII_ARTS = {
    "cave_entrance": textwrap.dedent(f"""
{Colors.YELLOW}
        .--""--.
       /        \\
      |  O    O  |
      |   .__.   |
       \\  `--'  /
        `------'
{Colors.RESET}
    一个深邃的洞穴入口若隐若现...
    """),
    "treasure_chest_open": textwrap.dedent(f"""
{Colors.GREEN}
       ___________
      '._==_==_=_.'
      .-\\:      /-.
     | (|:.     |) |
      '-|:.     |-'
        \\::.    /
         '::. .'
           ) (
         _.' '._
        '-------'
{Colors.RESET}
    宝箱敞开着，闪耀着金光！
    """),
    "game_over": textwrap.dedent(f"""
{Colors.RED}
    ██████╗  █████╗ ███╗   ███╗ ███████╗
    ██╔══██╗██╔══██╗████╗ ████║ ██╔════╝
    ██║  ██║███████║██╔████╔██║ █████╗
    ██║  ██║██╔══██║██║╚██╔╝██║ ██╔══╝
    ██████╔╝██║  ██║██║ ╚═╝ ██║ ███████╗
    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚══════╝
{Colors.RESET}
    """),
    "torch_art": textwrap.dedent(f"""
{Colors.YELLOW}
          ()
         ▐▐▐▐
        ▐▐███▌▌
        ███████
         █████
          ███
          ███
           V
{Colors.RESET}
    这是一支普通的火把。
    """), 
    "lit_torch_art": textwrap.dedent(f"""
{Colors.RED}      _{Colors.YELLOW}(火焰){Colors.RED}_
     {Colors.YELLOW}(火焰){Colors.RED}(_{Colors.YELLOW}(火焰){Colors.RED}_){Colors.YELLOW}(火焰)
    {Colors.RED}(火焰){Colors.YELLOW}(火焰){Colors.RED}(火焰){Colors.YELLOW}(火焰){Colors.RED}(火焰)
{Colors.WHITE}      ▐▐▐▐▐
      █████
      █████
{Colors.YELLOW}     VVVVV
{Colors.RESET}
    火把熊熊燃烧着，发出噼啪声。
    """),
    "door_closed_art": textwrap.dedent(f"""
{Colors.CYAN}
    ┎-----┒
    ┃  {Colors.YELLOW}=={Colors.CYAN} ┃
    ┃  {Colors.YELLOW}||{Colors.CYAN} ┃
    ┃  {Colors.YELLOW}=={Colors.CYAN} ┃
    ┖-----┚
{Colors.RESET}
    一扇紧闭的门。
    """),
    "door_open_art": textwrap.dedent(f"""
{Colors.CYAN}
    ┎-----\\
    ┃      {Colors.YELLOW}🚪{Colors.CYAN}
    ┃
    ┃
    ┖------
{Colors.RESET}
    门是开着的。
    """),
    "fireplace_cold_art": textwrap.dedent(f"""
{Colors.WHITE}
      ,--''''--.
     /          \\
    |            |
     \\  ______  /
      `-|____|-'
{Colors.RESET}
    一个冰冷的壁炉。
    """),
    "fireplace_lit_art": textwrap.dedent(f"""
{Colors.RED}     _{Colors.YELLOW}(火焰){Colors.RED}_
    {Colors.YELLOW}(火焰){Colors.RED}(_{Colors.YELLOW}(火焰){Colors.RED}_){Colors.YELLOW}(火焰)
{Colors.WHITE}   ,--''''--.
  /          \\
 | {Colors.YELLOW}(火焰){Colors.RED}(火焰){Colors.YELLOW}(火焰){Colors.WHITE}  |
  \\  ______  /
   `-|____|-'
{Colors.RESET}
    壁炉里火焰跳动，很暖和。
    """),
}

# --- 音效文件定义 ---
SOUND_FILES = {
    "ambient_forest": "forest_ambience.ogg", 
    "ambient_cave": "cave_drips.ogg",
    "ambient_windy": "wind_howling.ogg",
    "item_pickup": "pickup.wav",
    "action_fail": "error_buzz.wav",
    "puzzle_solve": "success_chime.wav",
    "door_open": "door_creak_open.wav",
    "door_unlock": "unlock_mechanism.wav",
    "fire_crackle": "fire_crackle_loop.ogg",
    "footsteps_stone": "footsteps_stone.wav",
    "default_beep": None 
}
LOADED_SOUNDS = {}

# --- 动态构建存档路径 ---
try:
    script_file_path = os.path.abspath(__file__)
    SCRIPT_FOLDER_PATH = os.path.dirname(script_file_path) 
    saving_folder_name = "saving"
    saving_folder_path = os.path.join(SCRIPT_FOLDER_PATH, saving_folder_name)
    os.makedirs(saving_folder_path, exist_ok=True)
    SAVE_FILE_NAME = "adventure_save.json"
    SAVE_FILE = os.path.join(saving_folder_path, SAVE_FILE_NAME)
except NameError:
    print(f"{Colors.YELLOW}警告：无法自动确定脚本路径，存档将保存在当前工作目录的 'saving' 文件夹下。{Colors.RESET}")
    SCRIPT_FOLDER_PATH = os.getcwd() 
    current_working_dir = os.getcwd()
    saving_folder_path = os.path.join(current_working_dir, "saving")
    os.makedirs(saving_folder_path, exist_ok=True)
    SAVE_FILE_NAME = "adventure_save.json"
    SAVE_FILE = os.path.join(saving_folder_path, SAVE_FILE_NAME)

SCREEN_WIDTH = 80

# --- 辅助函数 ---
def load_sound(sound_name):
    if not SOUND_ENABLED: return None
    if sound_name in LOADED_SOUNDS: return LOADED_SOUNDS[sound_name]
    
    file_basename = SOUND_FILES.get(sound_name)
    if not file_basename:
        if sound_name == "default_beep": return "BEEP_PLACEHOLDER"
        return None

    sounds_dir = os.path.join(SCRIPT_FOLDER_PATH, "sounds")
    full_file_path = os.path.join(sounds_dir, file_basename)

    if os.path.exists(full_file_path):
        try:
            sound = pygame.mixer.Sound(full_file_path)
            LOADED_SOUNDS[sound_name] = sound; return sound
        except pygame.error as e:
            print(f"{Colors.YELLOW}警告：无法加载音效 '{sound_name}' 从 '{full_file_path}': {e}{Colors.RESET}")
    # else: # 您注释掉了这个else块，我保持原样
    #     print(f"{Colors.YELLOW}警告：音效文件 '{full_file_path}' (为 '{sound_name}' 定义) 未找到。{Colors.RESET}")
    return None

def play_sound_effect(sound_name, loop=False, channel_obj=None, volume=1.0):
    if not SOUND_ENABLED:
        if sound_name in ["item_pickup", "action_fail", "puzzle_solve", "default_beep"]:
            beeps = {"item_pickup":1, "action_fail":2, "puzzle_solve":3, "default_beep":1}
            for _ in range(beeps.get(sound_name,0)): print("\a", end="", flush=True)
        return

    sound_obj = load_sound(sound_name)
    if sound_obj == "BEEP_PLACEHOLDER": print("\a", end="", flush=True); return
        
    if sound_obj:
        try:
            sound_obj.set_volume(volume); loops = -1 if loop else 0
            target_channel = channel_obj if channel_obj else pygame.mixer.find_channel()
            if target_channel: target_channel.play(sound_obj, loops=loops)
            else: sound_obj.play(loops=loops)
        except pygame.error as e: print(f"{Colors.YELLOW}播放音效 '{sound_name}' 时出错: {e}{Colors.RESET}")

def stop_ambient_sound():
    global AMBIENT_CHANNEL
    if SOUND_ENABLED and AMBIENT_CHANNEL and AMBIENT_CHANNEL.get_busy(): AMBIENT_CHANNEL.fadeout(500)

def print_slow(text, delay=0.02, color=None, bold=False, on_complete_sound=None):
    styled_text = f"{Colors.BOLD if bold else ''}{color if color else ''}{text}{Colors.RESET if color or bold else ''}"
    for char in styled_text: print(char, end='', flush=True); time.sleep(delay)
    print()
    if on_complete_sound: play_sound_effect(on_complete_sound)

def display_header(title):
    print_slow("=" * SCREEN_WIDTH, color=Colors.CYAN, bold=True, delay=0.005)
    print_slow(title.center(SCREEN_WIDTH), color=Colors.YELLOW, bold=True, delay=0.01)
    print_slow("=" * SCREEN_WIDTH, color=Colors.CYAN, bold=True, delay=0.005); print()

def display_ascii_art(art_name, play_sound=None):
    art = ASCII_ARTS.get(art_name)
    if art: print(art); time.sleep(0.1)
    if play_sound: play_sound_effect(play_sound)

# --- 新增：用于TTS的辅助函数 ---
def speak_dialogue_mac(text, voice_name=None, blocking=False):
    """在macOS上使用 'say' 命令进行文本转语音。"""
    if platform.system() == "Darwin": # 仅在 macOS 上执行
        try:
            # 简单清理文本中的引号，避免破坏shell命令
            # 对于更复杂的文本，可能需要更完善的清理库或方法
            sanitized_text = text.replace('"', '').replace("'", "").replace(";", "").replace("`", "")
            
            command = f"say"
            if voice_name: # 例如 "Ting-Ting" (一个常用的macOS中文女声)
                command += f" -v \"{voice_name}\""
            command += f" \"{sanitized_text}\"" # 将文本放在最后，并用引号括起来
            
            if not blocking:
                command += " &" # 后台播放，不阻塞游戏主线程

            os.system(command)
            return True
        except Exception as e:
            display_message(f"警告：使用 'say' 命令播放语音时出错: {e}", color=Colors.YELLOW, slow=False)
    # else: # 如果不是macOS，可以选择不发出声音或播放一个通用提示音（如果pygame可用）
    #     if SOUND_ENABLED: play_sound_effect("default_beep")
    return False


def display_message(message, wrapped=True, color=Colors.WHITE, bold=False, slow=True, sound_event=None, delay=None):
    print_slow_kwargs = {}
    if delay is not None: print_slow_kwargs['delay'] = delay
    if slow:
        if wrapped:
            lines = textwrap.wrap(message, SCREEN_WIDTH)
            for i, line in enumerate(lines):
                current_sound = sound_event if i == len(lines) - 1 else None
                print_slow(line, color=color, bold=bold, on_complete_sound=current_sound, **print_slow_kwargs)
        else:
            print_slow(message, color=color, bold=bold, on_complete_sound=sound_event, **print_slow_kwargs)
    else:
        formatted_message = c_text(message, color, bold)
        if wrapped: print("\n".join(textwrap.wrap(formatted_message, SCREEN_WIDTH)))
        else: print(formatted_message)
        if sound_event: play_sound_effect(sound_event)
        print()

def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

# --- 游戏对象定义 ---
class Item:
    def __init__(self, name, description, takeable=True, use_on=None, effect_description=None, ascii_art_name=None):
        self.name = name.lower(); self.display_name = name
        self.description = description; self.takeable = takeable
        self.use_on = use_on; self.effect_description = effect_description
        self.ascii_art_name = ascii_art_name
    def __str__(self): return self.name
    def examine(self):
        if self.ascii_art_name: display_ascii_art(self.ascii_art_name)
        return self.description

class Room:
    def __init__(self, name, description, items=None, npcs=None, properties=None, ascii_art_on_enter=None, ambient_sound=None):
        self.name = name; self.display_name = name.replace('_', ' ').title()
        self.description = description; self.exits = {}
        self.items = items if items else []; self.npcs = npcs if npcs else []
        self.properties = properties if properties else {}
        self.ascii_art_on_enter = ascii_art_on_enter; self.visited_art_shown = False
        self.ambient_sound = ambient_sound; self.monsters = []
    def add_exit(self, direction, room_id): self.exits[direction.lower()] = room_id
    def get_description_elements(self):
        header = f"--- {c_text(self.display_name, Colors.CYAN, bold=True)} ---"; desc_text = self.description
        items_text_list = []
        if self.items:
            items_text_list.append(f"\n你看到这里有：")
            for item in self.items: items_text_list.append(f"  - {c_text(item.display_name, Colors.BLUE)}")
        npcs_text_list = []
        if self.npcs:
            npcs_text_list.append(f"\n这里有：")
            for npc_obj in self.npcs: npcs_text_list.append(f"  - {c_text(npc_obj.name, Colors.MAGENTA)}")
        exits_header = "\n可用的出口："
        exits_list_text = ", ".join([c_text(d.capitalize(), Colors.CYAN) for d in self.exits.keys()]) if self.exits else c_text("无", Colors.YELLOW)
        return header, desc_text, items_text_list, npcs_text_list, exits_header, exits_list_text
    def add_item(self, item):
        if isinstance(item, Item): self.items.append(item)
        else: display_message(f"调试：向房间 {self.name} 添加非Item对象: {item}", Colors.RED)
    def remove_item(self, item_name):
        item_name_lower = item_name.lower()
        for i, item_obj in enumerate(self.items):
            if item_obj.name == item_name_lower: return self.items.pop(i)
        return None
    def has_item(self, item_name): return any(item.name == item_name.lower() for item in self.items)

class NPC:
    def __init__(self, name, description, dialogue=None, inventory=None, ascii_art_name=None, tts_voice_name=None): # 新增 tts_voice_name
        self.name = name; self.description = description
        self.dialogue = dialogue if dialogue else {"default": "这个角色似乎没什么好说的."}
        self.inventory = inventory if inventory else []; self.ascii_art_name = ascii_art_name
        self.health = 100; self.attack_power = 10; self.defense_power = 5; self.hostile = False
        self.tts_voice_name = tts_voice_name # 例如 "Ting-Ting"
    def talk(self, topic="default"): return self.dialogue.get(topic.lower(), self.dialogue.get("default", "嗯？我不明白你的意思。"))
    def examine(self):
        if self.ascii_art_name: display_ascii_art(self.ascii_art_name)
        return self.description

class Player:
    def __init__(self, start_room_id):
        self.current_room_id = start_room_id; self.inventory = []
        self.health = 100; self.score = 0; self.history = []; self.pets = []
    def add_to_inventory(self, item):
        self.inventory.append(item);
        display_message(f"你将 [{c_text(item.display_name, Colors.BLUE, bold=True)}] 加入了物品栏。", Colors.GREEN, sound_event="item_pickup")
        if item.ascii_art_name: display_ascii_art(item.ascii_art_name)
    def remove_from_inventory(self, item_name):
        item_name_lower = item_name.lower()
        for i, item_obj in enumerate(self.inventory):
            if item_obj.name == item_name_lower: return self.inventory.pop(i)
        return None
    def has_item(self, item_name): return any(item.name == item_name.lower() for item in self.inventory)
    def display_inventory(self):
        if not self.inventory: display_message("你的物品栏是空的。", Colors.YELLOW); return
        display_message("你的物品栏里有：", Colors.WHITE, True, False)
        for item in self.inventory: print_slow(f"  - {c_text(item.display_name, Colors.BLUE)}", delay=0.01)
        print()

# --- 游戏主类 ---
class Game:
    def __init__(self):
        self.player = None; self.rooms = {}; self.items = {}; self.npcs = {}
        self.is_running = True; self.autoplay_mode = False; self.autoplay_commands = []
        self.autoplay_command_index = 0; self.autoplay_delay = 0.7
        self._setup_world()

    def _add_item_definition(self, item): self.items[item.name.lower()] = item
    def _add_npc_definition(self, npc_id, npc_obj): self.npcs[npc_id.lower()] = npc_obj

    def _setup_world(self):
        self._add_item_definition(Item("生锈的钥匙", "一把看起来很旧的生锈铁钥匙。", True))
        self._add_item_definition(Item("古老的地图", "一张羊皮纸地图。", True))
        self._add_item_definition(Item("火把", "一个未点燃的火把。", True, use_on="壁炉", effect_description="火把被点燃了！", ascii_art_name="torch_art"))
        self._add_item_definition(Item("点燃的火把", "一个燃烧着的火把。", False, ascii_art_name="lit_torch_art"))
        self._add_item_definition(Item("撬棍", "一根结实的金属撬棍。", True))
        self._add_item_definition(Item("治疗药水", "一瓶红色发光的液体。", True))
        self._add_item_definition(Item("远古神像", "一个黑色石头雕刻的小神像。", True))
        self._add_item_definition(Item("绳子", "一捆结实的绳子。", True))
        self._add_item_definition(Item("布满灰尘的书", "一本厚重的古书。", True))

        ASCII_ARTS["fireplace_cold"] = ASCII_ARTS["fireplace_cold_art"]
        ASCII_ARTS["fireplace_lit"] = ASCII_ARTS["fireplace_lit_art"]
        ASCII_ARTS["door_closed"] = ASCII_ARTS["door_closed_art"]
        ASCII_ARTS["door_open"] = ASCII_ARTS["door_open_art"]

        doujiang_dialogue = {
            "default": "年轻人，此地凶险，亦藏机缘。心有所向，不妨一问。",
            "世界观": "这片土地，曾是古代文明的摇篮，星辰之力曾在此交汇。然盛极而衰，一场未知的灾变使得辉煌化为尘土，只余下被遗忘的传说和守护着秘密的遗迹。无数探险者被宝藏的低语吸引而来，但多数人，或迷失于机关，或臣服于诱惑，最终成为了这片土地无声历史的一部分。",
            "金句": "流斗桨，莫问何处是归航；风波恶，心有航灯破万浪。年轻人，愿你的智慧如星辰指引，勇气如磐石坚定。",
            "宝藏": "那远古的秘宝？呵呵，它既是无上智慧的钥匙，也可能是开启疯狂的魔盒。传说它藏匿于洞穴最深处，被复杂的机关和扭曲的意志所守护。唯有真正理解其价值的人，方能窥其一二。",
            
            # --- 新增/修改的语录 ---
            "关于你自己": "吾乃此间一孤舟，一斗桨，渡人亦渡己。名号早已随风逝，唤我'斗桨'足矣。我见证了太多旅人的到来与离去，希望你不是下一个匆匆的过客。",
            "此地危险": "危险？此地危机四伏，不仅有失落文明遗留的致命机关，更有因秘宝力量而扭曲的生灵徘徊。但年轻人，真正的危险往往源于内心的贪婪与恐惧，而非外界的险阻。",
            "线索提示": "万物皆有言，只待有心人。一卷古图，残破石碑，乃至风中低语，皆可能藏着通往真相的丝缕。耐心与细致的观察，是冒险者在这片迷雾中最好的罗盘。有时，最不起眼的角落，反而藏着关键。",
            "火种的重要性": "在这伸手不见五指的黑暗中，即便是微弱的火光，亦能成为指引方向的希望。善用你的光源，它能为你驱散迷雾，但也可能引来不必要的注意。",
            "古老文明的警示": "他们曾追逐星辰之力，试图掌握超越凡俗的力量。他们的智慧曾照亮时代，但也因无度和傲慢播下了毁灭的种子。这片废墟，便是对后来者无声的警示。",
            "命运的启示": "命运如湍流，时而汹涌，时而平缓。真正的舵手，并非一味顺流而下，而是在浪涛中稳住自己的航向，哪怕这意味着逆水行舟，亦勇往直前。",
            "抉择的重量": "每一次选择，都如同在命运的棋盘上落下一子。看似微小，却可能牵动全局的走向。谨慎对待你的每一个决定，因为棋局一旦开始，便没有回头路。",
            "星辰的低语": "我曾于星夜静观天象，古老的星辰低语着一些被遗忘的名字，和即将到来的时代。它们说，有些灵魂如同暗夜中的灯塔，即便微弱，也能指引方向。我似乎听到了一个名字的回响...或许是‘张本意涵’？时间的长河会揭示一切奥秘。", # 尝试融入特定名字
            # --- 结束新增/修改 ---
            
            "再见": "去吧，愿你好运，年轻人。若有缘，自会再见。记住，选择比寻找更重要。"
        }
        mr_doujiang = NPC(name="斗桨先生", 
                          description="一位头戴斗笠、身披蓑衣的老者。他眼神深邃，手中总是稳稳地握着一根看似普通的船桨。", 
                          dialogue=doujiang_dialogue,
                          tts_voice_name="Ting-Ting") # 为斗桨先生指定TTS语音
        self._add_npc_definition("斗桨先生", mr_doujiang)

        room_cabin = Room(name="cabin", description="废弃小屋。\n你发现自己在一个摇摇欲坠的废弃小屋里。尘土飞扬，空气中弥漫着霉味。角落里有一个冰冷的[壁炉]。一张破旧的[桌子]放在房间中央。", items=[self.items['火把'], self.items['古老的地图']], npcs=[self.npcs['斗桨先生']], properties={'has_fireplace': True, 'table_searched': False, "fireplace_lit": False}, ambient_sound="ambient_windy")
        room_cabin.add_exit("北", "forest_path"); room_cabin.add_exit("东", "dark_cellar_entrance"); self.rooms["cabin"] = room_cabin
        # ... (其他房间定义保持不变，您可以为它们也添加 tts_voice_name 如果需要)

        room_forest_path = Room(name="forest_path", description="森林小径。\n你来到一条蜿蜒的森林小径。高大的树木遮天蔽日。地上散落着一些[枯叶]。", items=[], properties={'leaves_searched': False, 'key_found_here': True}, ambient_sound="ambient_forest")
        room_forest_path.add_exit("南", "cabin"); room_forest_path.add_exit("北", "deep_forest"); room_forest_path.add_exit("西", "river_bank"); self.rooms["forest_path"] = room_forest_path
        room_dark_cellar_entrance = Room(name="dark_cellar_entrance", description="黑暗的地下室入口。\n这是一段通往地下的楼梯，非常黑暗。你需要[光源]才能下去。一扇[木门]紧闭着。", properties={'requires_light': True, 'door_locked': True})
        room_dark_cellar_entrance.add_exit("西", "cabin"); self.rooms["dark_cellar_entrance"] = room_dark_cellar_entrance
        room_cellar = Room(name="cellar", description="阴暗的地下室。\n地下室里阴冷潮湿。墙角堆放着一些破旧的[木箱]。一个[远古神像]放在一个石台上。", items=[self.items['远古神像']], properties={'crates_searched': False, 'crowbar_found_here': True}, ambient_sound="ambient_cave")
        room_cellar.add_exit("上", "dark_cellar_entrance"); self.rooms["cellar"] = room_cellar
        room_deep_forest = Room(name="deep_forest", description="森林深处。\n你越往森林深处走，光线就越暗。这里似乎有一个隐蔽的[洞穴入口]。", items=[self.items['治疗药水']], properties={'cave_hidden': True}, ambient_sound="ambient_forest")
        room_deep_forest.add_exit("南", "forest_path"); room_deep_forest.add_exit("进入洞穴", "cave_entrance"); self.rooms["deep_forest"] = room_deep_forest
        room_cave_entrance = Room(name="cave_entrance", description="洞穴入口。\n这是一个黑暗的洞穴入口，里面吹出阵阵冷风。洞壁上刻着一些奇怪的[符号]。", items=[self.items['布满灰尘的书']], properties={'symbols_deciphered': False}, ascii_art_on_enter="cave_entrance", ambient_sound="ambient_cave")
        room_cave_entrance.add_exit("离开洞穴", "deep_forest"); room_cave_entrance.add_exit("深入洞穴", "cave_chamber"); self.rooms["cave_entrance"] = room_cave_entrance
        room_cave_chamber = Room(name="cave_chamber", description="洞穴密室。\n在洞穴的深处，你发现了一个宽敞的密室。密室中央有一个古老的[石棺]。旁边散落着一些[金币]。", items=[], properties={'treasure_found': False, 'coffin_opened': False}, ambient_sound="ambient_cave")
        room_cave_chamber.add_exit("离开密室", "cave_entrance"); self.rooms["cave_chamber"] = room_cave_chamber
        
        self.player = Player(start_room_id="cabin")

    def _handle_initial_npc_dialogue(self):
        current_room = self.rooms.get(self.player.current_room_id)
        if current_room and current_room.name == "cabin":
            for npc in current_room.npcs:
                if npc.name == "斗桨先生":
                    display_message(f"\n你看到一位{c_text(npc.name, Colors.MAGENTA, bold=True)}站在小屋的阴影中，他缓缓开口：", slow=False)
                    time.sleep(0.5) # 给玩家一点反应时间
                    
                    dialogue_sequence = [
                        ("世界观", npc.talk("世界观"), Colors.WHITE, 0.035),
                        ("金句", npc.talk("金句"), Colors.YELLOW, 0.045)
                    ]
                    
                    for topic, text, color, delay_speed in dialogue_sequence:
                        # 尝试播放语音
                        if npc.tts_voice_name: # 检查NPC是否有指定的TTS语音
                            speak_dialogue_mac(text, voice_name=npc.tts_voice_name, blocking=False)
                        
                        # 逐行慢速打印文本
                        for line_text in text.split('\n'):
                            display_message(f"{c_text(npc.name, Colors.MAGENTA)}: \"{line_text}\"", 
                                            color=color, 
                                            bold=(color==Colors.YELLOW), 
                                            slow=True, 
                                            delay=delay_speed)
                        time.sleep(0.4) # 每段完整对话（如世界观、金句）之间的小停顿
                    
                    display_message(f"{c_text(npc.name, Colors.MAGENTA)}点了点头，不再多言。", color=Colors.WHITE)
                    break 

    def load_and_start_autoplay(self, filename):
        command_file_path = ""; script_dir = SCRIPT_FOLDER_PATH
        try:
            commands_from_file = []
            path_in_script_folder = os.path.join(script_dir, filename)
            path_in_saving_folder = os.path.join(os.path.dirname(SAVE_FILE), filename)
            if os.path.exists(path_in_script_folder): command_file_path = path_in_script_folder
            elif os.path.exists(path_in_saving_folder): command_file_path = path_in_saving_folder
            elif os.path.exists(filename): command_file_path = filename
            else: display_message(f"错误：找不到指令集文件 '{filename}'", Colors.RED, False, sound_event="action_fail"); return
            with open(command_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    command_part = line.split('#', 1)[0].strip()
                    if command_part: commands_from_file.append(command_part)
            self.autoplay_commands = commands_from_file
            if not self.autoplay_commands: display_message(f"指令集 '{filename}' 为空。", Colors.YELLOW, False); return
            self.autoplay_mode = True; self.autoplay_command_index = 0
            display_message(f"开始自动播放 '{os.path.basename(command_file_path)}'...", Colors.MAGENTA, True)
        except Exception as e: display_message(f"加载指令集 '{filename}' 出错: {e}", Colors.RED, False, sound_event="action_fail")

    def start_game(self):
        clear_screen(); display_header(GAME_TITLE)
        if os.path.exists(os.path.dirname(SAVE_FILE)): display_message(f"提示：存档在: {c_text(SAVE_FILE, Colors.YELLOW)}", slow=False)
        display_message("欢迎来到《迷失的宝藏猎人》！输入 '帮助' 查看指令。", Colors.GREEN, True)
        self.look_around()
        self._handle_initial_npc_dialogue()
        while self.is_running:
            try:
                current_room = self.rooms.get(self.player.current_room_id)
                if not current_room:
                    display_message(f"错误：玩家在无效房间 '{self.player.current_room_id}'", Colors.RED, False, sound_event="action_fail")
                    self.is_running = False; break
                command_input_source = ""; command_input = ""
                if self.autoplay_mode:
                    if self.autoplay_command_index < len(self.autoplay_commands):
                        command_input = self.autoplay_commands[self.autoplay_command_index]; self.autoplay_command_index += 1
                        print(f"\n{Colors.MAGENTA}> (自动) {command_input}{Colors.RESET}"); command_input_source = "auto"
                    else:
                        display_message("自动播放完毕。恢复手动。", Colors.MAGENTA, False); self.autoplay_mode = False
                        command_input = input(f"\n{Colors.GREEN}> {Colors.RESET}").strip().lower(); command_input_source = "manual_after_auto"
                else:
                    command_input = input(f"\n{Colors.GREEN}> {Colors.RESET}").strip().lower(); command_input_source = "manual"
                if not command_input and command_input_source != "auto": continue
                
                self.player.history.append(f"({command_input_source}) {command_input}")
                self.process_command(command_input)
                if self.autoplay_mode and command_input_source == "auto": time.sleep(self.autoplay_delay)
                
                if self.check_win_condition():
                    display_message("\n恭喜！你找到了远古神像并打开了石棺，揭开了宝藏的秘密！游戏胜利！", Colors.GREEN, True, sound_event="puzzle_solve")
                    display_ascii_art("treasure_chest_open"); self.is_running = False
                elif self.player.health <= 0:
                    display_message("\n你的生命值耗尽了...游戏结束。", Colors.RED, True, sound_event="action_fail")
                    display_ascii_art("game_over"); self.is_running = False
            except KeyboardInterrupt:
                if self.autoplay_mode: display_message("\n自动播放已中断。", Colors.YELLOW, False); self.autoplay_mode = False
                else: display_message("\n你选择退出游戏。", Colors.YELLOW, False); self.is_running = False
            except Exception as e: display_message(f"发生意外错误: {e}", Colors.RED, False, sound_event="action_fail"); import traceback; traceback.print_exc()
        stop_ambient_sound()

    def process_command(self, command_input):
        parts = command_input.split(); action = parts[0] if parts else ""
        target_full = " ".join(parts[1:]) if len(parts) > 1 else None
        if not action: return

        if action == "talk" and parts[1:2] == ["to"] and len(parts) >= 3:
            npc_name_parts = []; topic = "default"; parsing_npc_name = True
            for i in range(2, len(parts)):
                if parts[i].lower() == "about" and i + 1 < len(parts):
                    parsing_npc_name = False; topic = " ".join(parts[i+1:]); break
                if parsing_npc_name: npc_name_parts.append(parts[i])
            npc_name_target = " ".join(npc_name_parts)
            if npc_name_target: self.talk_to_npc(npc_name_target, topic)
            else: display_message("你想和谁说话？", Colors.YELLOW, False)
            return

        if action in ["go", "move", "walk", "run", "travel"]:
            if target_full: self.move_player(target_full)
            else: display_message("去哪个方向？", Colors.YELLOW, False)
        elif self.player.current_room_id in self.rooms and action in self.rooms[self.player.current_room_id].exits:
             self.move_player(action)
        elif action in ["look", "examine", "inspect", "l"]:
            if target_full: self.examine_target(target_full)
            else: self.look_around()
        elif action in ["take", "get", "pickup", "grab"]:
            if target_full: self.take_item(target_full)
            else: display_message("拿什么？", Colors.YELLOW, False, sound_event="action_fail")
        elif action in ["drop", "discard"]:
            if target_full: self.drop_item(target_full)
            else: display_message("丢什么？", Colors.YELLOW, False, sound_event="action_fail")
        elif action in ["use", "apply"]:
            if target_full:
                item_name_to_use = "" ; on_what_target = None
                if "on" in parts:
                    try: on_idx = parts.index("on"); item_name_to_use = " ".join(parts[1:on_idx]); on_what_target = " ".join(parts[on_idx+1:])
                    except ValueError: item_name_to_use=target_full
                else: item_name_to_use = target_full
                if not item_name_to_use: display_message("用什么物品？", Colors.YELLOW, False); return
                self.use_item(item_name_to_use, on_what_target)
            else: display_message("用什么物品？", Colors.YELLOW, False, sound_event="action_fail")
        elif action == "inventory" or action == "i": self.player.display_inventory()
        elif action == "search":
            if target_full: self.search_target(target_full)
            else: display_message("搜索什么？", Colors.YELLOW, False, sound_event="action_fail")
        elif action in ["help", "h", "?", "commands"]: self.display_help()
        elif action in ["quit", "exit", "q"]: self.quit_game()
        elif action in ["save"]: self.save_game()
        elif action in ["load"]: self.load_game()
        elif action == "autoplay":
            if self.autoplay_mode: display_message("自动播放在进行中。", Colors.YELLOW, False)
            elif target_full: self.load_and_start_autoplay(target_full)
            else: display_message("请提供指令集文件名。", Colors.YELLOW, False, sound_event="action_fail")
        elif action == "stopautoplay":
            if self.autoplay_mode: self.autoplay_mode = False; self.autoplay_commands = []; self.autoplay_command_index = 0; display_message("自动播放已停止。", Colors.MAGENTA, False)
            else: display_message("未在自动播放模式。", Colors.YELLOW, False)
        elif action == "unlock" and target_full:
            item_used_for_unlock = None; target_to_unlock_name = target_full
            if "with" in parts:
                try: with_idx = parts.index("with"); target_to_unlock_name = " ".join(parts[1:with_idx]); item_used_for_unlock = " ".join(parts[with_idx+1:])
                except ValueError: pass
            if not item_used_for_unlock : display_message("用什么解锁？", Colors.YELLOW, False, sound_event="action_fail"); return
            self.unlock_target_with_item(target_to_unlock_name, item_used_for_unlock)
        elif action == "open" and target_full: self.open_target(target_full)
        else:
            if not (action == "talk" and parts[1:2] == ["to"]):
                 display_message(f"我不明白 '{c_text(command_input, Colors.YELLOW)}'. 输入 '帮助' 查看。", Colors.RED, False, sound_event="action_fail")

    def talk_to_npc(self, npc_name_input, topic="default"):
        current_room = self.rooms.get(self.player.current_room_id)
        if not current_room: self.look_around(); return
        npc_target = None; npc_name_input_lower = npc_name_input.lower()
        for npc_obj in current_room.npcs:
            if npc_obj.name.lower() == npc_name_input_lower: npc_target = npc_obj; break
        if npc_target:
            if npc_target.ascii_art_name: display_ascii_art(npc_target.ascii_art_name)
            
            dialogue_text = npc_target.talk(topic) 

            # --- 调用 TTS 播放语音 ---
            if npc_target.name == "斗桨先生" and npc_target.tts_voice_name: # 检查是否有指定的TTS语音
                # 为了更好的同步，将整个对话文本一次性传递给TTS
                full_dialogue_for_tts = dialogue_text 
                # 如果对话文本可能包含换行，TTS通常能处理，但speak_dialogue_mac中的清理可能需要注意
                speak_dialogue_mac(full_dialogue_for_tts, voice_name=npc_target.tts_voice_name, blocking=False)
            
            # 逐行慢速打印文本
            for line_text in dialogue_text.split('\n'):
                display_message(f"{c_text(npc_target.name, Colors.MAGENTA, bold=True)} 说: \"{line_text}\"", 
                                color=Colors.WHITE, 
                                slow=True, 
                                delay=0.05) # 可以为NPC对话设置一个统一的文本速度
            
            if topic.lower() == "再见" and not (npc_target.name == "斗桨先生" and npc_target.tts_voice_name): 
                 play_sound_effect("default_beep") 
        else: display_message(f"这里没有 '{c_text(npc_name_input, Colors.YELLOW)}' 可以对话。", Colors.YELLOW, False, sound_event="action_fail")

    def look_around(self): 
        current_room = self.rooms.get(self.player.current_room_id)
        if not current_room: display_message(f"错误: 当前房间 '{self.player.current_room_id}' 未找到!", Colors.RED, False, sound_event="action_fail"); return
        stop_ambient_sound()
        if current_room.ambient_sound:
            global AMBIENT_CHANNEL
            if SOUND_ENABLED and pygame.mixer.get_init(): 
                if not AMBIENT_CHANNEL and pygame.mixer.get_num_channels() > 0: AMBIENT_CHANNEL = pygame.mixer.Channel(0)
                if AMBIENT_CHANNEL : play_sound_effect(current_room.ambient_sound, loop=True, channel_obj=AMBIENT_CHANNEL, volume=0.3)

        if current_room.ascii_art_on_enter and not current_room.visited_art_shown:
            display_ascii_art(current_room.ascii_art_on_enter); current_room.visited_art_shown = True
        header, desc_text, items_text_list, npcs_text_list, exits_header, exits_list_text = current_room.get_description_elements()
        print_slow(header, delay=0.005)
        print_slow(desc_text, delay=0.02)
        for line in items_text_list: print_slow(line, delay=0.01)
        for line in npcs_text_list: print_slow(line, delay=0.01)
        print_slow(exits_header + " " + exits_list_text, delay=0.01); print()

    def examine_target(self, target_name_input): 
        target_name_lower = target_name_input.lower(); current_room = self.rooms.get(self.player.current_room_id)
        if not current_room: self.look_around(); return
        for item_obj in self.player.inventory:
            if item_obj.name == target_name_lower or item_obj.display_name.lower() == target_name_lower:
                display_message(f"你仔细检查了 [{c_text(item_obj.display_name, Colors.BLUE, True)}]:",color=Colors.WHITE, slow=False); display_message(item_obj.examine()); return
        for item_obj in current_room.items:
            if item_obj.name == target_name_lower or item_obj.display_name.lower() == target_name_lower:
                display_message(f"你看到一个 [{c_text(item_obj.display_name, Colors.BLUE, True)}]:",color=Colors.WHITE, slow=False); display_message(item_obj.examine()); return
        for npc_obj in current_room.npcs:
            if npc_obj.name.lower() == target_name_lower:
                display_message(f"你仔细观察 {c_text(npc_obj.name, Colors.MAGENTA, True)}:",color=Colors.WHITE, slow=False); display_message(npc_obj.examine()); return
        feature_examined = False
        if current_room.name == "cabin":
            if "壁炉" in target_name_lower or "fireplace" in target_name_lower:
                art = "fireplace_lit" if current_room.properties.get("fireplace_lit") else "fireplace_cold"; display_ascii_art(art)
                desc = "壁炉里火焰熊熊。" if current_room.properties.get("fireplace_lit") else "一个冰冷的石头壁炉。"
                display_message(desc); feature_examined = True
            elif "桌子" in target_name_lower: display_message("一张摇摇晃晃的旧木桌。"); feature_examined = True
        if current_room.name == "dark_cellar_entrance" and ("门" in target_name_lower or "door" in target_name_lower):
            art = "door_open" if not current_room.properties.get("door_locked") else "door_closed"; display_ascii_art(art)
            desc = "门是开着的。" if not current_room.properties.get("door_locked") else "一扇厚重的木门，紧锁着。"
            display_message(desc); feature_examined = True
        if feature_examined: return
        display_message(f"这里没有 '{c_text(target_name_input, Colors.YELLOW)}' 可以检查。", Colors.YELLOW, False)

    def move_player(self, direction): 
        current_room = self.rooms.get(self.player.current_room_id);
        if not current_room: self.look_around(); return
        direction_lower = direction.lower()
        if direction_lower in current_room.exits:
            next_room_id = current_room.exits[direction_lower]; next_room = self.rooms.get(next_room_id)
            if not next_room: display_message(f"错误：目标房间 '{next_room_id}' 未定义！", Colors.RED, False, sound_event="action_fail"); return
            if current_room.name == "dark_cellar_entrance" and direction_lower == "下":
                if current_room.properties.get('door_locked', True): display_message("门是锁着的。", Colors.YELLOW, False, sound_event="action_fail"); return
                if not self.player.has_item("点燃的火把") and next_room.properties.get('requires_light', False): display_message("太暗了，需要光源。", Colors.YELLOW, False, sound_event="action_fail"); return
            if current_room.name == "deep_forest" and direction_lower == "进入洞穴" and current_room.properties.get('cave_hidden', True):
                display_message("这里没什么特别的。", Colors.YELLOW, False); return
            play_sound_effect("footsteps_stone", volume=0.5)
            self.player.current_room_id = next_room_id; self.look_around()
            if next_room.name == "deep_forest" and next_room.properties.get('cave_hidden', True):
                display_message("仔细观察后，你注意到一个被藤蔓遮掩的[洞穴入口]！", Colors.GREEN, True, sound_event="puzzle_solve")
                next_room.properties['cave_hidden'] = False
        else: display_message(f"不能往 ({direction.capitalize()}) 走。", Colors.RED, False, sound_event="action_fail")

    def take_item(self, item_name_input): 
        current_room = self.rooms.get(self.player.current_room_id);
        if not current_room: self.look_around(); return
        item_to_take = None; item_name_input_lower = item_name_input.lower()
        for room_item_obj in current_room.items:
            if room_item_obj.display_name.lower() == item_name_input_lower or room_item_obj.name == item_name_input_lower:
                item_to_take = room_item_obj; break
        if item_to_take:
            if item_to_take.takeable:
                removed = current_room.remove_item(item_to_take.name)
                if removed: self.player.add_to_inventory(removed) 
                else: display_message("拾取错误。", Colors.RED, False, sound_event="action_fail")
            else: display_message(f"不能拾取 [{c_text(item_to_take.display_name, Colors.BLUE)}].", Colors.YELLOW, False)
        else: display_message(f"这里没有 '{c_text(item_name_input, Colors.YELLOW)}'。", Colors.YELLOW, False, sound_event="action_fail")

    def drop_item(self, item_name_input): 
        item_name_input_lower = item_name_input.lower(); item_to_drop = None
        for inv_item in self.player.inventory:
            if inv_item.display_name.lower() == item_name_input_lower or inv_item.name == item_name_input_lower:
                item_to_drop = inv_item; break
        if item_to_drop:
            self.player.remove_from_inventory(item_to_drop.name)
            current_room = self.rooms.get(self.player.current_room_id)
            if current_room: current_room.add_item(item_to_drop); display_message(f"你丢下了 [{c_text(item_to_drop.display_name, Colors.BLUE)}].", Colors.WHITE, False)
            else: self.player.add_to_inventory(item_to_drop); display_message("错误: 无法确定房间。", Colors.RED, False)
        else: display_message(f"物品栏里没有 '{c_text(item_name_input, Colors.YELLOW)}'。", Colors.YELLOW, False, sound_event="action_fail")

    def search_target(self, target_name_input): 
        target_lower = target_name_input.lower(); current_room = self.rooms.get(self.player.current_room_id)
        if not current_room: self.look_around(); return
        if current_room.name == "cabin" and ("桌子" in target_lower or "desk" in target_lower):
            if not current_room.properties.get('table_searched', False):
                display_message("你仔细搜索了桌子。", slow=False); current_room.properties['table_searched'] = True
                if current_room.has_item('古老的地图'): display_message(f"桌上放着一张{c_text('[古老的地图]', Colors.BLUE)}。", Colors.WHITE, False)
                else: display_message("桌上没什么特别的。", Colors.YELLOW, False)
            else: display_message("已经搜索过桌子了。", Colors.YELLOW, False)
            return
        if current_room.name == "forest_path" and ("枯叶" in target_lower or "leaves" in target_lower):
            if not current_room.properties.get('leaves_searched', False):
                display_message("你在枯叶堆里翻找...", slow=False); current_room.properties['leaves_searched'] = True
                key_def = self.items.get('生锈的钥匙')
                if key_def and current_room.properties.get('key_found_here') and not current_room.has_item(key_def.name) and not self.player.has_item(key_def.name):
                    current_room.add_item(key_def); display_message(f"在枯叶下，你发现了一把{c_text('[生锈的钥匙]', Colors.BLUE, True)}！", Colors.GREEN, False, sound_event="item_pickup")
                else: display_message("枯叶下只有泥土。", Colors.YELLOW, False)
            else: display_message("已经搜索过枯叶了。", Colors.YELLOW, False)
            return
        if current_room.name == "cellar" and ("木箱" in target_lower or "crates" in target_lower):
            if not current_room.properties.get('crates_searched', False):
                display_message("你搜索了木箱...", slow=False); current_room.properties['crates_searched'] = True
                crowbar_def = self.items.get('撬棍')
                if crowbar_def and current_room.properties.get('crowbar_found_here') and not current_room.has_item(crowbar_def.name) and not self.player.has_item(crowbar_def.name):
                    current_room.add_item(crowbar_def); display_message(f"在一个箱子里找到了一根{c_text('[撬棍]', Colors.BLUE, True)}！", Colors.GREEN, False, sound_event="item_pickup")
                else: display_message("箱子是空的。", Colors.YELLOW, False)
            else: display_message("已经搜过箱子了。", Colors.YELLOW, False)
            return
        display_message(f"你搜索了 {c_text(target_name_input, Colors.YELLOW)}，但什么也没找到。", Colors.YELLOW, False)

    def use_item(self, item_name_input, use_on_target_name=None): 
        item_name_lower = item_name_input.lower(); item_to_use = None
        for inv_item in self.player.inventory:
            if inv_item.name == item_name_lower or inv_item.display_name.lower() == item_name_lower: item_to_use = inv_item; break
        if not item_to_use: display_message(f"你没有 [{c_text(item_name_input, Colors.YELLOW)}].", Colors.RED, False, sound_event="action_fail"); return
        current_room = self.rooms.get(self.player.current_room_id);
        if not current_room: self.look_around(); return
        target_lower = use_on_target_name.lower() if use_on_target_name else ""

        if item_to_use.name == "火把":
            if use_on_target_name and ("壁炉" in target_lower or "fireplace" in target_lower):
                if current_room.name == "cabin" and current_room.properties.get('has_fireplace') and not current_room.properties.get("fireplace_lit"):
                    display_message(f"你用{c_text('[壁炉]', Colors.YELLOW)}点燃了{c_text('[火把]', Colors.BLUE)}！", Colors.GREEN, False, sound_event="puzzle_solve")
                    display_ascii_art("fireplace_lit", play_sound="fire_crackle"); current_room.properties["fireplace_lit"] = True
                    self.player.remove_from_inventory(item_to_use.name); self.player.add_to_inventory(self.items["点燃的火把"])
                    dce = self.rooms.get("dark_cellar_entrance")
                    if dce: base="黑暗地下室入口。\n楼梯很暗。"; ds="门已开。" if not dce.properties.get('door_locked',True) else "一扇[木门]紧锁。"; ls="现在可用[点燃的火把]照路！"; dce.description=f"{base} {ds} {ls} 扶手有蜘蛛网。"
                elif current_room.properties.get("fireplace_lit"): display_message("壁炉已点燃。", Colors.YELLOW, False)
                else: display_message("这里没有壁炉。", Colors.YELLOW, False)
            else: display_message(f"想用{c_text('[火把]', Colors.BLUE)}点燃什么？", Colors.YELLOW, False)
            return
        if item_to_use.name == "治疗药水":
            self.player.health = min(100, self.player.health + 50); display_message("你喝下治疗药水，好多了！", Colors.GREEN, False, sound_event="item_pickup")
            display_message(f"(生命值: {c_text(str(self.player.health), Colors.GREEN, True)})", slow=False); self.player.remove_from_inventory(item_to_use.name); return
        if item_to_use.name == "生锈的钥匙": display_message(f"{c_text('[生锈的钥匙]', Colors.BLUE)}用来开锁。", Colors.YELLOW, False); return
        if item_to_use.name == "撬棍":
            if use_on_target_name and ("石棺" in target_lower or "coffin" in target_lower):
                 if current_room.name == "cave_chamber":
                     if not current_room.properties.get('coffin_opened', False):
                        display_message(f"你用{c_text('[撬棍]', Colors.BLUE)}撬开了{c_text('[石棺]',Colors.YELLOW)}！", Colors.GREEN, False, sound_event="puzzle_solve")
                        display_message(f"里面是空的！旁边有些{c_text('[金币]', Colors.YELLOW)}。", Colors.WHITE, False); current_room.properties['coffin_opened'] = True
                     else: display_message("石棺已打开。", Colors.YELLOW, False)
                 else: display_message(f"这里没有 '{c_text(use_on_target_name, Colors.YELLOW)}' 可撬。", Colors.RED, False)
            else: display_message(f"想用{c_text('[撬棍]', Colors.BLUE)}撬什么？", Colors.YELLOW, False)
            return
        if item_to_use.use_on and use_on_target_name and item_to_use.use_on.lower() == target_lower:
            if item_to_use.effect_description: display_message(item_to_use.effect_description, Colors.GREEN, False)
            else: display_message(f"对 {c_text(use_on_target_name, Colors.YELLOW)} 使用了 [{c_text(item_to_use.display_name, Colors.BLUE)}]. 效果不明显。", Colors.YELLOW, False)
        elif use_on_target_name: display_message(f"不能对 {c_text(use_on_target_name, Colors.YELLOW)} 使用 [{c_text(item_to_use.display_name, Colors.BLUE)}].", Colors.RED, False, sound_event="action_fail")
        else: display_message(f"使用了 [{c_text(item_to_use.display_name, Colors.BLUE)}]. 没什么反应。", Colors.YELLOW, False)

    def unlock_target_with_item(self, target_to_unlock_input, item_used_input): # Restored
        target_lower = target_to_unlock_input.lower(); item_used_lower = item_used_input.lower()
        current_room = self.rooms.get(self.player.current_room_id);
        if not current_room: self.look_around(); return
        item_for_unlock = next((i for i in self.player.inventory if i.name==item_used_lower or i.display_name.lower()==item_used_lower), None)
        if not item_for_unlock: display_message(f"你没有 [{c_text(item_used_input, Colors.YELLOW)}].", Colors.RED, False, sound_event="action_fail"); return

        if current_room.name == "dark_cellar_entrance" and ("门" in target_lower or "door" in target_lower):
            if current_room.properties.get('door_locked', True):
                if item_for_unlock.name == "生锈的钥匙":
                    display_message(f"你用{c_text('[生锈的钥匙]', Colors.BLUE, True)}打开了{c_text('[门]', Colors.YELLOW)}！", Colors.GREEN, False, sound_event="door_unlock")
                    display_ascii_art("door_open"); current_room.properties['door_locked'] = False; current_room.add_exit("下", "cellar")
                    base="黑暗地下室入口。\n楼梯很暗。"; ls="现在可用[点燃的火把]照路！" if self.player.has_item("点燃的火把") else "你需要[光源]。"; current_room.description=f"{base} 门已开。{ls} 扶手有蜘蛛网。"
                else: display_message(f"[{c_text(item_for_unlock.display_name, Colors.BLUE)}] 打不开这扇门。", Colors.RED, False, sound_event="action_fail")
            else: display_message("门已开。", Colors.YELLOW, False)
            return
        display_message(f"不能用 [{c_text(item_for_unlock.display_name, Colors.BLUE)}] 解锁 '{c_text(target_to_unlock_input, Colors.YELLOW)}'。", Colors.RED, False, sound_event="action_fail")

    def open_target(self, target_name_input): # Restored
        target_lower = target_name_input.lower(); current_room = self.rooms.get(self.player.current_room_id)
        if not current_room: self.look_around(); return
        if current_room.name == "dark_cellar_entrance" and ("门" in target_lower or "door" in target_lower):
            if not current_room.properties.get('door_locked', True): display_message("门已开。", Colors.YELLOW, False); display_ascii_art("door_open"); play_sound_effect("door_open")
            else: display_message("门锁着。", Colors.YELLOW, False, sound_event="action_fail"); display_ascii_art("door_closed")
            return
        if current_room.name == "cave_chamber" and ("石棺" in target_lower or "coffin" in target_lower):
            if current_room.properties.get('coffin_opened', False): display_message("石棺已打开。", Colors.YELLOW, False)
            else: display_message(f"石棺盖很重，打不开。也许需要[{c_text('工具', Colors.BLUE)}]？", Colors.YELLOW, False)
            return
        display_message(f"尝试打开 '{c_text(target_name_input, Colors.YELLOW)}' 失败。", Colors.RED, False, sound_event="action_fail")

    def display_help(self): # (As before)
        help_text = f"""
{Colors.BOLD}--- 帮助菜单 ---{Colors.RESET}
{c_text("常用指令:", Colors.GREEN, True)}
  go [方向]       - 向指定方向移动 (例如: go {c_text('north', Colors.CYAN)})
  look / l        - 查看当前环境
  examine {c_text('[目标]', Colors.BLUE)} - 仔细检查 (例如: examine {c_text('desk', Colors.YELLOW)})
  search {c_text('[目标]', Colors.YELLOW)} - 搜索 (例如: search {c_text('leaves', Colors.YELLOW)})
  take {c_text('[物品]', Colors.BLUE)}     - 拾取物品 (例如: take {c_text('key', Colors.BLUE)})
  drop {c_text('[物品]', Colors.BLUE)}     - 丢弃物品
  inventory / i   - 查看你的物品栏
  use {c_text('[物品]', Colors.BLUE)} (on {c_text('[目标]', Colors.YELLOW)}) - 使用物品
  unlock {c_text('[目标]', Colors.YELLOW)} with {c_text('[物品]', Colors.BLUE)} - 解锁
  open {c_text('[目标]', Colors.YELLOW)}     - 打开
  talk to {c_text('[NPC]', Colors.MAGENTA)} (about {c_text('[话题]', Colors.YELLOW)}) - 与NPC对话
{c_text("游戏指令:", Colors.GREEN, True)}
  save            - 保存游戏进度; load            - 读取游戏进度
  autoplay {c_text('[文件名]', Colors.MAGENTA)} - 自动执行指令集
  stopautoplay    - 停止自动播放
  help / h / ?    - 显示此帮助菜单; quit / q        - 退出游戏
{Colors.BOLD}提示:{Colors.RESET} 尝试与环境中的 [{c_text('方括号内的文字', Colors.YELLOW)}] 互动！"""
        print(help_text); print()

    def save_game(self): # (As before)
        game_state = {"player_room_id": self.player.current_room_id, "player_inventory": [i.name for i in self.player.inventory], "player_health": self.player.health, "player_score": self.player.score, "room_states": {}}
        for room_id, room_obj in self.rooms.items(): game_state["room_states"][room_id] = {"items_in_room": [i.name for i in room_obj.items], "properties": room_obj.properties.copy(), "exits": room_obj.exits.copy(), "description": room_obj.description, "visited_art_shown": room_obj.visited_art_shown, "ambient_sound": room_obj.ambient_sound}
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f: json.dump(game_state, f, indent=4, ensure_ascii=False)
            display_message(f"游戏进度已保存到 {c_text(SAVE_FILE, Colors.YELLOW)}", Colors.GREEN, False, sound_event="puzzle_solve")
        except IOError as e: display_message(f"错误：无法保存游戏！ {e}", Colors.RED, False, sound_event="action_fail")

    def load_game(self): # (As before)
        if not os.path.exists(SAVE_FILE): display_message(f"没有找到存档: {c_text(SAVE_FILE, Colors.YELLOW)}", Colors.RED, False, sound_event="action_fail"); return
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f: game_state = json.load(f)
            self._setup_world()
            self.player.current_room_id = game_state.get("player_room_id", "cabin")
            self.player.health = game_state.get("player_health", 100); self.player.score = game_state.get("player_score", 0)
            self.player.inventory = [self.items[name.lower()] for name in game_state.get("player_inventory", []) if name.lower() in self.items]
            loaded_room_states = game_state.get("room_states", {})
            for room_id, room_obj_to_restore in self.rooms.items():
                room_s_data = loaded_room_states.get(room_id)
                if room_s_data:
                    room_obj_to_restore.items = [self.items[name.lower()] for name in room_s_data.get("items_in_room", []) if name.lower() in self.items]
                    room_obj_to_restore.properties = room_s_data.get("properties", room_obj_to_restore.properties)
                    room_obj_to_restore.exits = room_s_data.get("exits", room_obj_to_restore.exits)
                    room_obj_to_restore.description = room_s_data.get("description", room_obj_to_restore.description)
                    room_obj_to_restore.visited_art_shown = room_s_data.get("visited_art_shown", False)
                    room_obj_to_restore.ambient_sound = room_s_data.get("ambient_sound", room_obj_to_restore.ambient_sound)
            stop_ambient_sound(); display_message("游戏进度已成功读取！", Colors.GREEN, False, sound_event="puzzle_solve"); self.look_around()
        except (IOError, json.JSONDecodeError) as e: display_message(f"错误：无法读取存档。({e})", Colors.RED, False, sound_event="action_fail")

    def check_win_condition(self): # (As before)
        treasure_room = self.rooms.get("cave_chamber")
        if self.player.current_room_id == "cave_chamber" and \
           treasure_room and treasure_room.properties.get('coffin_opened') and \
           self.player.has_item("远古神像"):
            treasure_room.properties['treasure_found'] = True; return True
        return False

    def quit_game(self): # (As before)
        display_message("你确定要退出游戏吗？(是/否)", Colors.YELLOW, True)
        if input(f"{Colors.GREEN}> {Colors.RESET}").strip().lower() in ["是", "yes", "y"]:
            stop_ambient_sound(); display_message("感谢游玩！再见。", Colors.MAGENTA, True); self.is_running = False
        else: display_message("游戏继续。", Colors.GREEN, False)

# --- 游戏入口点 ---
if __name__ == "__main__":
    print(f"{Colors.YELLOW}游戏加载中... {('音效已启用。' if SOUND_ENABLED else '音效未启用 (Pygame问题?)')} {Colors.RESET}\n")
    time.sleep(0.5)
    try:
        game_instance = Game()
        game_instance.start_game()
    except Exception as e:
        print(f"{Colors.RED}{Colors.BOLD}\n{'='*SCREEN_WIDTH}\n{'游戏发生严重错误，被迫中止。抱歉！'.center(SCREEN_WIDTH)}\n{f'错误详情: {e}'.center(SCREEN_WIDTH)}\n{'='*SCREEN_WIDTH}{Colors.RESET}")
        import traceback; traceback.print_exc()
    finally:
        if SOUND_ENABLED and pygame.mixer.get_init(): pygame.mixer.quit()