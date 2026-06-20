NavAssist

AI-Powered Smart Navigation Assistant for Visually Impaired Users

Overview

NavAssist is an AI-powered navigation and accessibility platform designed to help visually impaired individuals navigate safely, independently, and efficiently. The system combines Computer Vision, Real-Time Object Detection, Voice Assistance, GPS Navigation, Emergency Support, and Haptic Feedback to provide a hands-free navigation experience.

The primary objective of NavAssist is to improve mobility, safety, and accessibility for visually impaired users through intelligent assistive technology.

⸻

Features

Smart Navigation

* Real-time route guidance
* Turn-by-turn navigation assistance
* Destination search functionality
* Dynamic route updates

AI Object Detection

* YOLOv8-powered obstacle detection
* Real-time camera analysis
* Detection of pedestrians, vehicles, poles, stairs, and obstacles
* Audio alerts for detected objects

Voice Assistant

* Speech-to-Text command recognition
* Text-to-Speech navigation responses
* Hands-free interaction
* Voice-based destination input

Emergency Assistance

* SOS emergency trigger
* Emergency alert functionality
* Quick-access emergency services module

Haptic Feedback

* Vibration-based navigation alerts
* Obstacle proximity notifications
* Direction-based feedback system

Location Tracking

* Real-time GPS tracking
* Route monitoring
* Live location updates

Accessibility-Focused Design

* Voice-first interaction model
* Minimal visual dependency
* User-friendly accessible interface

⸻

System Architecture

+----------------------+
|        User          |
+----------+-----------+
           |
           v
+----------------------+
|   React Frontend     |
| TypeScript + Vite    |
+----------+-----------+
           |
           v
+----------------------+
|   FastAPI Backend    |
+----------+-----------+
           |
  +--------+--------+
  |        |        |
  v        v        v
Navigation  Voice   AI Detection
 Engine    Service    YOLOv8
  |        |        |
  +--------+--------+
           |
           v
 Emergency & Haptic Services

⸻

Technology Stack

Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

Backend

* FastAPI
* Python

AI and Computer Vision

* YOLOv8
* OpenCV
* NumPy

APIs and Services

* Google Maps API
* Browser Geolocation API
* Speech Recognition API
* Text-to-Speech API

⸻

Project Structure

NavAssist
│
├── frontend
│   ├── public
│   ├── src
│   │   ├── components
│   │   ├── contexts
│   │   ├── hooks
│   │   ├── pages
│   │   └── lib
│   └── package.json
│
├── backend
│   ├── routes
│   ├── services
│   ├── models
│   ├── utils
│   ├── Future_modules
│   ├── main.py
│   └── requirements.txt
│
└── README.md

⸻

Installation and Setup

Clone the Repository

git clone https://github.com/Tanishttha/NavAssist.git
cd NavAssist

⸻

Backend Setup

Navigate to the backend directory:

cd backend

Create a virtual environment:

python -m venv venv

Activate the virtual environment:

macOS / Linux

source venv/bin/activate

Windows

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the backend server:

uvicorn main:app --reload

Backend will be available at:

http://127.0.0.1:8000

⸻

Frontend Setup

Open a new terminal:

cd frontend

Install dependencies:

npm install

Run the development server:

npm run dev

Frontend will be available at:

http://localhost:5173

⸻

API Endpoints

Navigation

POST /navigation

Provides route guidance and navigation instructions.

Voice Commands

POST /command

Processes user voice commands and generates responses.

Emergency Services

POST /sos

Triggers emergency assistance functionality.

⸻

Workflow

1. User enters a destination through voice or text input.
2. Frontend sends the request to the FastAPI backend.
3. Navigation Engine generates route instructions.
4. Voice Service converts instructions into speech.
5. YOLOv8 detects nearby obstacles using camera input.
6. Haptic and audio alerts notify the user of hazards.
7. Emergency module can be activated when assistance is required.

⸻

Future Enhancements

* Offline navigation support
* Smart cane integration
* Wearable device connectivity
* Indoor navigation assistance
* Multi-language voice support
* Advanced obstacle prediction
* Edge AI deployment for low-latency inference
* Enhanced accessibility analytics

⸻

Live Demo

https://nav-assist-main.vercel.app

⸻

License

This project is licensed under the MIT License.

