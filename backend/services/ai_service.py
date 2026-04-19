"""
AI Service
Handles object detection + distance estimation (extensible for YOLO / MiDaS)
"""

import logging
from typing import List, Dict, Any

# Integration imports
from services.decision_engine import decide
from services.voice_service import generate_voice_output
from services.haptic_service import get_haptic_pattern

# 🧠 Simple processing throttle
_last_process_time = 0
PROCESS_INTERVAL = 0.5  # seconds

# 🎯 Relevant objects for filtering
IMPORTANT_OBJECTS = {
    "person", "car", "truck", "bus",
    "bicycle", "motorcycle", "stairs"
}

# 🎯 Confidence threshold
CONFIDENCE_THRESHOLD = 0.5


def detect_objects(frame) -> List[Dict[str, Any]]:
    """
    Placeholder detection (replace with YOLO integration later)

    Returns:
    [
        {
            "object": str,
            "confidence": float
        }
    ]
    """

    try:
        # 🚀 Dummy detection (simulate real output)
        detections = [
            {"object": "person", "confidence": 0.9},
            {"object": "chair", "confidence": 0.4},
        ]

        # 🔮 Future: Replace above with YOLO model inference
        # results = model(frame)
        # parse results here

        # 🧠 Filter only important objects + confidence threshold
        filtered = []
        for d in detections:
            logging.debug(f"Detected {d['object']} with confidence {d['confidence']}")
            if d["object"] in IMPORTANT_OBJECTS and d["confidence"] > CONFIDENCE_THRESHOLD:
                filtered.append(d)

        # 📏 Attach dummy distance per object (future: real depth mapping)
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
    """
    Placeholder distance estimation (replace with MiDaS / depth model later)

    Returns:
        float (meters)
    """

    try:
        # 🚀 Dummy logic
        distance = 1.5

        # 🛡️ Safety clamp
        if distance < 0:
            distance = 0
        if distance > 100:
            distance = 100

        return distance

    except Exception as e:
        logging.error(f"Distance error: {e}")
        return None


def process_frame(frame) -> Dict[str, Any]:
    """
    🔁 Main AI pipeline

    Returns:
    {
        "objects": [...],
        "distance": float
    }
    """
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

    # 🧹 Deduplicate objects
    unique_objects = list(set([obj["object"] for obj in objects]))

    # 🧠 Prepare integration-ready payload
    result_payload = {
        "objects": unique_objects,
        "detailed_objects": objects,
        "distance": distance if distance is not None else 999
    }

    return result_payload

# 🚀 FULL PIPELINE HELPER (FINAL STEP)
def run_ai_pipeline(frame, route_data=None):
    """
    🚀 FULL AI + DECISION + OUTPUT PIPELINE
    """
    data = process_frame(frame)

    # 🧠 Decision Engine
    result = decide(
        data.get("objects", []),
        data.get("distance", 999),
        route_data
    )

    # 🔊 Voice Output
    generate_voice_output(result["message"], result["level"])

    # 📳 Haptic Feedback
    haptic = get_haptic_pattern(result["action"], data.get("distance"))

    return {
        "ai": data,
        "decision": result,
        "haptic": haptic
    }