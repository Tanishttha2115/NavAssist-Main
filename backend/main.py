from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
from fastapi.responses import JSONResponse
from collections import deque
from threading import Lock, Thread
from contextlib import asynccontextmanager
import math
import time
import logging
import requests
import re
from fastapi import Request
import numpy as np
import os

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────
# YOLO model
# ─────────────────────────────────────────────
model = YOLO("yolov8n.pt")

# ─────────────────────────────────────────────
# Named objects — inका naam bolta hai
# Baaki sab ke liye sirf "obstacle"
# ─────────────────────────────────────────────
NAMED_OBJECTS = {"person", "car", "truck", "bus", "bicycle", "motorcycle", "dog"}

# ─────────────────────────────────────────────
# Global camera
# ─────────────────────────────────────────────
camera_lock = Lock()
camera = None
if camera is not None and not camera.isOpened():
    logging.error("Global camera failed to initialize")


def read_frame():
    if camera is None:
        return False, None
    with camera_lock:
        ret, frame = camera.read()
    return ret, frame


# ─────────────────────────────────────────────
# Voice queue
# ─────────────────────────────────────────────
MAX_QUEUE = 20
voice_queue: deque = deque()
voice_lock = Lock()


def enqueue_voice(message: str):
    with voice_lock:
        if len(voice_queue) >= MAX_QUEUE:
            voice_queue.clear()
        if not voice_queue or voice_queue[-1] != message:
            voice_queue.append(message)


# ─────────────────────────────────────────────
# TTS Worker
# ─────────────────────────────────────────────
def tts_worker():
    print("TTS WORKER STARTED")
    while True:
        text = None
        with voice_lock:
            if voice_queue:
                text = voice_queue.popleft()
        if text:
            print(f"Speaking: {text}")
        else:
            time.sleep(0.05)


# ─────────────────────────────────────────────
# Detection state
# ─────────────────────────────────────────────
detect_lock = Lock()
last_detect_call: float = 0.0
DETECT_COOLDOWN = 0

# ─────────────────────────────────────────────
# Navigation state
# ─────────────────────────────────────────────
nav_lock = Lock()
current_route_steps: list = []
current_step_index: int = 0
last_spoken_step: str = ""

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
PRIORITY_MAP = {
    "person": 3, "car": 3, "truck": 3, "bus": 3,
    "chair": 3, "bottle": 3, "table": 3, "dog": 3, "cat": 3,
}
IGNORE_OBJECTS = {"remote", "cell phone", "tie"}
MIN_BOX_AREA = 12000


def get_direction(box_center_x: float, frame_width: int) -> str:
    if box_center_x < frame_width * 0.35:
        return "slightly left"
    elif box_center_x > frame_width * 0.65:
        return "slightly right"
    return "ahead"


# ─────────────────────────────────────────────
# Haversine distance
# ─────────────────────────────────────────────
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Thread(target=tts_worker, daemon=True).start()
    yield
    if camera is not None:
        camera.release()


app = FastAPI(lifespan=lifespan)

# ─────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost:5173",
        "https://nav-assist-main.vercel.app",
        "http://localhost:8080"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "Backend connected successfully 🚀"}


@app.post("/navigate")
def navigate(data: dict):
    destination = data.get("destination", "unknown")
    steps = [
        {"text": "Walk straight", "distance": "20m", "type": "forward"},
        {"text": "Turn left", "distance": "5m", "type": "left"},
        {"text": "Turn right", "distance": "10m", "type": "right"},
    ]
    return {"message": f"Navigating to {destination}", "steps": steps, "eta": "5 mins"}


