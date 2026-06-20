from fastapi import APIRouter, HTTPException
from models.schemas import RouteRequest
from services.decision_engine import process_navigation
from services.voice_service import generate_voice_output
import logging
import requests
import re

print("🔥 THIS FILE IS RUNNING")
router = APIRouter()

# 🧠 In-memory step tracker (for demo)
current_step_index = 0

# 🧹 Clean HTML instructions from Google Maps
def clean_html(raw_html):
    # Remove all HTML tags properly
    clean_text = re.sub(r'<[^>]+>', '', raw_html)
    # Remove extra spaces/newlines
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text


def get_google_maps_route(destination: str, origin: str):
    """
    🔥 Google Maps API integration (placeholder)
    Replace API_KEY with your key
    """
    try:
        API_KEY = "AIzaSyCv6dwB1BL3uF2uliD-rp10-xSu8bhmesI"

        origin = origin.replace(" ", "")
        destination = destination.strip()

        params = {
            "origin": origin,
            "destination": destination,
            "mode": "walking",
            "key": API_KEY
        }

        response = requests.get("https://maps.googleapis.com/maps/api/directions/json", params=params)
        data = response.json()

        print("🔥 GOOGLE API RESPONSE:", data)

        # ⚠️ Fallback if API fails
        if data.get("status") != "OK":
            logging.error(f"Google API Error: {data}")
            raise Exception(f"Google API failed: {data.get('status')}")

        steps = data["routes"][0]["legs"][0]["steps"]

        formatted_steps = []
        for step in steps:
            raw_instruction = step.get("html_instructions", "")
            instruction = clean_html(raw_instruction)
            distance = step["distance"]["text"]

            # 🧠 Detect direction type
            direction = "forward"
            text_lower = instruction.lower()

            if any(word in text_lower for word in ["left", "slight left", "sharp left"]):
                direction = "left"
            elif any(word in text_lower for word in ["right", "slight right", "sharp right"]):
                direction = "right"

            formatted_steps.append({
                "text": instruction,  # cleaned text (no HTML)
                "type": step.get("maneuver", direction),  # use Google maneuver if available
                "distance_value": step["distance"]["value"],  # meters
                "start_location": step.get("start_location"),
                "end_location": step.get("end_location")
            })

        return {
            "steps": formatted_steps,
            "distance": data["routes"][0]["legs"][0]["distance"]["text"],
            "eta": data["routes"][0]["legs"][0]["duration"]["text"],
            "destination": destination
        }

    except Exception as e:
        logging.error(f"Google Maps error: {e}")

        raise HTTPException(status_code=500, detail="Google Maps API failed. Check API key, billing, or request format.")


@router.post("/get-route")
def get_route(data: RouteRequest):
    """
    🧭 Navigation API with:
    ✔ Google Maps integration
    ✔ Turn-by-turn step tracking
    ✔ Voice auto instructions
    """

    global current_step_index

    try:
        # 🛡️ Validation
        if not data:
            raise HTTPException(status_code=400, detail="Invalid request")

        destination = getattr(data, "destination", None)
        origin = getattr(data, "origin", None)

        if not destination:
            raise HTTPException(status_code=400, detail="Destination required")
        if not origin:
            raise HTTPException(status_code=400, detail="Origin (current location) required")

        logging.info(f"Fetching route for: {destination}")

        # 🔥 Get route (Google Maps or fallback)
        route = get_google_maps_route(destination, origin)

        steps = route.get("steps", [])

        if not steps:
            raise HTTPException(status_code=500, detail="No route steps found")

        # 🧭 Turn-by-turn logic
        if current_step_index >= len(steps):
            current_step_index = 0  # reset

        current_step = steps[current_step_index]

        # 📍 FIXED: Do NOT auto-skip steps randomly
        # Step progression should be controlled by frontend (GPS tracking)
        step_distance = current_step.get("distance_value", 0)

        # Only move step if explicitly triggered (keep stable)
        if step_distance == 0 and current_step_index < len(steps) - 1:
            current_step_index += 1
            current_step = steps[current_step_index]

        # 🔊 English + Hindi voice
        generate_voice_output(f"{current_step['text']}", "navigation")
        generate_voice_output("Kripya diye gaye direction follow karein", "navigation")

        # 🧠 Decision Engine
        navigation_result = process_navigation(route)

        return {
            "status": "success",
            "route": route,
            "current_step": current_step,
            "navigation": navigation_result
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Route error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch route")
