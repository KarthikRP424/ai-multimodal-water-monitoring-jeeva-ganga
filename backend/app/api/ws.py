# backend/app/api/ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from ..broadcast import register, unregister

router = APIRouter()

@router.websocket("/monitoring")
async def websocket_endpoint(ws: WebSocket):
    await register(ws)
    try:
        while True:
            try:
                # Wait for a message from the client, timeout to keep the connection alive
                data = await asyncio.wait_for(ws.receive_text(), timeout=30)
                # For now we just ignore client messages; they could be pings or commands
                _ = data
            except asyncio.TimeoutError:
                # Send a simple ping to keep the connection open
                await ws.send_text(json.dumps({"type": "ping"}))
                continue
    except WebSocketDisconnect:
        await unregister(ws)
    except Exception:
        await unregister(ws)
