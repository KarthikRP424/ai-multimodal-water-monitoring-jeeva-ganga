# test_api.py – basic API tests for JEEVA GANGA backend

import io
import json
import pytest
from fastapi.testclient import TestClient

# The client fixture is defined in conftest.py

def test_camera_upload(client: TestClient):
    # Minimal JPEG header + footer
    jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 10 + b"\xff\xd9"
    files = {"file": ("test.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = {"device_id": "esp32_cam_001"}
    response = client.post("/api/camera/upload", data=data, files=files)
    assert response.status_code == 200, response.text
    json_resp = response.json()
    assert json_resp["device_id"] == "esp32_cam_001"
    assert json_resp["image_path"].endswith("test.jpg")

def test_pir_event_alert(client: TestClient):
    payload = {"device_id": "esp32_cam_001", "motion": True}
    response = client.post("/api/sensors/pir", json=payload)
    assert response.status_code == 200, response.text
    alerts = client.get("/api/alerts/").json()
    assert any(a["category"] == "motion" for a in alerts)

def test_alert_acknowledge(client: TestClient):
    payload = {
        "device_id": "test_device",
        "category": "test",
        "severity": "info",
        "description": "test alert",
    }
    resp = client.post("/api/alerts/", json=payload)
    assert resp.status_code == 200
    alert_id = resp.json()["id"]
    ack_resp = client.patch(f"/api/alerts/{alert_id}")
    assert ack_resp.status_code == 200
    assert ack_resp.json()["acknowledged"] is True

def test_websocket_broadcast(client: TestClient):
    with client.websocket_connect("/ws/monitoring") as ws:
        from backend.app.services import alert_manager
        alert_manager.notify("test_ws", {"msg": "hello"})
        data = ws.receive_text()
        msg = json.loads(data)
        assert msg["type"] == "alert"
        assert msg["payload"]["category"] == "test_ws"
