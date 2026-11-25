// src/pages/PIR.tsx
import React, { useEffect, useState } from "react";
import { fetchPIREvents } from "../services/api";
import { useMonitoringWS } from "../hooks/useMonitoringWS";

const PIR = () => {
  const [loading, setLoading] = useState(true);
  const [initial, setInitial] = useState<any[]>([]);
  const wsState = useMonitoringWS(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");

  // Try to fetch any existing events – the backend currently only has POST, so this may be empty
  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetchPIREvents();
        setInitial(resp.data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Combine initial data with live WebSocket events (type "pir_event")
  const combined = [
    ...wsState.pirEvents.map((msg) => msg.payload),
    ...initial,
  ];

  if (loading) return <div className="p-4 text-gray-200">Loading PIR data…</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-100">PIR Motion Monitoring</h2>
      {combined.length === 0 ? (
        <p className="text-gray-300">No motion events recorded.</p>
      ) : (
        <ul className="space-y-2">
          {combined.map((ev, idx) => (
            <li key={idx} className="bg-gray-800 p-3 rounded">
              <div className="flex justify-between text-gray-200">
                <span>Device: {ev.device_id}</span>
                <span>Motion: {ev.motion ? "✅" : "❌"}</span>
              </div>
              <div className="text-sm text-gray-400">{new Date(ev.timestamp).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PIR;
