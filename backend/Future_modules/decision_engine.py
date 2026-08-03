
PRIORITY = {
    "EMERGENCY": 1,
    "DANGER": 2,
    "WARNING": 3,
    "NAVIGATION": 4,
    "INFO": 5
}

DANGER_OBJECTS = {
    "person", "car", "truck", "bus",
    "bicycle", "motorcycle",
    "wall", "tree", "pole"
}
STAIRS_OBJECTS = {"stairs", "steps"}

DANGER_DIST = 2.0
WARNING_DIST = 4.0


def process_navigation(route_data: dict):
   
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
    objects = set(objects or [])
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
    return {
        "action": "CLEAR",
        "priority": PRIORITY["INFO"],
        "message": "Path is clear",
        "level": "info"
    }


def decide(objects: list, distance: float, route_data: dict):
    alert = generate_alert(objects, distance)
    nav = process_navigation(route_data)
    if alert["priority"] <= nav["priority"]:
        return alert

    return nav

from time import time
PRIORITY = {
    "EMERGENCY": 1,
    "DANGER": 2,
    "WARNING": 3,
    "NAVIGATION": 4,
    "INFO": 5
}
DANGER_OBJECTS = {
    "person", "car", "truck", "bus",
    "bicycle", "motorcycle",
    "wall", "tree", "pole"
}
STAIRS_OBJECTS = {"stairs", "steps"}
DANGER_DIST = 2.0
WARNING_DIST = 4.0
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
    objects = set(objects or [])

    if distance is None:
        distance = 999

    has_danger = bool(objects & DANGER_OBJECTS)
    has_stairs = bool(objects & STAIRS_OBJECTS)

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

    return {
        "action": "CLEAR",
        "priority": PRIORITY["INFO"],
        "message": "Path is clear",
        "level": "info",
        "meta": {"distance": distance}
    }


def decide(objects: list, distance: float, route_data: dict):
    alert = generate_alert(objects, distance)
    nav = process_navigation(route_data)

    if alert["priority"] <= nav["priority"]:
        return alert

    return nav