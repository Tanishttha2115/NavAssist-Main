"""
🧠 Decision Engine
Combines navigation + detection → outputs action, message, priority, haptic level, and voice level.
Priority (lower = higher priority):
1. EMERGENCY
2. OBSTACLE (danger)
3. WARNING (near obstacle)
4. NAVIGATION
5. INFO
"""

# 🎯 Priority map (shared semantics with voice/haptics)
PRIORITY = {
    "EMERGENCY": 1,
    "DANGER": 2,
    "WARNING": 3,
    "NAVIGATION": 4,
    "INFO": 5
}

# 🔎 Relevant objects that matter for safety
DANGER_OBJECTS = {
    "person", "car", "truck", "bus",
    "bicycle", "motorcycle",
    "wall", "tree", "pole"
}
STAIRS_OBJECTS = {"stairs", "steps"}

# 🧪 Distance thresholds (meters)
DANGER_DIST = 2.0
WARNING_DIST = 4.0


def process_navigation(route_data: dict):
    """
    Normalize navigation payload (from /navigate or maps)
    Expected:
      {
        "steps": [{ "text": "...", "type": "left|right|forward" }],
        "eta": "..."
      }
    """
    if not route_data:
        return {
            "action": "INFO",
            "priority": PRIORITY["INFO"],
            "message": "No route available",
            "level": "info"
        }

    steps = route_data.get("steps", [])
    current = steps[0] if steps else {}

    step_type = (current.get("type") or "").upper()
    text = current.get("text", "Walk straight")

    if step_type in {"LEFT", "RIGHT", "FORWARD"}:
        return {
            "action": step_type,
            "priority": PRIORITY["NAVIGATION"],
            "message": text,
            "level": "navigation"
        }

    return {
        "action": "FORWARD",
        "priority": PRIORITY["NAVIGATION"],
        "message": text,
        "level": "navigation"
    }


def generate_alert(objects: list, distance: float):
    """
    From detection → produce alert (no navigation here)
    Returns dict with action/priority/message/level
    """
    objects = set(objects or [])

    # 🚨 Immediate danger
    if distance is not None and distance < DANGER_DIST:
        if objects & DANGER_OBJECTS:
            return {
                "action": "STOP",
                "priority": PRIORITY["DANGER"],
                "message": "Obstacle ahead. Stop.",
                "level": "danger"
            }
        if objects & STAIRS_OBJECTS:
            return {
                "action": "STOP",
                "priority": PRIORITY["DANGER"],
                "message": "Stairs ahead. Stop.",
                "level": "danger"
            }

    # ⚠️ Near warning
    if distance is not None and distance < WARNING_DIST:
        if objects & DANGER_OBJECTS:
            return {
                "action": "WARNING",
                "priority": PRIORITY["WARNING"],
                "message": "Obstacle nearby. Move carefully.",
                "level": "warning"
            }
        if objects & STAIRS_OBJECTS:
            return {
                "action": "WARNING",
                "priority": PRIORITY["WARNING"],
                "message": "Stairs nearby. Be careful.",
                "level": "warning"
            }

    # ✅ Safe
    return {
        "action": "CLEAR",
        "priority": PRIORITY["INFO"],
        "message": "Path is clear",
        "level": "info"
    }


def decide(objects: list, distance: float, route_data: dict):
    """
    🔁 Final decision combiner
    Priority:
      alert (danger/warning) > navigation > info
    """
    alert = generate_alert(objects, distance)
    nav = process_navigation(route_data)

    # Choose higher priority (lower number wins)
    if alert["priority"] <= nav["priority"]:
        return alert

    return nav
"""
🧠 Decision Engine (Enhanced)
Combines navigation + detection → outputs action, message, priority, level, meta.
Priority (lower = higher priority):
1. EMERGENCY
2. DANGER (immediate obstacle)
3. WARNING (near obstacle)
4. NAVIGATION
5. INFO
"""

from time import time

# 🎯 Priority map
PRIORITY = {
    "EMERGENCY": 1,
    "DANGER": 2,
    "WARNING": 3,
    "NAVIGATION": 4,
    "INFO": 5
}

