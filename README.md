# JEEVA GANGA

**Intelligence That Protects Life**

## Overview

JEEVA GANGA is an AI‑powered water‑emergency detection platform. It combines IoT sensors (ESP32‑CAM, PIR, ultrasonic), YOLO‑based computer vision and a real‑time web dashboard.

The repository contains two main parts:

- **frontend** – React + Vite + TypeScript UI
- **backend** – FastAPI + SQLite API server

Both parts are independent but communicate via REST and WebSocket.

## Quick Start (Windows)

```powershell
# 1️⃣ Clone / open this folder
cd C:\Users\DELL\Desktop\JEEVA_GANGA

# 2️⃣ Backend setup
python -m venv venv
.\venv\Scripts\activate
pip install -r backend\requirements.txt
uvicorn backend\app\main:app --reload

# 3️⃣ Frontend setup (in a new terminal)
npm install   # install dependencies listed in package.json
npm run dev   # starts Vite dev server at http://localhost:5173
```

The dashboard will connect to the backend at `http://localhost:8000`. If the backend runs on a different host/port, edit `frontend/src/services/api.ts` accordingly.

## Project Structure

```
JEEVA_GANGA/
├─ backend/                # FastAPI server
│   ├─ app/
│   │   ├─ api/            # Routers
│   │   ├─ models/         # SQLModel definitions
│   │   ├─ schemas/        # Pydantic schemas
│   │   ├─ services/       # Business logic (AI, sensor handling)
│   │   ├─ database/       # SQLite DB init
│   │   └─ main.py
│   └─ requirements.txt
├─ frontend/               # React UI
│   ├─ src/
│   │   ├─ components/    # Re‑usable UI pieces
│   │   ├─ pages/         # One page per navigation section
│   │   ├─ layouts/       # Sidebar + TopBar layout
│   │   ├─ hooks/         # Custom React hooks (WebSocket, fetch)
│   │   ├─ services/      # API client wrappers
│   │   ├─ types/         # TypeScript typings
│   │   ├─ App.tsx        # Root component with router
│   │   └─ main.tsx       # Vite entry point
│   ├─ package.json
│   ├─ vite.config.ts
│   ├─ tailwind.config.cjs
│   └─ tsconfig.json
├─ .env.example            # Environment variable template
└─ README.md               # This file
```

## Development Notes

- **Simulated mode** – When no hardware is available the backend emits fake sensor data every few seconds. The UI clearly labels this as **SIMULATED**.
- **AI inference** – The `/api/camera/upload` endpoint stores the image and returns a dummy YOLO result. Replace `services/ai.py` with a real Ultralytics model when hardware is ready.
- **WebSocket** – `ws://localhost:8000/ws/monitoring` streams live device status updates; the frontend subscribes via `useWebSocket` hook.
- **Tailwind** – The design follows the colour palette from the specification (midnight navy, cyan, emerald, amber, red). See `tailwind.config.cjs` for the custom theme.

## Hardware

```text
JEEVA_GANGA/
├─ hardware/
│   ├─ esp32cam/
│   │   └─ esp32cam_firmware.ino   # ESP32‑CAM with PIR upload code
│   └─ esp8266/
│       └─ ultrasonic_buzzer.ino  # ESP8266 ultrasonic sensor & buzzer
```

- **esp32cam_firmware.ino** – Connects to Wi‑Fi, monitors the PIR sensor, captures JPEG images, and uploads them to the backend.
- **ultrasonic_buzzer.ino** – Reads distance from the JSN‑SR04T ultrasonic sensor, posts readings to `/api/ultrasonic`, and triggers a buzzer when a threshold is crossed.

- **Simulated mode** – When no hardware is available the backend emits fake sensor data every few seconds. The UI clearly labels this as **SIMULATED**.
- **AI inference** – The `/api/camera/upload` endpoint stores the image and returns a dummy YOLO result. Replace `services/ai.py` with a real Ultralytics model when hardware is ready.
- **WebSocket** – `ws://localhost:8000/ws/monitoring` streams live device status updates; the frontend subscribes via `useWebSocket` hook.
- **Tailwind** – The design follows the colour palette from the specification (midnight navy, cyan, emerald, amber, red). See `tailwind.config.cjs` for the custom theme.

Feel free to explore, extend the API, plug real ESP‑based firmware and swap the dummy AI logic for a production model.
