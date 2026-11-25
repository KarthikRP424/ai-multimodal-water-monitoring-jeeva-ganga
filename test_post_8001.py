import requests, json
url = 'http://127.0.0.1:8001/api/sensors/pir/'
payload = {"device_id": "esp-cam-pir-01", "motion": True}
try:
    r = requests.post(url, json=payload, timeout=5)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', e)
