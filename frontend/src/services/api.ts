// src/services/api.ts
import axios from "axios";

// Backend base URL – read from VITE_BACKEND_URL (set in .env)
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000,
});

export const fetchOverview = () => api.get("/api/dashboard/");

// Upload a JPEG image from ESP32‑CAM (multipart/form-data)
// `form` must contain fields: device_id, event_id (optional), timestamp (ISO string), and file (the image).
export const uploadCameraImage = (form: FormData) =>
  api.post('/api/camera/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
export const fetchCameraEvents = () => api.get("/api/camera/events");
export const fetchDetections = () => api.get("/api/detections");
export const fetchPIREvents = () => api.get("/api/sensors/pir");
export const fetchUltrasonic = () => api.get("/api/sensors/ultrasonic");
export const fetchAlerts = () => api.get("/api/alerts");
export const acknowledgeAlert = (alertId: number) =>
  api.patch(`/api/alerts/${alertId}`);
export const fetchDevicesStatus = () => api.get("/api/devices/status");
export const postHeartbeat = (deviceId: string, status: string) =>
  api.post("/api/devices/heartbeat", { device_id: deviceId, status });
