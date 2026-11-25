from fastapi.testclient import TestClient
from backend.app.main import app
import json, pathlib

client = TestClient(app)

payload = {"device_id": "esp-cam-pir-01", "motion": true}
response = client.post("/api/sensors/pir/", json=payload)
print('POST status:', response.status_code)
print('Response JSON:', response.json())

# Verify GET alerts (assuming /api/alerts/ returns list)
get_resp = client.get("/api/alerts/")
print('GET alerts status:', get_resp.status_code)
print('Alerts:', get_resp.json())

# Show DB file location
print('DB path:', pathlib.Path('backend/jeeva_ganga.db').resolve())
