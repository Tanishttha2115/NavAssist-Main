from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)

settings_db = []

class UserSettings(BaseModel):
    user_id: str

    language: Optional[str] = "en"

    voice_enabled: Optional[bool] = True

    dark_mode: Optional[bool] = True

    notifications: Optional[bool] = True

    vibration: Optional[bool] = True

    font_size: Optional[str] = "medium"

    location_tracking: Optional[bool] = True

    emergency_alerts: Optional[bool] = True

    route_voice_guidance: Optional[bool] = True



def generate_id():
    return str(uuid.uuid4())


def current_time():
    return datetime.utcnow()


@router.post("/create")
def create_settings(
    data: UserSettings
):

    existing = next(
        (
            s
            for s in settings_db
            if s["user_id"] == data.user_id
        ),
        None
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Settings already exist"
        )

    settings = {
        "id": generate_id(),
        "user_id": data.user_id,

        "language":
        data.language,

        "voice_enabled":
        data.voice_enabled,

        "dark_mode":
        data.dark_mode,

        "notifications":
        data.notifications,

        "vibration":
        data.vibration,

        "font_size":
        data.font_size,

        "location_tracking":
        data.location_tracking,

        "emergency_alerts":
        data.emergency_alerts,

        "route_voice_guidance":
        data.route_voice_guidance,

        "created_at":
        current_time()
    }

    settings_db.append(
        settings
    )

    return settings


@router.get("/{user_id}")
def get_settings(
    user_id: str
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    return settings



@router.put("/language")
def update_language(
    user_id: str,
    language: str
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["language"] = language

    return {
        "success": True,
        "language": language
    }


@router.put("/dark-mode")
def dark_mode(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["dark_mode"] = enabled

    return {
        "success": True
    }



@router.put("/voice")
def voice_settings(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["voice_enabled"] = enabled

    return {
        "success": True
    }


@router.put("/notifications")
def notifications(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["notifications"] = enabled

    return {
        "success": True
    }



@router.put("/vibration")
def vibration(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["vibration"] = enabled

    return {
        "success": True
    }


@router.put("/font-size")
def font_size(
    user_id: str,
    size: str
):

    allowed = [
        "small",
        "medium",
        "large",
        "extra-large"
    ]

    if size not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Invalid font size"
        )

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["font_size"] = size

    return {
        "success": True,
        "font_size": size
    }



@router.put("/location-tracking")
def location_tracking(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["location_tracking"] = enabled

    return {
        "success": True
    }


@router.put("/emergency-alerts")
def emergency_alerts(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["emergency_alerts"] = enabled

    return {
        "success": True
    }


@router.put("/route-guidance")
def route_guidance(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s
            for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["route_voice_guidance"] = enabled

    return {
        "success": True
    }


@router.put("/accessibility/high-contrast")
def high_contrast_mode(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["high_contrast"] = enabled

    return {
        "success": True,
        "high_contrast": enabled
    }


@router.put("/accessibility/screen-reader")
def screen_reader(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["screen_reader"] = enabled

    return {
        "success": True
    }


@router.put("/accessibility/text-scale")
def text_scale(
    user_id: str,
    scale: float
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["text_scale"] = scale

    return {
        "success": True,
        "scale": scale
    }


@router.put("/ai/enabled")
def ai_enabled(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Settings not found"
        )

    settings["ai_enabled"] = enabled

    return {
        "success": True
    }


@router.put("/ai/voice-style")
def ai_voice_style(
    user_id: str,
    style: str
):

    allowed = [
        "male",
        "female",
        "neutral"
    ]

    if style not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Invalid style"
        )

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    settings["voice_style"] = style

    return {
        "success": True
    }


@router.put("/privacy/location-history")
def location_history_visibility(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    settings["location_history_visible"] = enabled

    return {
        "success": True
    }


@router.put("/privacy/share-data")
def share_analytics_data(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    settings["analytics_sharing"] = enabled

    return {
        "success": True
    }



@router.put("/security/biometric")
def biometric_login(
    user_id: str,
    enabled: bool
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    settings["biometric_login"] = enabled

    return {
        "success": True
    }


@router.put("/security/pin")
def update_pin(
    user_id: str,
    pin: str
):

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    settings["security_pin"] = pin

    return {
        "success": True
    }



trusted_contacts = []


@router.post("/trusted-contact")
def add_trusted_contact(
    user_id: str,
    name: str,
    phone: str
):

    contact = {
        "id": generate_id(),
        "user_id": user_id,
        "name": name,
        "phone": phone
    }

    trusted_contacts.append(
        contact
    )

    return contact


@router.get(
    "/trusted-contact/{user_id}"
)
def get_trusted_contacts(
    user_id: str
):

    return [
        c
        for c in trusted_contacts
        if c["user_id"] == user_id
    ]



devices_db = []


@router.post("/device/register")
def register_device(
    user_id: str,
    device_name: str
):

    device = {
        "id": generate_id(),
        "user_id": user_id,
        "device_name": device_name,
        "registered_at":
        current_time()
    }

    devices_db.append(
        device
    )

    return device


@router.get("/devices/{user_id}")
def user_devices(
    user_id: str
):

    return [
        d
        for d in devices_db
        if d["user_id"] == user_id
    ]


backups_db = []


@router.post("/backup")
def create_backup(
    user_id: str
):

    backup = {
        "backup_id":
        generate_id(),

        "user_id":
        user_id,

        "created_at":
        current_time()
    }

    backups_db.append(
        backup
    )

    return backup


@router.get("/backup/{user_id}")
def get_backups(
    user_id: str
):

    return [
        b
        for b in backups_db
        if b["user_id"] == user_id
    ]


@router.put("/theme")
def update_theme(
    user_id: str,
    theme: str
):

    allowed = [
        "light",
        "dark",
        "blue",
        "green"
    ]

    if theme not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Invalid theme"
        )

    settings = next(
        (
            s for s in settings_db
            if s["user_id"] == user_id
        ),
        None
    )

    settings["theme"] = theme

    return {
        "success": True,
        "theme": theme
    }