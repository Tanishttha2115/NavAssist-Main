from time import time

# 🧠 Cooldown memory (prevents spam vibrations)
last_trigger_time = {}

COOLDOWN_MS = 800  # minimum gap between same event

# 🔁 Continuous navigation pulse interval
NAV_PULSE_INTERVAL = 5000  # ms

# 🧠 Track last navigation pulse
_last_nav_pulse = 0

# 🧠 Track last event (for duplicate prevention)
_last_event_type = None

# 🎯 Haptic patterns (enhanced)
HAPTIC_PATTERNS = {
    "LEFT": {
        "pattern": [100, 50, 100],
        "duration": 300,
        "intensity": "low"
    },
    "RIGHT": {
        "pattern": [100, 50, 100, 50, 100],
        "duration": 300,
        "intensity": "low"
    },
    "STOP": {
        "pattern": [300],
        "duration": 700,
        "intensity": "high"
    },
    "WARNING": {
        "pattern": [200, 100, 200],
        "duration": 500,
        "intensity": "medium"
    },
    "NAVIGATION": {
        "pattern": [50],
        "duration": 100,
        "intensity": "low"
    },
    "EMERGENCY": {
        "pattern": [300, 100, 300, 100, 300],
        "duration": 1000,
        "intensity": "high"
    }
}


MAX_DURATION = 2000  # ms, for emergency override

# 🔁 Main function
def get_haptic_pattern(event_type, distance=None):
    global _last_nav_pulse, _last_event_type

    current_time = time() * 1000  # ms

    # 🛑 Duplicate prevention
    if event_type == _last_event_type:
        if event_type in last_trigger_time and current_time - last_trigger_time[event_type] < COOLDOWN_MS:
            return None

    # 🔁 Continuous navigation pulse (every few seconds)
    if event_type == "NAVIGATION":
        if current_time - _last_nav_pulse < NAV_PULSE_INTERVAL:
            return None
        _last_nav_pulse = current_time

    last_trigger_time[event_type] = current_time
    _last_event_type = event_type

    pattern_data = HAPTIC_PATTERNS.get(event_type, {
        "pattern": [100],
        "duration": 200,
        "intensity": "low"
    })

    # ⚡ Distance-based vibration tuning (closer → faster/stronger)
    if distance is not None:
        try:
            # Normalize distance (meters)
            d = float(distance)
            if d < 2:
                # very close → faster pulses
                pattern_data["pattern"] = [50, 30, 50, 30, 50]
            elif d < 4:
                # near → moderate pulses
                pattern_data["pattern"] = [80, 40, 80]
        except Exception:
            pass

    # 🚨 Emergency override (strong repeated signal)
    if event_type == "EMERGENCY":
        pattern_data["pattern"] = [300, 100, 300, 100, 300, 100, 300]
        pattern_data["duration"] = min(pattern_data.get("duration", 1000), MAX_DURATION)
        pattern_data["intensity"] = "high"

    # 🧭 Ensure navigation stays subtle
    if event_type == "NAVIGATION":
        pattern_data["intensity"] = "low"

    return pattern_data