@app.post("/get-route")
def get_route(data: dict):
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return {"route": {"steps": []}}

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "walking",
        "key": "AIzaSyCv6dwB1BL3uF2uliD-rp10-xSu8bhmesI"
    }

    def clean_html(raw_html):
        text = re.sub(r'<[^>]+>', '', raw_html)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        remove_phrases = [
            "Restricted usage road",
            "Destination will be on the left",
            "Destination will be on the right",
        ]
        for phrase in remove_phrases:
            text = text.replace(phrase, "")
        text = re.sub(r'Pass by.*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()
        lower = text.lower()
        if "roundabout" in lower:
            return "Take roundabout exit"
        if "exit" in lower:
            return "Take exit"
        if "turn right" in lower:
            return "Turn right"
        if "turn left" in lower:
            return "Turn left"
        if "slight right" in lower:
            return "Slight right"
        if "slight left" in lower:
            return "Slight left"
        if "continue" in lower or "head" in lower:
            return "Go straight"
        return text.split('.')[0]

    try:
        logging.info(f"Fetching route: {origin} -> {destination}")
        res = requests.get(url, params=params, timeout=5)
        result = res.json()
        steps = []
        for step in result["routes"][0]["legs"][0]["steps"]:
            steps.append({
                "text": clean_html(step.get("html_instructions", "")),
                "distance_value": step["distance"]["value"],
                "type": step.get("maneuver", ""),
                "start_location": step["start_location"],
                "end_location": step["end_location"]
            })
        with nav_lock:
            global current_route_steps, current_step_index
            current_route_steps = steps
            current_step_index = 0
        return {"route": {"steps": steps}}
    except Exception as e:
        logging.error(f"Route error: {e}")
        return {"route": {"steps": []}}


@app.post("/process-command")
def process_command(data: dict):
    text = data.get("text", "").lower()
    logging.info(f"Received voice: {text}")
    destination = "Metro Station"
    if "to" in text:
        destination = text.split("to")[-1].strip()
    if any(w in text for w in ["go", "take me", "navigate"]):
        return {"intent": "NAVIGATE", "destination": destination}
    elif "stop" in text:
        return {"intent": "STOP"}
    elif any(w in text for w in ["help", "emergency"]):
        return {"intent": "SOS"}
    elif "detect" in text:
        return {"intent": "DETECTION"}
    elif "where am i" in text:
        return {"intent": "LOCATION"}
    return {"intent": "UNKNOWN"}


@app.post("/location")
def location(data: dict):
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    logging.info(f"Location received: {latitude}, {longitude}")
    return {"message": f"Location received: {latitude}, {longitude}"}


@app.post("/send-sos")
def send_sos(data: dict):
    location = data.get("location", "unknown")
    logging.warning(f"SOS received at location: {location}")
    return {"status": "SOS sent 🚨", "location": location}


@app.post("/send-sos-advanced")
def send_sos_advanced(data: dict):
    location = data.get("location", "unknown")
    contact = data.get("contact", "not set")
    logging.warning(f"SOS alert → Location: {location}, Contact: {contact}")
    return {"status": "SOS sent to emergency contact", "location": location, "contact": contact}


user_locations = []

@app.post("/save-location")
def save_location(data: dict):
    user_locations.append(data)
    return {"message": "Location saved", "total": len(user_locations)}


@app.get("/locations")
def get_locations():
    return {"locations": user_locations}


@app.post("/decision")
def decision(data: dict):
    objects = data.get("objects", [])
    step = data.get("step", "")
    if any(obj in ["person", "car", "truck", "bus"] for obj in objects):
        return {"action": "STOP", "priority": 1, "message": "Obstacle very close 🚨"}
    if "left" in step.lower():
        return {"action": "LEFT", "priority": 2, "message": "Turn left"}
    if "right" in step.lower():
        return {"action": "RIGHT", "priority": 2, "message": "Turn right"}
    return {"action": "FORWARD", "priority": 3, "message": "Walk straight"}


@app.post("/speak")
def speak(data: dict):
    text = data.get("text", "")
    if not text:
        return {"status": "empty"}
    enqueue_voice(text)
    return {"status": "queued", "text": text}


@app.get("/next-voice")
def get_next_voice():
    with voice_lock:
        if voice_queue:
            return {"text": voice_queue.popleft()}
    return {"text": None, "status": "empty"}


@app.post("/update-location")
def update_location(data: dict):
    global current_step_index, last_spoken_step
    user_lat = data.get("lat")
    user_lng = data.get("lng")
    if user_lat is None or user_lng is None:
        return {"error": "Location missing"}
    with nav_lock:
        if not current_route_steps:
            return {"error": "No active route"}
        current_step = current_route_steps[current_step_index]
        step_lat = current_step["end_location"]["lat"]
        step_lng = current_step["end_location"]["lng"]
        distance_m = haversine(user_lat, user_lng, step_lat, step_lng)
        if distance_m < 10 and current_step_index < len(current_route_steps) - 1:
            current_step_index += 1
        current_text = current_route_steps[current_step_index]["text"]
        if current_text != last_spoken_step:
            enqueue_voice(f"Navigation: {current_text}")
            last_spoken_step = current_text
        return {
            "current_step": current_route_steps[current_step_index],
            "step_index": current_step_index
        }


# ─────────────────────────────────────────────
# Image detection from posted image
# ─────────────────────────────────────────────
@app.post("/detect-image")
async def detect_image(file: UploadFile = File(...)):
    logging.info("/detect-image HIT")
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return {"error": "Invalid image"}

        results = model(frame, verbose=False)

        frame_width = frame.shape[1]
        result_objects = []

        for r in results:
            for box in r.boxes:
                # Confidence check
                if float(box.conf[0]) < 0.3:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                box_area = (x2 - x1) * (y2 - y1)

                # Chote/door objects ignore karo — MIN_BOX_AREA se chhote skip
                if box_area < MIN_BOX_AREA:
                    continue

                label = model.names[int(box.cls[0])]

                # Irrelevant objects ignore karo
                if label in IGNORE_OBJECTS:
                    continue

                # Direction calculate karo
                center_x = (x1 + x2) / 2
                direction = get_direction(center_x, frame_width)

                if label in NAMED_OBJECTS:
                    # Named object — naam + direction bolega
                    result_objects.append(f"{label} {direction}")
                else:
                    # Unknown object — "obstacle" + direction bolega
                    result_objects.append(f"obstacle {direction}")

        # Duplicates hata do (same label + direction)
        unique_objects = list(set(result_objects))

        if not unique_objects:
            return {"objects": []}

        return {"objects": unique_objects}

    except Exception as e:
        logging.error(f"detect-image error: {e}")
        return {"error": str(e)}