import json
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# Camera event
resp = client.post('/api/camera/events', json={'device_id':'dev1','motion':True})
print('Camera event status', resp.status_code, resp.json())

# PIR event
resp2 = client.post('/api/sensors/pir/', json={'device_id':'dev1','motion':True})
print('PIR event status', resp2.status_code, resp2.json())

# Dashboard overview
resp3 = client.get('/api/dashboard/')
print('Dashboard status', resp3.status_code, resp3.json())
