"""Game content: ASCII art, items, rooms, NPCs"""
from ..core.entities import Item, Room, NPC

ASCII_ARTS = {
    "cave_entrance": """
        .--""--.
       /        \\
      |  O    O  |
      |   .__.   |
       \\  `--'  /
        `------'
    一个深邃的洞穴入口若隐若现...
    """,
    "treasure_chest_open": """
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
    宝箱敞开着，闪耀着金光！
    """,
    "game_over": """
    ██████╗  █████╗ ███╗   ███╗ ███████╗
    ██╔══██╗██╔══██╗████╗ ████║ ██╔════╝
    ██║  ██║███████║██╔████╔██║ █████╗
    ██║  ██║██╔══██║██║╚██╔╝██║ ██╔══╝
    ██████╔╝██║  ██║██║ ╚═╝ ██║ ███████╗
    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚══════╝
    """,
    "torch_art": """
          ()
         ▐▐▐▐
        ▐▐███▌▌
        ███████
         █████
          ███
          ███
           V
    这是一支普通的火把。
    """,
    "lit_torch_art": """
      _(火焰)_
     (火焰)(_(火焰)_)(火焰)
    (火焰)(火焰)(火焰)(火焰)(火焰)
      ▐▐▐▐▐
      █████
      █████
     VVVVV
    火把熊熊燃烧着，发出噼啪声。
    """,
    "door_closed_art": """
    ┎-----┒
    ┃  == ┃
    ┃  || ┃
    ┃  == ┃
    ┖-----┚
    一扇紧闭的门。
    """,
    "door_open_art": """
    ┎-----\\
    ┃      🚪
    ┃
    ┃
    ┖------
    门是开着的。
    """,
    "fireplace_cold_art": """
      ,--''''--.
     /          \\
    |            |
     \\  ______  /
      `-|____|-'
    一个冰冷的壁炉。
    """,
    "fireplace_lit_art": """
     _(火焰)_
    (火焰)(_(火焰)_)(火焰)
   ,--''''--.
  /          \\
 | (火焰)(火焰)(火焰)  |
  \\  ______  /
   `-|____|-'
    壁炉里火焰跳动，很暖和。
    """,
}

def create_items():
    """Create all game items"""
    items = {}

    item_list = [
        Item("生锈的钥匙", "生锈的钥匙", "一把看起来很旧的生锈铁钥匙。", True, item_type="key"),
        Item("古老的地图", "古老的地图", "一张羊皮纸地图。", True, item_type="document"),
        Item("火把", "火把", "一个未点燃的火把。", True, use_on="壁炉",
             effect_description="火把被点燃了！", ascii_art_name="torch_art", item_type="tool"),
        Item("点燃的火把", "点燃的火把", "一个燃烧着的火把。", False,
             ascii_art_name="lit_torch_art", item_type="tool"),
        Item("撬棍", "撬棍", "一根结实的金属撬棍。", True, item_type="tool"),
        Item("治疗药水", "治疗药水", "一瓶红色发光的液体。", True, item_type="consumable", value=50),
        Item("远古神像", "远古神像", "一个黑色石头雕刻的小神像。", True, item_type="treasure", value=1000),
        Item("绳子", "绳子", "一捆结实的绳子。", True, item_type="tool"),
        Item("布满灰尘的书", "布满灰尘的书", "一本厚重的古书。", True, item_type="document"),
    ]

    for item in item_list:
        items[item.name] = item

    return items

def create_npcs():
    """Create all NPCs"""
    npcs = {}

    doujiang_dialogue = {
        "default": "年轻人，此地凶险，亦藏机缘。心有所向，不妨一问。",
        "世界观": "这片土地，曾是古代文明的摇篮，星辰之力曾在此交汇。然盛极而衰，一场未知的灾变使得辉煌化为尘土，只余下被遗忘的传说和守护着秘密的遗迹。",
        "金句": "流斗桨，莫问何处是归航；风波恶，心有航灯破万浪。年轻人，愿你的智慧如星辰指引，勇气如磐石坚定。",
        "宝藏": "那远古的秘宝？呵呵，它既是无上智慧的钥匙，也可能是开启疯狂的魔盒。传说它藏匿于洞穴最深处，被复杂的机关和扭曲的意志所守护。",
        "关于你自己": "吾乃此间一孤舟，一斗桨，渡人亦渡己。名号早已随风逝，唤我'斗桨'足矣。",
        "此地危险": "危险？此地危机四伏，不仅有失落文明遗留的致命机关，更有因秘宝力量而扭曲的生灵徘徊。",
        "线索提示": "万物皆有言，只待有心人。一卷古图，残破石碑，乃至风中低语，皆可能藏着通往真相的丝缕。",
        "火种的重要性": "在这伸手不见五指的黑暗中，即便是微弱的火光，亦能成为指引方向的希望。",
        "星辰的低语": "我曾于星夜静观天象，古老的星辰低语着一些被遗忘的名字，和即将到来的时代。或许是'张本意涵'？时间的长河会揭示一切奥秘。",
        "再见": "去吧，愿你好运，年轻人。若有缘，自会再见。记住，选择比寻找更重要。"
    }

    mr_doujiang = NPC(
        name="斗桨先生",
        description="一位头戴斗笠、身披蓑衣的老者。他眼神深邃，手中总是稳稳地握着一根看似普通的船桨。",
        dialogue=doujiang_dialogue,
        tts_voice_name="Ting-Ting"
    )

    npcs["斗桨先生"] = mr_doujiang

    return npcs

