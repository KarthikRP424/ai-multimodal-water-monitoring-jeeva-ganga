// src/pages/History.tsx
import React, { useEffect, useState } from "react";
import { fetchDetections } from "../services/api";
import { useMonitoringWS } from "../hooks/useMonitoringWS";

const History = () => {
  const [detections, setDetections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const wsState = useMonitoringWS(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");

  // Initial load of existing detections
  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetchDetections();
        setDetections(resp.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Live camera upload events – prepend new detections
  useEffect(() => {
    const uploads = wsState.cameraEvents.filter((msg) => msg.type === "camera_upload");
    if (uploads.length) {
      const newDet = uploads[0].payload?.detections || [];
      setDetections((prev) => [...newDet, ...prev]);
    }
  }, [wsState.cameraEvents]);

  if (loading) return <div className="p-4 text-gray-200">Loading detection history…</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-100">Detection History</h2>
      {detections.length === 0 ? (
        <p className="text-gray-300">No detections recorded.</p>
      ) : (
        <ul className="space-y-2">
          {detections.map((det) => (
            <li key={det.id} className="bg-gray-800 p-3 rounded">
              <div className="flex justify-between text-gray-200">
                <span>{det.object_class}</span>
                <span>{(det.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="text-sm text-gray-400 mt-1">{new Date(det.timestamp).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default History;
