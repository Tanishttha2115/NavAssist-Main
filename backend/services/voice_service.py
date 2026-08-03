from collections import deque
from threading import Lock
voice_queue = deque()
voice_lock = Lock()
PRIORITY_MAP = {
    "emergency": 1,
    "danger": 1,
    "warning": 2,
    "navigation": 3,
    "info": 4
}
def generate_voice_output(message, level="info"):
    priority = PRIORITY_MAP.get(level, 4)

    voice_data = {
        "tts": message,
        "level": level,
        "priority": priority
    }

    with voice_lock:
        voice_queue.append(voice_data)

    return voice_data
def get_next_voice():
    with voice_lock:
        if voice_queue:
            return voice_queue.popleft()
    return None
def audio_tone(level):
    tones = {
        "safe": {"tone": "low_beep", "frequency": 400},
        "warning": {"tone": "medium_beep", "frequency": 800},
        "danger": {"tone": "high_beep", "frequency": 1200},
        "emergency": {"tone": "high_beep_fast", "frequency": 1500}
    }
    return tones.get(level, tones["safe"])
def format_message(message):
    return message.strip().capitalize()