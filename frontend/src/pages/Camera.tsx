// src/pages/Camera.tsx
import React, { useEffect, useState, useRef } from "react";
import { fetchCameraEvents } from "../services/api";
import { useMonitoringWS } from "../hooks/useMonitoringWS";

// Simple canvas overlay for detections
const drawDetections = (ctx: CanvasRenderingContext2D, detections: any[]) => {
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  detections.forEach((det) => {
    const { bbox, class: cls, confidence } = det;
    const { x, y, w, h } = bbox;
    ctx.strokeStyle = "#00FF00";
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = "#00FF00";
    ctx.font = "12px sans-serif";
    ctx.fillText(`${cls} ${(confidence * 100).toFixed(0)}%`, x + 2, y + 12);
  });
};

export default function Camera() {
  const [events, setEvents] = useState<any[]>([]); // recent camera events (image URLs)
  const [detectionsMap, setDetectionsMap] = useState<Record<number, any[]>>({}); // event_id → detections
  const [loading, setLoading] = useState(true);
  const wsState = useMonitoringWS(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  // Load initial events on mount
  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetchCameraEvents();
        const data = resp.data || [];
        setEvents(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Handle live camera upload messages
  useEffect(() => {
    const camMsg = wsState.cameraEvents[0];
    if (camMsg && camMsg.payload) {
      const { event_id, image_url, timestamp } = camMsg.payload;
      setEvents((prev) => [{ id: event_id, image_url, timestamp }, ...prev]);
    }
  }, [wsState.cameraEvents]);

  // Listen for detection WS messages (type "detection")
  useEffect(() => {
    const wsUrl = `${import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"}`
      .replace("http", "ws")
      .replace("https", "wss") + "/ws/monitoring";
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === "detection" && msg.payload) {
          const { event_id, detections } = msg.payload;
          setDetectionsMap((prev) => ({ ...prev, [event_id]: detections }));
        }
      } catch (_) {}
    };
    return () => ws.close();
  }, []);

  // Draw detections whenever the image loads or detections change
  useEffect(() => {
    const latest = events[0];
    if (!latest) return;
    const img = imgRef.current;
    const canvas = canvasRef.current;
    if (!img || !canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const handleLoad = () => {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const dets = detectionsMap[latest.id] || [];
      drawDetections(ctx, dets);
    };
    if (img.complete) {
      handleLoad();
    } else {
      img.onload = handleLoad;
    }
  }, [events, detectionsMap]);

  if (loading) return <div className="p-4 text-gray-200">Loading camera data…</div>;

  const latest = events[0];

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-100">AI Camera Intelligence</h2>
      {latest ? (
        <div className="relative inline-block mb-4">
          <img ref={imgRef} src={latest.image_url} alt="Camera capture" className="max-w-full rounded" />
          <canvas ref={canvasRef} className="absolute top-0 left-0 pointer-events-none" />
        </div>
      ) : (
        <p className="text-gray-300">No camera images yet.</p>
      )}
      <h3 className="text-lg font-semibold text-gray-200 mb-2">Recent Detections</h3>
      <ul className="space-y-2">
        {Object.entries(detectionsMap).map(([eid, dets]) => (
          <li key={eid} className="bg-gray-800 p-3 rounded text-gray-100">
            <strong>Event {eid}:</strong>
            {dets.length === 0 ? (
              <span className="ml-2">No objects detected.</span>
            ) : (
              <ul className="ml-4 mt-1 space-y-1">
                {dets.map((d: any, i: number) => (
                  <li key={i}>
                    {d.class} – {(d.confidence * 100).toFixed(1)}% (bbox: {Math.round(d.bbox.x)},{Math.round(d.bbox.y)},{Math.round(d.bbox.w)},{Math.round(d.bbox.h)})
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
