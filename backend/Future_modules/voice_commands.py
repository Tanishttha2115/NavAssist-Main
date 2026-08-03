
WAKE_WORDS = [
    "hey navassist",
    "ok navassist",
    "hello navassist",
    "navassist"
]

@router.post("/wake-word/check")
def check_wake_word(text: str):

    text = text.lower()

    detected = False
    matched_word = None

    for wake_word in WAKE_WORDS:

        if wake_word in text:
            detected = True
            matched_word = wake_word
            break

    return {
        "detected": detected,
        "wake_word": matched_word
    }

SUPPORTED_LANGUAGES = [
    "en",
    "hi",
    "fr",
    "es",
    "de",
    "it",
    "ja"
]

USER_LANGUAGES = {}

@router.get("/languages")
def get_languages():

    return {
        "count": len(SUPPORTED_LANGUAGES),
        "languages": SUPPORTED_LANGUAGES
    }

@router.post("/language/change")
def change_language(
    request: LanguageChangeRequest
):

    if request.language not in SUPPORTED_LANGUAGES:

        raise HTTPException(
            status_code=400,
            detail="Unsupported language"
        )

    USER_LANGUAGES[
        request.user_id
    ] = request.language

    initialize_analytics(
        request.user_id
    )

    VOICE_ANALYTICS[
        request.user_id
    ]["language_changes"] += 1

    return {
        "success": True,
        "language": request.language
    }

@router.get("/history/{user_id}")
def get_voice_history(user_id: str):

    history = []

    for command in VOICE_COMMANDS.values():

        if command["user_id"] == user_id:
            history.append(command)

    return {
        "count": len(history),
        "history": history
    }

@router.delete("/history/{user_id}")
def clear_history(user_id: str):

    delete_ids = []

    for command_id, command in VOICE_COMMANDS.items():

        if command["user_id"] == user_id:
            delete_ids.append(command_id)

    for command_id in delete_ids:
        del VOICE_COMMANDS[command_id]

    return {
        "success": True,
        "deleted": len(delete_ids)
    }

@router.get("/frequent/{user_id}")
def get_frequent_commands(user_id: str):

    counter = {}

    for command in VOICE_COMMANDS.values():

        if command["user_id"] != user_id:
            continue

        cmd = command["command"]

        counter[cmd] = (
            counter.get(cmd, 0) + 1
        )

    sorted_commands = sorted(
        counter.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "commands": sorted_commands[:10]
    }

VOICE_SUGGESTIONS = [
    "Navigate Home",
    "Read Text",
    "Scan Surroundings",
    "Call Caregiver",
    "Emergency SOS",
    "Open Profile",
    "Check Battery",
    "Start Navigation"
]

@router.get("/suggestions")
def get_suggestions():

    return {
        "suggestions":
            VOICE_SUGGESTIONS
    }

@router.get("/analytics/{user_id}")
def get_voice_analytics(user_id: str):

    initialize_analytics(user_id)

    return VOICE_ANALYTICS[user_id]

@router.get("/analytics")
def global_voice_analytics():

    total_users = len(
        VOICE_ANALYTICS
    )

    total_commands = sum(
        item["total_commands"]
        for item in
        VOICE_ANALYTICS.values()
    )

    total_navigation = sum(
        item["navigation_commands"]
        for item in
        VOICE_ANALYTICS.values()
    )

    total_sos = sum(
        item["sos_commands"]
        for item in
        VOICE_ANALYTICS.values()
    )

    return {
        "users": total_users,
        "commands": total_commands,
        "navigation": total_navigation,
        "sos": total_sos
    }

@router.get("/score/{user_id}")
def calculate_voice_score(
    user_id: str
):

    initialize_analytics(user_id)

    analytics = VOICE_ANALYTICS[
        user_id
    ]

    score = (
        analytics["total_commands"]
        + analytics["navigation_commands"] * 2
        + analytics["ocr_commands"] * 2
        + analytics["object_detection_commands"] * 2
    )

    return {
        "user_id": user_id,
        "voice_score": score
    }

