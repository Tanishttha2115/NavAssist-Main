from fastapi import APIRouter, HTTPException, Request
from models.schemas import CommandRequest
from utils.helpers import detect_intent
import logging
import re
from datetime import datetime

router = APIRouter()

@router.post("/process-command")
def process_command(data: CommandRequest, request: Request):
    """
    🎙️ Voice Command Processing API
    - Detects intent
    - Adds logging + validation
    - Returns structured response
    """

    try:
        # 🛡️ Validation
        if not data or not data.text:
            raise HTTPException(status_code=400, detail="Invalid command input")

        text = data.text.strip().lower()

        # 🧠 Detect intent
        result = detect_intent(text)
        intent = result.get("intent", "UNKNOWN")

        # 📍 Extract simple destination (basic NLP)
        destination = None
        if intent == "NAVIGATE":
            match = re.search(r"(to|towards)\s+(.*)", text)
            if match:
                destination = match.group(2).strip()
                # 🧹 Clean destination (remove extra words like please, punctuation)
                destination = re.sub(r"[^\w\s]", "", destination)  # remove punctuation
                destination = re.sub(r"\b(please|now|quickly)\b", "", destination)  # remove filler words
                destination = re.sub(r"\s+", " ", destination).strip()

        # 🔥 Default fallback
        if intent == "NAVIGATE" and not destination:
            destination = "nearest metro station"

        # 🧾 Timestamp + IP
        timestamp = datetime.utcnow().isoformat()
        client_ip = request.client.host if request and request.client else "unknown"

        # 📊 Logging
        logging.info(f"[COMMAND] IP: {client_ip}, Text: {text}, Intent: {intent}, Time: {timestamp}")

        # 🔊 Response message
        message = f"Command recognized as {intent}"
        if destination:
            message += f" to {destination}"

        return {
            "status": "success",
            "intent": intent,
            "destination": destination,
            "is_navigation": intent == "NAVIGATE",
            "message": message,
            "confidence": result.get("confidence", 0.9),
            "timestamp": timestamp
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Command error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process command")