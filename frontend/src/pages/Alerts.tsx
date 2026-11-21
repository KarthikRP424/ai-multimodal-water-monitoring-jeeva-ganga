// src/pages/Alerts.tsx
import React, { useEffect, useState } from "react";
import { fetchAlerts, acknowledgeAlert } from "../services/api";
import { useMonitoringWS } from "../hooks/useMonitoringWS";

export const Alerts = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const wsState = useMonitoringWS(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");

  // Initial load
  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetchAlerts();
        setAlerts(resp.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Merge live alerts from WS (type "alert")
  useEffect(() => {
    const live = wsState.alerts.map((msg) => msg.payload);
    if (live.length) {
      setAlerts((prev) => {
        // Avoid duplicates by ID
        const ids = new Set(prev.map((a) => a.id));
        const newAlerts = live.filter((a) => !ids.has(a.id));
        return [...newAlerts, ...prev];
      });
    }
  }, [wsState.alerts]);

  const handleAcknowledge = async (id: number) => {
    try {
      await acknowledgeAlert(id);
      setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a)));
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="p-4 text-gray-200">Loading alerts…</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-100">Emergency Alerts</h2>
      {alerts.length === 0 ? (
        <p className="text-gray-300">No active alerts.</p>
      ) : (
        <ul className="space-y-2">
          {alerts.map((alert) => (
            <li key={alert.id} className="bg-gray-800 p-3 rounded flex justify-between items-center">
              <div className="flex-1">
                <div className="flex justify-between text-gray-200">
                  <span>{alert.category}</span>
                  <span className="font-medium">{alert.severity.toUpperCase()}</span>
                </div>
                <p className="text-sm text-gray-400 mt-1">{alert.description}</p>
                <p className="text-xs text-gray-500 mt-1">{new Date(alert.timestamp).toLocaleString()}</p>
              </div>
              {!alert.acknowledged && (
                <button
                  className="ml-4 px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded"
                  onClick={() => handleAcknowledge(alert.id)}
                >
                  Acknowledge
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
