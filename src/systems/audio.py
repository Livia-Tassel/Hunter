"""Audio system for sound effects and ambient sounds"""
import os
import platform
from typing import Optional

SOUND_ENABLED = True
AMBIENT_CHANNEL = None

try:
    import pygame
    pygame.mixer.init()
    if pygame.mixer.get_num_channels() > 0:
        AMBIENT_CHANNEL = pygame.mixer.Channel(0)
    print("音效系统已启用")
except (ImportError, Exception):
    SOUND_ENABLED = False
    print("音效系统未启用")

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
    "combat_hit": "combat_hit.wav",
    "level_up": "level_up.wav",
}

LOADED_SOUNDS = {}

class AudioSystem:
    def __init__(self, sounds_dir: str):
        self.sounds_dir = sounds_dir
        self.enabled = SOUND_ENABLED
        self.ambient_channel = AMBIENT_CHANNEL

    def load_sound(self, sound_name: str):
        if not self.enabled:
            return None
        if sound_name in LOADED_SOUNDS:
            return LOADED_SOUNDS[sound_name]

        file_basename = SOUND_FILES.get(sound_name)
        if not file_basename:
            return None

        full_path = os.path.join(self.sounds_dir, file_basename)
        if os.path.exists(full_path):
            try:
                sound = pygame.mixer.Sound(full_path)
                LOADED_SOUNDS[sound_name] = sound
                return sound
            except Exception:
                pass
        return None

    def play_sound(self, sound_name: str, loop: bool = False, volume: float = 1.0):
        if not self.enabled:
            return

        sound = self.load_sound(sound_name)
        if sound:
            try:
                sound.set_volume(volume)
                loops = -1 if loop else 0
                if self.ambient_channel and loop:
                    self.ambient_channel.play(sound, loops=loops)
                else:
                    sound.play(loops=loops)
            except Exception:
                pass

    def stop_ambient(self):
        if self.enabled and self.ambient_channel and self.ambient_channel.get_busy():
            self.ambient_channel.fadeout(500)

    def speak_mac(self, text: str, voice: Optional[str] = None):
        if platform.system() != "Darwin":
            return False
        try:
            sanitized = text.replace('"', '').replace("'", "").replace(";", "")
            cmd = f"say"
            if voice:
                cmd += f' -v "{voice}"'
            cmd += f' "{sanitized}" &'
            os.system(cmd)
            return True
        except Exception:
            return False

audio = None

def init_audio(sounds_dir: str):
    global audio
    audio = AudioSystem(sounds_dir)
    return audio
