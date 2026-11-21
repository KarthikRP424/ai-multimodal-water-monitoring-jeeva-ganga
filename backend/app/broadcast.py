# backend/app/broadcast.py

import asyncio
import json
from typing import Set
from fastapi import WebSocket

# Global set of active WebSocket connections
connections: Set[WebSocket] = set()

async def send_to_all(message: dict):
    """Serialize and send a JSON message to all connected WebSocket clients."""
    dead = []
    for ws in connections:
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.remove(ws)

async def register(ws: WebSocket):
    await ws.accept()
    connections.add(ws)

async def unregister(ws: WebSocket):
    if ws in connections:
        connections.remove(ws)
