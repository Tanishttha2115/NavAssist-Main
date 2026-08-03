from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)

USERS: Dict[str, dict] = {}
PROFILE_ANALYTICS: Dict[str, dict] = {}

class EmergencyContact(BaseModel):
    name: str
    phone: str
    relation: str


class AccessibilityPreferences(BaseModel):
    voice_guidance: bool = True
    obstacle_alerts: bool = True
    vibration_feedback: bool = True
    high_contrast_mode: bool = False
    large_text_mode: bool = False


class UserProfileCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str
    preferred_language: str = "en"

    accessibility: AccessibilityPreferences

    emergency_contacts: List[EmergencyContact] = []


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    accessibility: Optional[AccessibilityPreferences] = None


class ProfileResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone: str
    preferred_language: str
    created_at: str



def generate_user_id():
    return f"USR-{uuid4().hex[:10].upper()}"


def initialize_analytics(user_id: str):
    PROFILE_ANALYTICS[user_id] = {
        "profile_views": 0,
        "profile_updates": 0,
        "navigation_sessions": 0,
        "ocr_requests": 0,
        "object_detection_requests": 0,
        "sos_triggered": 0,
        "last_active": datetime.utcnow().isoformat()
    }

@router.post("/create")
def create_profile(payload: UserProfileCreate):

    existing_email = any(
        user["email"] == payload.email
        for user in USERS.values()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user_id = generate_user_id()

    USERS[user_id] = {
        "user_id": user_id,
        "full_name": payload.full_name,
        "email": payload.email,
        "phone": payload.phone,
        "preferred_language": payload.preferred_language,
        "accessibility": payload.accessibility.dict(),
        "emergency_contacts": [
            contact.dict()
            for contact in payload.emergency_contacts
        ],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "is_active": True
    }

    initialize_analytics(user_id)

    return {
        "success": True,
        "message": "Profile created successfully",
        "user_id": user_id
    }

@router.get("/{user_id}")
def get_profile(user_id: str):

    if user_id not in USERS:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    PROFILE_ANALYTICS[user_id]["profile_views"] += 1

    return USERS[user_id]

@router.put("/{user_id}")
def update_profile(
    user_id: str,
    payload: UserProfileUpdate
):

    if user_id not in USERS:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    profile = USERS[user_id]

    update_data = payload.dict(exclude_unset=True)

    for key, value in update_data.items():

        if key == "accessibility":
            profile[key] = value.dict()

        else:
            profile[key] = value

    profile["updated_at"] = datetime.utcnow().isoformat()

    PROFILE_ANALYTICS[user_id]["profile_updates"] += 1

    return {
        "success": True,
        "message": "Profile updated successfully",
        "profile": profile
    }

@router.delete("/{user_id}")
def delete_profile(user_id: str):

    if user_id not in USERS:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    USERS.pop(user_id)
    PROFILE_ANALYTICS.pop(user_id, None)

    return {
        "success": True,
        "message": "Profile deleted"
    }

@router.get("/")
def search_users(
    name: Optional[str] = Query(None)
):

    results = []

    for user in USERS.values():

        if name:

            if name.lower() not in user["full_name"].lower():
                continue

        results.append(user)

    return {
        "count": len(results),
        "results": results
    }

@router.get("/{user_id}/emergency-contacts")
def get_emergency_contacts(user_id: str):

    if user_id not in USERS:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return USERS[user_id]["emergency_contacts"]


@router.post("/{user_id}/emergency-contacts")
def add_emergency_contact(
    user_id: str,
    contact: EmergencyContact
):

    if user_id not in USERS:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    USERS[user_id]["emergency_contacts"].append(
        contact.dict()
    )

    return {
        "success": True,
        "message": "Emergency contact added"
    }