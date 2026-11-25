import requests, os, json, time

# Paths
image_path = os.path.join(os.getenv('VIRTUAL_ENV', ''), 'Lib', 'site-packages', 'ultralytics', 'assets', 'bus.jpg')
# In case VIRTUAL_ENV not set, fallback to relative path
if not os.path.isfile(image_path):
    image_path = r"C:\Users\DELL\Desktop\JEEVA_GANGA\.venv\Lib\site-packages\ultralytics\assets\bus.jpg"

upload_url = 'http://127.0.0.1:8080/api/camera/upload'
alerts_url = 'http://192.168.163.117:8080/api/alerts/'

print('Uploading image:', image_path)
with open(image_path, 'rb') as f:
    files = {'file': ('bus.jpg', f, 'image/jpeg')}
    data = {'device_id': 'test-device'}
    resp = requests.post(upload_url, files=files, data=data)
    print('Upload response status:', resp.status_code)
    try:
        print('Response JSON:', resp.json())
    except Exception:
        print('Response text:', resp.text)

# Wait a moment for async processing
print('Waiting for detection to complete...')
time.sleep(5)

# Fetch alerts
resp = requests.get(alerts_url)
print('Alerts response status:', resp.status_code)
try:
    alerts = resp.json()
    print('Alerts:', json.dumps(alerts, indent=2))
except Exception as e:
    print('Failed to parse alerts:', e)
