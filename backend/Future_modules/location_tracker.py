
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import math
import uuid

router = APIRouter(
    prefix="/location",
    tags=["Location Tracker"]
)

class LocationUpdate(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    battery_level: Optional[int] = None


class GeoFence(BaseModel):
    name: str
    center_lat: float
    center_lng: float
    radius: float


locations_db = []
geofences_db = []
tracking_sessions = []

def generate_id():
    return str(uuid.uuid4())


def current_time():
    return datetime.utcnow()


def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


def get_user_locations(user_id):
    return [
        item
        for item in locations_db
        if item["user_id"] == user_id
    ]

@router.post("/update")
def update_location(
    data: LocationUpdate
):

    location = {
        "id": generate_id(),
        "user_id": data.user_id,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "accuracy": data.accuracy,
        "speed": data.speed,
        "battery": data.battery_level,
        "timestamp": current_time()
    }

    locations_db.append(location)

    return {
        "success": True,
        "location_id": location["id"]
    }

@router.get("/last/{user_id}")
def last_location(user_id: str):

    records = get_user_locations(user_id)

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No location found"
        )

    return records[-1]


@router.get("/history/{user_id}")
def location_history(
    user_id: str
):

    return {
        "count": len(
            get_user_locations(user_id)
        ),
        "history": get_user_locations(user_id)
    }

@router.get("/distance/{user_id}")
def total_distance(
    user_id: str
):

    records = get_user_locations(user_id)

    if len(records) < 2:
        return {
            "distance_km": 0
        }

    total = 0

    for i in range(
        len(records) - 1
    ):

        first = records[i]
        second = records[i + 1]

        total += haversine_distance(
            first["latitude"],
            first["longitude"],
            second["latitude"],
            second["longitude"]
        )

    return {
        "distance_km": round(
            total,
            2
        )
    }


@router.get("/average-speed/{user_id}")
def average_speed(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    speeds = [
        item["speed"]
        for item in records
        if item["speed"]
    ]

    if not speeds:
        return {
            "average_speed": 0
        }

    return {
        "average_speed":
        round(
            sum(speeds) /
            len(speeds),
            2
        )
    }


@router.post("/session/start")
def start_tracking(
    user_id: str
):

    session = {
        "session_id": generate_id(),
        "user_id": user_id,
        "started_at": current_time(),
        "status": "active"
    }

    tracking_sessions.append(
        session
    )

    return session
@router.post("/geofence/create")
def create_geofence(
    geofence: GeoFence
):

    data = {
        "id": generate_id(),
        "name": geofence.name,
        "center_lat": geofence.center_lat,
        "center_lng": geofence.center_lng,
        "radius": geofence.radius,
        "created_at": current_time()
    }

    geofences_db.append(data)

    return {
        "success": True,
        "geofence": data
    }


@router.get("/geofence/all")
def get_all_geofences():

    return {
        "count": len(geofences_db),
        "data": geofences_db
    }


@router.delete("/geofence/delete/{geofence_id}")
def delete_geofence(
    geofence_id: str
):

    global geofences_db

    geofences_db = [
        g
        for g in geofences_db
        if g["id"] != geofence_id
    ]

    return {
        "success": True
    }

@router.get(
    "/geofence/check/{user_id}"
)
def check_geofence(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="User location not found"
        )

    last = records[-1]

    results = []

    for zone in geofences_db:

        distance = haversine_distance(
            last["latitude"],
            last["longitude"],
            zone["center_lat"],
            zone["center_lng"]
        ) * 1000

        results.append({
            "zone": zone["name"],
            "inside":
            distance <= zone["radius"]
        })

    return results


share_links = []


@router.post("/share/start")
def start_live_share(
    user_id: str
):

    share_id = generate_id()

    data = {
        "share_id": share_id,
        "user_id": user_id,
        "created_at": current_time(),
        "active": True
    }

    share_links.append(data)

    return {
        "share_link":
        f"/location/share/{share_id}"
    }


@router.get("/share/{share_id}")
def get_shared_location(
    share_id: str
):

    link = next(
        (
            x
            for x in share_links
            if x["share_id"]
            == share_id
        ),
        None
    )

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Link not found"
        )

    locations = get_user_locations(
        link["user_id"]
    )

    if not locations:
        raise HTTPException(
            status_code=404,
            detail="Location unavailable"
        )

    return locations[-1]


@router.get(
    "/route-replay/{user_id}"
)
def route_replay(
    user_id: str
):

    history = get_user_locations(
        user_id
    )

    route = []

    for item in history:

        route.append({
            "lat":
            item["latitude"],
            "lng":
            item["longitude"],
            "time":
            item["timestamp"]
        })

    return {
        "points": len(route),
        "route": route
    }

@router.get(
    "/battery/{user_id}"
)
def battery_status(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No records"
        )

    latest = records[-1]

    return {
        "battery":
        latest["battery"]
    }

