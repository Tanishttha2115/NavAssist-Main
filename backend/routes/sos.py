from fastapi import APIRouter, BackgroundTasks, Request
from models.schemas import SOSRequest
import logging
from datetime import datetime
from fastapi import HTTPException

router = APIRouter()

def _send_notifications(location: str, contact: str, timestamp: str):
    """
    Simulate sending SOS notifications (SMS/WhatsApp/Push)
    Replace with real integrations (Twilio, Firebase) in production.
    """
    try:
        logging.warning(f"[NOTIFY] Sending SOS to {contact} with location {location} at {timestamp}")
    except Exception as e:
        logging.error(f"Notification error: {e}")

@router.post("/send-sos")
def send_sos(data: SOSRequest, background_tasks: BackgroundTasks, request: Request):
    try:
        client_ip = request.client.host if request and request.client else "unknown"

        # 🛑 Simple in-memory rate limit (per IP)
        if not hasattr(send_sos, "_rate"):
            send_sos._rate = {}
        now = datetime.utcnow().timestamp()
        last = send_sos._rate.get(client_ip, 0)
        if now - last < 5:  # 5 sec cooldown
            raise HTTPException(status_code=429, detail="Too many SOS requests. Please wait.")
        send_sos._rate[client_ip] = now

        # 🛡️ Basic validation
        if not data:
            raise HTTPException(status_code=400, detail="Invalid SOS data")
        # Optional stricter checks (if schema fields exist)
        if not getattr(data, "location", None):
            raise HTTPException(status_code=400, detail="Location is required")

        # 📍 Extract fields safely (assuming schema has location/contact)
        location = getattr(data, "location", "unknown")
        contact = getattr(data, "contact", None) or "not provided"

        # 🧾 Timestamp
        timestamp = datetime.utcnow().isoformat()

        # 📊 Logging
        logging.warning(f"SOS Triggered → IP: {client_ip}, Location: {location}, Contact: {contact}, Time: {timestamp}")

        # 🚀 Background notification (non-blocking)
        background_tasks.add_task(_send_notifications, location, contact, timestamp)

        # 🚨 Simulated alert (future: integrate SMS/WhatsApp API)
        return {
            "status": "success",
            "message": "Emergency alert sent",
            "data": {
                "location": location,
                "contact": contact,
                "timestamp": timestamp,
                "ip": client_ip
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"SOS Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send SOS")