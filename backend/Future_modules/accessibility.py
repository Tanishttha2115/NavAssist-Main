from fastapi import APIRouter

router = APIRouter()

ACCESSIBILITY_SETTINGS = {
    "high_contrast": False,
    "large_text": False,
    "voice_guidance": True,
    "vibration_feedback": True,
    "screen_reader_mode": False
}

@router.get("/accessibility/settings")
def get_accessibility_settings():
    return ACCESSIBILITY_SETTINGS

@router.post("/accessibility/high-contrast/enable")
def enable_high_contrast():
    ACCESSIBILITY_SETTINGS["high_contrast"] = True
    return {"message": "High contrast mode enabled"}

@router.post("/accessibility/high-contrast/disable")
def disable_high_contrast():
    ACCESSIBILITY_SETTINGS["high_contrast"] = False
    return {"message": "High contrast mode disabled"}

@router.post("/accessibility/large-text/enable")
def enable_large_text():
    ACCESSIBILITY_SETTINGS["large_text"] = True
    return {"message": "Large text mode enabled"}

@router.post("/accessibility/large-text/disable")
def disable_large_text():
    ACCESSIBILITY_SETTINGS["large_text"] = False
    return {"message": "Large text mode disabled"}

@router.post("/accessibility/voice-guidance/enable")
def enable_voice_guidance():
    ACCESSIBILITY_SETTINGS["voice_guidance"] = True
    return {"message": "Voice guidance enabled"}

@router.post("/accessibility/voice-guidance/disable")
def disable_voice_guidance():
    ACCESSIBILITY_SETTINGS["voice_guidance"] = False
    return {"message": "Voice guidance disabled"}

@router.post("/accessibility/vibration/enable")
def enable_vibration_feedback():
    ACCESSIBILITY_SETTINGS["vibration_feedback"] = True
    return {"message": "Vibration feedback enabled"}

@router.post("/accessibility/vibration/disable")
def disable_vibration_feedback():
    ACCESSIBILITY_SETTINGS["vibration_feedback"] = False
    return {"message": "Vibration feedback disabled"}

@router.get("/accessibility/profile")
def get_accessibility_profile():
    return {
        "user_type": "visually_impaired",
        "settings": ACCESSIBILITY_SETTINGS
    }

@router.get("/accessibility/status")
def accessibility_status():
    enabled = [
        key for key, value in ACCESSIBILITY_SETTINGS.items()
        if value is True
    ]

    return {
        "active_features": enabled,
        "count": len(enabled)
    }
##