def create_rooms(items, npcs):
    """Create all game rooms"""
    rooms = {}

    room_cabin = Room(
        name="cabin",
        display_name="废弃小屋",
        description="你发现自己在一个摇摇欲坠的废弃小屋里。尘土飞扬，空气中弥漫着霉味。角落里有一个冰冷的[壁炉]。一张破旧的[桌子]放在房间中央。",
        items=[items['火把'], items['古老的地图']],
        npcs=[npcs['斗桨先生']],
        properties={'has_fireplace': True, 'table_searched': False, "fireplace_lit": False},
        ambient_sound="ambient_windy"
    )
    room_cabin.add_exit("北", "forest_path")
    room_cabin.add_exit("东", "dark_cellar_entrance")
    rooms["cabin"] = room_cabin

    room_forest_path = Room(
        name="forest_path",
        display_name="森林小径",
        description="你来到一条蜿蜒的森林小径。高大的树木遮天蔽日。地上散落着一些[枯叶]。",
        properties={'leaves_searched': False, 'key_found_here': True},
        ambient_sound="ambient_forest"
    )
    room_forest_path.add_exit("南", "cabin")
    room_forest_path.add_exit("北", "deep_forest")
    rooms["forest_path"] = room_forest_path

    room_dark_cellar_entrance = Room(
        name="dark_cellar_entrance",
        display_name="黑暗的地下室入口",
        description="这是一段通往地下的楼梯，非常黑暗。你需要[光源]才能下去。一扇[木门]紧闭着。",
        properties={'requires_light': True, 'door_locked': True}
    )
    room_dark_cellar_entrance.add_exit("西", "cabin")
    rooms["dark_cellar_entrance"] = room_dark_cellar_entrance

    room_cellar = Room(
        name="cellar",
        display_name="阴暗的地下室",
        description="地下室里阴冷潮湿。墙角堆放着一些破旧的[木箱]。一个[远古神像]放在一个石台上。",
        items=[items['远古神像']],
        properties={'crates_searched': False, 'crowbar_found_here': True},
        ambient_sound="ambient_cave"
    )
    room_cellar.add_exit("上", "dark_cellar_entrance")
    rooms["cellar"] = room_cellar

    room_deep_forest = Room(
        name="deep_forest",
        display_name="森林深处",
        description="你越往森林深处走，光线就越暗。这里似乎有一个隐蔽的[洞穴入口]。",
        items=[items['治疗药水']],
        properties={'cave_hidden': True},
        ambient_sound="ambient_forest"
    )
    room_deep_forest.add_exit("南", "forest_path")
    room_deep_forest.add_exit("进入洞穴", "cave_entrance")
    rooms["deep_forest"] = room_deep_forest

    room_cave_entrance = Room(
        name="cave_entrance",
        display_name="洞穴入口",
        description="这是一个黑暗的洞穴入口，里面吹出阵阵冷风。洞壁上刻着一些奇怪的[符号]。",
        items=[items['布满灰尘的书']],
        properties={'symbols_deciphered': False},
        ascii_art_on_enter="cave_entrance",
        ambient_sound="ambient_cave"
    )
    room_cave_entrance.add_exit("离开洞穴", "deep_forest")
    room_cave_entrance.add_exit("深入洞穴", "cave_chamber")
    rooms["cave_entrance"] = room_cave_entrance

    room_cave_chamber = Room(
        name="cave_chamber",
        display_name="洞穴密室",
        description="在洞穴的深处，你发现了一个宽敞的密室。密室中央有一个古老的[石棺]。旁边散落着一些[金币]。",
        properties={'treasure_found': False, 'coffin_opened': False},
        ambient_sound="ambient_cave"
    )
    room_cave_chamber.add_exit("离开密室", "cave_entrance")
    rooms["cave_chamber"] = room_cave_chamber

    return rooms