@router.get("/export/{user_id}")
def export_voice_data(
    user_id: str
):

    history = []

    for command in VOICE_COMMANDS.values():

        if command["user_id"] == user_id:
            history.append(command)

    return {
        "analytics":
            VOICE_ANALYTICS.get(
                user_id,
                {}
            ),
        "history":
            history
    }

@router.get("/admin/dashboard")
def admin_dashboard():

    active_sessions = sum(
        1
        for session
        in VOICE_SESSIONS.values()
        if session["active"]
    )

    total_sessions = len(
        VOICE_SESSIONS
    )

    total_history = len(
        VOICE_COMMANDS
    )

    return {
        "total_sessions":
            total_sessions,
        "active_sessions":
            active_sessions,
        "total_commands":
            total_history,
        "registered_users":
            len(VOICE_ANALYTICS)
    }

COMMAND_CATEGORIES = {
    "navigation": [
        "navigate home",
        "navigate office",
        "start navigation",
        "stop navigation"
    ],
    "ocr": [
        "read text",
        "scan document",
        "read signboard"
    ],
    "object_detection": [
        "scan surroundings",
        "detect object",
        "what is ahead"
    ],
    "emergency": [
        "sos",
        "help me",
        "call caregiver"
    ]
}

@router.get("/categories")
def get_categories():

    return COMMAND_CATEGORIES

USER_FAVORITES = {}

@router.post("/favorites/add")
def add_favorite(
    user_id: str,
    command: str
):

    if user_id not in USER_FAVORITES:
        USER_FAVORITES[user_id] = []

    USER_FAVORITES[user_id].append(
        command
    )

    return {
        "success": True
    }


@router.get("/favorites/{user_id}")
def get_favorites(
    user_id: str
):

    return {
        "favorites":
            USER_FAVORITES.get(
                user_id,
                []
            )
    }

VOICE_NOTIFICATIONS = {}

@router.post("/notifications/create")
def create_notification(
    user_id: str,
    message: str
):

    notification_id = str(uuid4())

    VOICE_NOTIFICATIONS[
        notification_id
    ] = {
        "id": notification_id,
        "user_id": user_id,
        "message": message,
        "created_at":
            datetime.utcnow().isoformat()
    }

    return {
        "notification_id":
            notification_id
    }


@router.get("/notifications/{user_id}")
def get_notifications(
    user_id: str
):

    results = []

    for item in (
        VOICE_NOTIFICATIONS.values()
    ):

        if item["user_id"] == user_id:
            results.append(item)

    return {
        "count": len(results),
        "notifications":
            results
    }

@router.get("/search")
def search_command(
    query: str
):

    matches = []

    for category in (
        COMMAND_CATEGORIES.values()
    ):

        for command in category:

            if query.lower() in (
                command.lower()
            ):
                matches.append(command)

    return {
        "results": matches
    }

@router.get("/leaderboard")
def voice_leaderboard():

    ranking = []

    for user_id, analytics in (
        VOICE_ANALYTICS.items()
    ):

        score = (
            analytics["total_commands"]
            +
            analytics[
                "navigation_commands"
            ]
        )

        ranking.append({
            "user_id": user_id,
            "score": score
        })

    ranking.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "leaderboard":
            ranking[:20]
    }

CAREGIVER_SHORTCUTS = {}

@router.post("/caregiver/save")
def save_caregiver(
    user_id: str,
    phone: str
):

    CAREGIVER_SHORTCUTS[
        user_id
    ] = phone

    return {
        "success": True
    }


@router.get("/caregiver/{user_id}")
def get_caregiver(
    user_id: str
):

    return {
        "phone":
            CAREGIVER_SHORTCUTS.get(
                user_id
            )
    }

QUICK_COMMANDS = [
    "Navigate Home",
    "Call Caregiver",
    "Read Text",
    "Emergency SOS",
    "Scan Area",
    "Battery Status",
    "Current Location",
    "Nearby Obstacle"
]

@router.get("/quick-commands")
def quick_commands():

    return {
        "commands":
            QUICK_COMMANDS
    }

@router.get("/health")
def health():

    return {
        "status": "healthy",
        "module":
            "voice_commands",
        "timestamp":
            datetime.utcnow().isoformat()
    }