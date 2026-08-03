from fastapi import APIRouter, BackgroundTasks, Request
from models.schemas import SOSRequest
import logging
from datetime import datetime
from fastapi import HTTPException

router = APIRouter()

def _send_notifications(location: str, contact: str, timestamp: str):
    try:
        logging.warning(f"[NOTIFY] Sending SOS to {contact} with location {location} at {timestamp}")
    except Exception as e:
        logging.error(f"Notification error: {e}")

@router.post("/send-sos")
def send_sos(data: SOSRequest, background_tasks: BackgroundTasks, request: Request):
    try:
        client_ip = request.client.host if request and request.client else "unknown"
        if not hasattr(send_sos, "_rate"):
            send_sos._rate = {}
        now = datetime.utcnow().timestamp()
        last = send_sos._rate.get(client_ip, 0)
        if now - last < 5:  # 5 sec cooldown
            raise HTTPException(status_code=429, detail="Too many SOS requests. Please wait.")
        send_sos._rate[client_ip] = now
        if not data:
            raise HTTPException(status_code=400, detail="Invalid SOS data")
        if not getattr(data, "location", None):
            raise HTTPException(status_code=400, detail="Location is required")
        location = getattr(data, "location", "unknown")
        contact = getattr(data, "contact", None) or "not provided"
        timestamp = datetime.utcnow().isoformat()
        logging.warning(f"SOS Triggered → IP: {client_ip}, Location: {location}, Contact: {contact}, Time: {timestamp}")
        background_tasks.add_task(_send_notifications, location, contact, timestamp)
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