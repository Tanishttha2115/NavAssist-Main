from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid

router = APIRouter()

class SOSRequest(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    emergency_type: str

class EmergencyContact(BaseModel):
    name: str
    phone: str
    relation: str

emergency_contacts = []
sos_history = []

INDIA_EMERGENCY = {
    "police": "100",
    "ambulance": "108",
    "fire": "101",
    "women_helpline": "1091",
    "disaster": "1078"
}

@router.post("/emergency/contact")
def add_contact(contact: EmergencyContact):

    emergency_contacts.append(contact.dict())

    return {
        "success": True,
        "message": "Emergency contact added"
    }

@router.get("/emergency/contact")
def get_contacts():

    return {
        "contacts": emergency_contacts
    }

@router.delete("/emergency/contact/{phone}")
def delete_contact(phone: str):

    global emergency_contacts

    emergency_contacts = [
        c for c in emergency_contacts
        if c["phone"] != phone
    ]

    return {
        "message": "Contact removed"
    }

@router.post("/emergency/sos")
def trigger_sos(data: SOSRequest):

    sos_id = str(uuid.uuid4())

    record = {
        "sos_id": sos_id,
        "user_id": data.user_id,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "emergency_type": data.emergency_type,
        "timestamp": datetime.now().isoformat(),
        "status": "ACTIVE"
    }

    sos_history.append(record)

    return {
        "success": True,
        "sos_id": sos_id,
        "message": "Emergency alert generated"
    }

@router.get("/emergency/sos/history")
def get_sos_history():

    return {
        "count": len(sos_history),
        "records": sos_history
    }

@router.post("/emergency/share-location")
def share_location(
    latitude: float,
    longitude: float
):

    location_link = (
        f"https://maps.google.com/?q="
        f"{latitude},{longitude}"
    )

    return {
        "shared": True,
        "location": location_link
    }

@router.post("/emergency/fall-detected")
def fall_detected():

    return {
        "alert": True,
        "message":
        "Potential fall detected. SOS recommended."
    }

@router.post("/emergency/panic")
def panic_mode():

    return {
        "mode": "PANIC",
        "actions": [
            "Send SOS",
            "Share Live Location",
            "Notify Contacts",
            "Start Recording"
        ]
    }

@router.post("/emergency/checkin")
def safe_checkin(user_id: str):

    return {
        "user_id": user_id,
        "status": "SAFE",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/emergency/services")
def emergency_services():

    return INDIA_EMERGENCY

@router.get("/emergency/nearby-help")
def nearby_help():

    return {
        "hospitals": [
            "City Hospital",
            "Emergency Trauma Center"
        ],
        "police_stations": [
            "Central Police Station"
        ]
    }

@router.get("/emergency/status")
def system_status():

    return {
        "service": "Emergency Module",
        "status": "ONLINE",
        "active_sos": len(
            [
                s for s in sos_history
                if s["status"] == "ACTIVE"
            ]
        )
    }