@router.get(
    "/battery-alert/{user_id}"
)
def battery_alert(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No data"
        )

    battery = records[-1]["battery"]

    return {
        "low_battery":
        battery is not None
        and battery < 20
    }

@router.get(
    "/accuracy/{user_id}"
)
def location_accuracy(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No records"
        )

    return {
        "accuracy":
        records[-1]["accuracy"]
    }

@router.get("/speed/{user_id}")
def current_speed(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No records"
        )

    return {
        "speed":
        records[-1]["speed"]
    }
emergency_contacts = []


class EmergencyContact(BaseModel):
    user_id: str
    name: str
    phone: str


@router.post("/emergency/contact")
def add_emergency_contact(
    contact: EmergencyContact
):

    data = {
        "id": generate_id(),
        "user_id": contact.user_id,
        "name": contact.name,
        "phone": contact.phone,
        "created_at": current_time()
    }

    emergency_contacts.append(data)

    return {
        "success": True,
        "contact": data
    }


@router.get(
    "/emergency/contact/{user_id}"
)
def get_emergency_contacts(
    user_id: str
):

    return [
        c
        for c in emergency_contacts
        if c["user_id"] == user_id
    ]

sos_alerts = []


@router.post("/sos/{user_id}")
def trigger_sos(
    user_id: str
):

    locations = get_user_locations(
        user_id
    )

    if not locations:
        raise HTTPException(
            status_code=404,
            detail="Location not found"
        )

    current = locations[-1]

    alert = {
        "alert_id": generate_id(),
        "user_id": user_id,
        "latitude":
        current["latitude"],
        "longitude":
        current["longitude"],
        "timestamp":
        current_time(),
        "status": "active"
    }

    sos_alerts.append(alert)

    return {
        "success": True,
        "alert": alert
    }


@router.get("/sos/all")
def get_all_sos():

    return sos_alerts

safe_arrivals = []


class SafeArrivalRequest(
    BaseModel
):
    user_id: str
    destination_lat: float
    destination_lng: float


@router.post("/safe-arrival")
def create_safe_arrival(
    data: SafeArrivalRequest
):

    request = {
        "id": generate_id(),
        "user_id": data.user_id,
        "destination_lat":
        data.destination_lat,
        "destination_lng":
        data.destination_lng,
        "arrived": False
    }

    safe_arrivals.append(
        request
    )

    return request


@router.get(
    "/safe-arrival/check/{user_id}"
)
def check_safe_arrival(
    user_id: str
):

    task = next(
        (
            x
            for x in safe_arrivals
            if x["user_id"] == user_id
        ),
        None
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    records = get_user_locations(
        user_id
    )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="Location missing"
        )

    last = records[-1]

    distance = haversine_distance(
        last["latitude"],
        last["longitude"],
        task["destination_lat"],
        task["destination_lng"]
    )

    arrived = distance < 0.1

    task["arrived"] = arrived

    return {
        "arrived": arrived,
        "distance_km":
        round(distance, 2)
    }


crash_events = []


@router.post(
    "/crash-detection/{user_id}"
)
def crash_detection(
    user_id: str,
    acceleration: float
):

    threshold = 18

    if acceleration >= threshold:

        crash = {
            "id": generate_id(),
            "user_id": user_id,
            "acceleration":
            acceleration,
            "time":
            current_time()
        }

        crash_events.append(
            crash
        )

        return {
            "crash_detected":
            True,
            "event": crash
        }

    return {
        "crash_detected":
        False
    }



@router.get(
    "/analytics/{user_id}"
)
def journey_analytics(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    if len(records) < 2:
        return {
            "message":
            "Not enough data"
        }

    total_distance = 0

    for i in range(
        len(records) - 1
    ):

        total_distance += (
            haversine_distance(
                records[i]["latitude"],
                records[i]["longitude"],
                records[i + 1]["latitude"],
                records[i + 1]["longitude"]
            )
        )

    speeds = [
        r["speed"]
        for r in records
        if r["speed"]
    ]

    avg_speed = (
        sum(speeds) /
        len(speeds)
        if speeds else 0
    )

    return {
        "distance_km":
        round(total_distance, 2),

        "avg_speed":
        round(avg_speed, 2),

        "points":
        len(records)
    }


@router.get(
    "/analytics/hotspot/{user_id}"
)
def most_visited(
    user_id: str
):

    records = get_user_locations(
        user_id
    )

    counter = {}

    for r in records:

        key = (
            round(
                r["latitude"],
                3
            ),
            round(
                r["longitude"],
                3
            )
        )

        counter[key] = (
            counter.get(
                key,
                0
            ) + 1
        )

    if not counter:
        return {
            "message":
            "No data"
        }

    hotspot = max(
        counter,
        key=counter.get
    )

    return {
        "latitude":
        hotspot[0],
        "longitude":
        hotspot[1],
        "visits":
        counter[hotspot]
    }