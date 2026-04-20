from fastapi import FastAPI
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

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────
# YOLO model
# ─────────────────────────────────────────────
model = YOLO("yolov8n.pt")

# ─────────────────────────────────────────────
# Global camera (thread-safe read via lock)
# ─────────────────────────────────────────────
camera_lock = Lock()
import os

if os.getenv("RENDER"):
    camera = None
else:
    camera = None
if camera is not None and not camera.isOpened():
    logging.error("Global camera failed to initialize")


def read_frame():
    """Thread-safe single frame read from global camera."""
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
    """Add message to TTS queue, skip exact duplicates at tail."""
    with voice_lock:
        if len(voice_queue) >= MAX_QUEUE:
            voice_queue.clear()
        if not voice_queue or voice_queue[-1] != message:
            voice_queue.append(message)


# ─────────────────────────────────────────────
# TTS Worker — fallback to print-based
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
# Detection state (thread-safe)
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
# Haversine distance (metres) — replaces wrong Euclidean calc
# ─────────────────────────────────────────────
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─────────────────────────────────────────────
# Background detection worker
# ─────────────────────────────────────────────
def background_worker():
    global last_detect_call
    while True:
        try:
            ret, frame = read_frame()
            if not ret or frame is None:
                logging.warning("Frame drop in background_worker")
                time.sleep(0.2)
                continue

            results = model(frame, verbose=False)

            best_object = None
            best_score = 0
            best_direction = "ahead"
            all_detected = []

            frame_h, frame_w = frame.shape[:2]

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    if conf < 0.3:
                        continue

                    label = model.names[cls]
                    if label in IGNORE_OBJECTS:
                        continue

                    x1, y1, x2, y2 = box.xyxy[0]
                    box_area = (x2 - x1) * (y2 - y1)
                    if box_area < MIN_BOX_AREA:
                        continue

                    all_detected.append(label)
                    score = PRIORITY_MAP.get(label, 1) * 100_000 + float(box_area)

                    if score > best_score:
                        best_score = score
                        best_object = label
                        best_direction = get_direction((x1 + x2) / 2, frame_w)

            current_time = time.time()

            with detect_lock:
                elapsed = current_time - last_detect_call

            if best_object and elapsed > 3.0:
                # ✅ Queue clear karo — purana backlog flush
                with voice_lock:
                    voice_queue.clear()
                message = f"{best_object} {best_direction}"
                enqueue_voice(message)
                with detect_lock:
                    last_detect_call = current_time

            elif not best_object and all_detected and elapsed > 3.0:
                with voice_lock:
                    voice_queue.clear()
                enqueue_voice(f"{all_detected[0]} ahead")
                with detect_lock:
                    last_detect_call = current_time

            time.sleep(0.3)

        except Exception as e:
            logging.error(f"background_worker error: {e}")
            time.sleep(1)


# ─────────────────────────────────────────────
# Lifespan (replaces deprecated @app.on_event)
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ❌ disable backend camera detection
    # Thread(target=background_worker, daemon=True).start()

    Thread(target=tts_worker, daemon=True).start()
    yield
    # cleanup on shutdown
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


# @app.post("/detect")
# def detect():
'''
    ret, frame = read_frame()
    if not ret:
        return JSONResponse(content={"error": "Camera read failed"}, status_code=500)

    try:
        results = model(frame, verbose=False)
        objects = []
        for r in results:
            for box in r.boxes:
                if float(box.conf[0]) > 0.3:
                    objects.append(model.names[int(box.cls[0])])
        unique_objects = list(set(objects))
        return {"objects": unique_objects, "count": len(unique_objects)}
    except Exception as e:
        logging.error(f"Detection error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
'''


# NOTE: /camera-detect removed — it was blocking the server with a UI window.
# Use /detect or /detect-live instead.


 # ❌ NOT USED (frontend should not call this anymore)
# @app.post("/detect-live")
def detect_live():
    global last_detect_call

    with detect_lock:
        if time.time() - last_detect_call < DETECT_COOLDOWN:
            return {"error": "Too many requests"}
        last_detect_call = time.time()

    ret, frame = read_frame()
    if not ret:
        return {"error": "Frame not captured"}

    try:
        results = model(frame, verbose=False)
        objects = []
        alerts = []
        frame_h, frame_w = frame.shape[:2]

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if conf <= 0.3:
                    continue

                label = model.names[cls]
                # 🔥 allow only important objects
                IMPORTANT = {
                    "person", "car", "truck", "bus",
                    "bicycle", "motorcycle",
                    "wall", "tree", "pole"
                }
                if label not in IMPORTANT:
                    continue

                x1, y1, x2, y2 = box.xyxy[0]
                box_area = (x2 - x1) * (y2 - y1)

                # 🔥 approximate distance (bigger box = closer object)
                distance_est = 200000 / box_area if box_area > 0 else 999

                # 🔥 special handling for walls (detect only when close)
                if label == "wall" and distance_est < 2.5:
                    direction = get_direction((x1 + x2) / 2, frame_w)
                    alert_msg = f"wall ahead" if direction == "ahead" else f"wall ahead {direction}"
                    alerts.append(alert_msg)
                    enqueue_voice("Wall ahead. Stop.")

                # 🔥 normal objects
                elif box_area > 50000:
                    direction = get_direction((x1 + x2) / 2, frame_w)
                    alert_msg = f"{label} ahead" if direction == "ahead" else f"{label} ahead {direction}"
                    alerts.append(alert_msg)
                    enqueue_voice(f"{label} {direction}")

                objects.append(label)

        # 🔥 BETTER WALL DETECTION (distance-based fallback)
        if len(objects) == 0:
            frame_area = frame.shape[0] * frame.shape[1]

            # assume full frame = close obstacle
            distance_est = 200000 / frame_area if frame_area > 0 else 999

            if distance_est < 2.5:
                enqueue_voice("Obstacle very close. Stop.")
                alerts.append("obstacle ahead")

        return {"objects": list(set(objects)), "count": len(set(objects)), "alerts": list(set(alerts))}

    except Exception as e:
        logging.error(f"Live detect error: {e}")
        return {"error": str(e)}


# @app.get("/detect-stream")
def detect_stream():
    # Uses global camera — no new VideoCapture
    detections = []
    for _ in range(10):
        ret, frame = read_frame()
        if not ret:
            break
        results = model(frame, verbose=False)
        for r in results:
            for box in r.boxes:
                if float(box.conf[0]) > 0.3:
                    detections.append(model.names[int(box.cls[0])])

    unique = list(set(detections))
    return {"objects": unique, "count": len(unique)}


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

        # ✅ Haversine distance (was wrong Euclidean before)
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
from fastapi import File, UploadFile

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

        objects = []
        for r in results:
            for box in r.boxes:
                if float(box.conf[0]) > 0.3:
                    label = model.names[int(box.cls[0])]
                    objects.append(label)

        return {"objects": list(set(objects))}

    except Exception as e:
        return {"error": str(e)}