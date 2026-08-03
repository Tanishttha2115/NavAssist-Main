
import logging
from typing import List, Dict, Any

# Integration imports
from services.decision_engine import decide
from services.voice_service import generate_voice_output
from services.haptic_service import get_haptic_pattern

_last_process_time = 0
PROCESS_INTERVAL = 0.5  

IMPORTANT_OBJECTS = {
    "person", "car", "truck", "bus",
    "bicycle", "motorcycle", "stairs"
}

CONFIDENCE_THRESHOLD = 0.5


def detect_objects(frame) -> List[Dict[str, Any]]:

    try:
        detections = [
            {"object": "person", "confidence": 0.9},
            {"object": "chair", "confidence": 0.4},
        ]
        filtered = []
        for d in detections:
            logging.debug(f"Detected {d['object']} with confidence {d['confidence']}")
            if d["object"] in IMPORTANT_OBJECTS and d["confidence"] > CONFIDENCE_THRESHOLD:
                filtered.append(d)

        for obj in filtered:
            obj["distance"] = 1.5

        if not filtered:
            logging.warning("Detection returned no valid objects")

        return filtered

    except Exception as e:
        logging.error(f"Detection error: {e}")
        logging.warning("Detection returned no valid objects")
        return []


def estimate_distance(frame=None) -> float:


    try:
        distance = 1.5

        if distance < 0:
            distance = 0
        if distance > 100:
            distance = 100

        return distance

    except Exception as e:
        logging.error(f"Distance error: {e}")
        return None


def process_frame(frame) -> Dict[str, Any]:

    from time import time
    global _last_process_time

    current_time = time()
    if current_time - _last_process_time < PROCESS_INTERVAL:
        return {
            "objects": [],
            "detailed_objects": [],
            "distance": 999
        }

    _last_process_time = current_time

    if frame is None:
        logging.error("Invalid frame received")
        return {
            "objects": [],
            "detailed_objects": [],
            "distance": 999
        }

    objects = detect_objects(frame)
    distance = estimate_distance(frame)

    logging.info(f"AI Output → Objects: {objects}, Distance: {distance}")

    if not objects:
        logging.warning("No important objects detected")

    unique_objects = list(set([obj["object"] for obj in objects]))

    result_payload = {
        "objects": unique_objects,
        "detailed_objects": objects,
        "distance": distance if distance is not None else 999
    }

    return result_payload
def run_ai_pipeline(frame, route_data=None):
    data = process_frame(frame)

    result = decide(
        data.get("objects", []),
        data.get("distance", 999),
        route_data
    )

    generate_voice_output(result["message"], result["level"])

    haptic = get_haptic_pattern(result["action"], data.get("distance"))

    return {
        "ai": data,
        "decision": result,
        "haptic": haptic
    }