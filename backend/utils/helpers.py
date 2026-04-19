def detect_intent(text):
    text = text.lower().strip()

    # 🔥 Navigation intents
    if any(keyword in text for keyword in ["go", "take me", "navigate", "direction", "reach"]):
        return {"intent": "NAVIGATE", "confidence": 0.9}

    # 🛑 Stop / cancel
    elif any(keyword in text for keyword in ["stop", "cancel", "halt"]):
        return {"intent": "STOP", "confidence": 0.9}

    # 🚨 Emergency
    elif any(keyword in text for keyword in ["help", "emergency", "sos"]):
        return {"intent": "SOS", "confidence": 1.0}

    # 👁️ Detection / surroundings
    elif any(keyword in text for keyword in ["what is in front", "what's around", "detect", "see", "look"]):
        return {"intent": "DETECTION", "confidence": 0.85}

    # 📍 Location queries
    elif any(keyword in text for keyword in ["where am i", "my location", "current location"]):
        return {"intent": "LOCATION", "confidence": 0.85}

    # 🧠 Fallback
    return {"intent": "UNKNOWN", "confidence": 0.5}