# 🔎 Relevant objects
DANGER_OBJECTS = {
    "person", "car", "truck", "bus",
    "bicycle", "motorcycle",
    "wall", "tree", "pole"
}
STAIRS_OBJECTS = {"stairs", "steps"}

# 🧪 Distance thresholds (meters)
DANGER_DIST = 2.0
WARNING_DIST = 4.0

# 🔁 Cooldown (avoid repeating same alert)
_last_event = {"key": None, "time": 0}
COOLDOWN_MS = 2000


def _cooldown_ok(key: str):
    now = time() * 1000
    global _last_event

    if _last_event["key"] == key and (now - _last_event["time"] < COOLDOWN_MS):
        return False

    _last_event = {"key": key, "time": now}
    return True


def process_navigation(route_data: dict):
    """
    Normalize navigation payload
    """
    if not route_data:
        return {
            "action": "INFO",
            "priority": PRIORITY["INFO"],
            "message": "No route available",
            "level": "info",
            "meta": {}
        }

    steps = route_data.get("steps", [])
    current = steps[0] if steps else {}

    step_type = (current.get("type") or "").upper()
    text = current.get("text", "Walk straight")

    if step_type in {"LEFT", "RIGHT", "FORWARD"}:
        return {
            "action": step_type,
            "priority": PRIORITY["NAVIGATION"],
            "message": text,
            "level": "navigation",
            "meta": {"type": step_type}
        }

    return {
        "action": "FORWARD",
        "priority": PRIORITY["NAVIGATION"],
        "message": text,
        "level": "navigation",
        "meta": {"type": "FORWARD"}
    }


def generate_alert(objects: list, distance: float):
    """
    Detection → alert (priority aware, multi-object aware)
    """
    objects = set(objects or [])

    # Normalize distance
    if distance is None:
        distance = 999

    # 🧠 Multi-object priority
    has_danger = bool(objects & DANGER_OBJECTS)
    has_stairs = bool(objects & STAIRS_OBJECTS)

    # 🚨 Immediate danger
    if distance < DANGER_DIST:
        if has_stairs:
            key = "stairs_stop"
            if _cooldown_ok(key):
                return {
                    "action": "STOP",
                    "priority": PRIORITY["DANGER"],
                    "message": "Stairs ahead. Stop.",
                    "level": "danger",
                    "meta": {"object": "stairs", "distance": distance}
                }

        if has_danger:
            key = "danger_stop"
            if _cooldown_ok(key):
                return {
                    "action": "STOP",
                    "priority": PRIORITY["DANGER"],
                    "message": f"{', '.join(objects)} ahead. Stop.",
                    "level": "danger",
                    "meta": {"objects": list(objects), "distance": distance}
                }

    # ⚠️ Near warning
    if distance < WARNING_DIST:
        if has_stairs:
            key = "stairs_warn"
            if _cooldown_ok(key):
                return {
                    "action": "WARNING",
                    "priority": PRIORITY["WARNING"],
                    "message": "Stairs nearby. Be careful.",
                    "level": "warning",
                    "meta": {"object": "stairs", "distance": distance}
                }

        if has_danger:
            key = "danger_warn"
            if _cooldown_ok(key):
                return {
                    "action": "WARNING",
                    "priority": PRIORITY["WARNING"],
                    "message": f"{', '.join(objects)} nearby. Move carefully.",
                    "level": "warning",
                    "meta": {"objects": list(objects), "distance": distance}
                }

    # ✅ Safe
    return {
        "action": "CLEAR",
        "priority": PRIORITY["INFO"],
        "message": "Path is clear",
        "level": "info",
        "meta": {"distance": distance}
    }


def decide(objects: list, distance: float, route_data: dict):
    """
    🔁 Final decision combiner
    alert > navigation > info
    """
    alert = generate_alert(objects, distance)
    nav = process_navigation(route_data)

    # Choose higher priority (lower number wins)
    if alert["priority"] <= nav["priority"]:
        return alert

    return nav