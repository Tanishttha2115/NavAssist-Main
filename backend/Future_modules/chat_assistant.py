from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str

chat_history = []

NAVIGATION_KEYWORDS = {
    "left": "Turn left ahead.",
    "right": "Turn right ahead.",
    "stop": "Please stop and stay alert.",
    "location": "Fetching your current location.",
    "destination": "Checking destination details.",
    "help": "I am here to assist with navigation."
}

def generate_navigation_response(message: str):
    text = message.lower()

    for keyword, response in NAVIGATION_KEYWORDS.items():
        if keyword in text:
            return response

    return (
        "I can help with navigation, directions, obstacles, "
        "destinations and accessibility support."
    )

@router.post("/chat/message")
def chat_with_assistant(data: ChatMessage):

    response = generate_navigation_response(data.message)

    chat_history.append({
        "user": data.message,
        "assistant": response,
        "time": datetime.now().isoformat()
    })

    return ChatResponse(
        response=response,
        timestamp=datetime.now().isoformat()
    )

@router.get("/chat/history")
def get_chat_history():
    return {
        "total_messages": len(chat_history),
        "history": chat_history[-50:]
    }

@router.delete("/chat/history")
def clear_chat_history():
    chat_history.clear()

    return {
        "message": "Chat history cleared successfully"
    }
# ============================
# AI COMMANDS & QUICK ACTIONS
# ============================

QUICK_COMMANDS = {
    "nearest hospital": "Searching nearest hospital...",
    "nearest police": "Searching nearest police station...",
    "nearest atm": "Searching nearest ATM...",
    "call emergency": "Emergency mode activated.",
    "share location": "Preparing live location sharing.",
    "battery status": "Checking battery information.",
    "traffic": "Checking nearby traffic conditions.",
    "weather": "Fetching current weather."
}

@router.get("/chat/commands")
def get_commands():
    return {
        "commands": list(QUICK_COMMANDS.keys())
    }

@router.post("/chat/execute")
def execute_command(data: ChatMessage):

    text = data.message.lower().strip()

    if text in QUICK_COMMANDS:
        return {
            "success": True,
            "response": QUICK_COMMANDS[text]
        }

    return {
        "success": False,
        "response": "Unknown command"
    }

# ============================
# FAQ ASSISTANT
# ============================

FAQ_DATABASE = {
    "how to navigate":
        "Press start navigation and speak destination.",

    "how to stop navigation":
        "Use stop command or tap stop button.",

    "how to change language":
        "Open settings and select language.",

    "how to share location":
        "Use share location command.",

    "how to activate voice mode":
        "Enable voice assistance from settings."
}

@router.get("/chat/faqs")
def get_faqs():
    return {
        "faqs": list(FAQ_DATABASE.keys())
    }

@router.post("/chat/faq")
def faq_response(data: ChatMessage):

    question = data.message.lower()

    for key, value in FAQ_DATABASE.items():

        if key in question:
            return {
                "answer": value
            }

    return {
        "answer": "No matching FAQ found."
    }

# ============================
# CHAT ANALYTICS
# ============================

@router.get("/chat/stats")
def get_chat_stats():

    total_messages = len(chat_history)

    return {
        "total_messages": total_messages,
        "assistant_replies": total_messages,
        "active": True
    }

# ============================
# SAVED CONVERSATIONS
# ============================

saved_sessions = []

@router.post("/chat/save")
def save_session():

    saved_sessions.append({
        "timestamp": datetime.now().isoformat(),
        "messages": chat_history.copy()
    })

    return {
        "message": "Session saved successfully"
    }

@router.get("/chat/saved")
def get_saved_sessions():

    return {
        "count": len(saved_sessions),
        "sessions": saved_sessions
    }

# ============================
# EMERGENCY ASSISTANT
# ============================

EMERGENCY_CONTACTS = [
    {
        "name": "Police",
        "number": "100"
    },
    {
        "name": "Ambulance",
        "number": "108"
    },
    {
        "name": "Women Helpline",
        "number": "1091"
    }
]

@router.get("/chat/emergency")
def emergency_contacts():

    return {
        "contacts": EMERGENCY_CONTACTS
    }

@router.post("/chat/sos")
def trigger_sos():

    return {
        "success": True,
        "message": "SOS request generated.",
        "time": datetime.now().isoformat()
    }

# ============================
# VOICE CHAT PLACEHOLDER
# ============================

@router.post("/chat/voice")
def process_voice(data: ChatMessage):

    return {
        "transcript": data.message,
        "response": generate_navigation_response(
            data.message
        )
    }

# ============================
# ROUTE QUESTIONS
# ============================

ROUTE_QUESTIONS = {
    "distance":
        "Distance calculation module active.",

    "time":
        "Estimated travel time module active.",

    "traffic":
        "Traffic analysis module active.",

    "route":
        "Route planning module active."
}

@router.post("/chat/route")
def route_assistant(data: ChatMessage):

    text = data.message.lower()

    for keyword, answer in ROUTE_QUESTIONS.items():

        if keyword in text:
            return {
                "response": answer
            }

    return {
        "response":
        "Please ask about route, time, traffic or distance."
    }