// src/pages/Water.tsx
import React, { useEffect, useState, useMemo } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import { fetchUltrasonic } from "../services/api";
import { useMonitoringWS } from "../hooks/useMonitoringWS";

export const Water = () => {
  const [loading, setLoading] = useState(true);
  const [initial, setInitial] = useState<any[]>([]);
  const wsState = useMonitoringWS(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");

  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetchUltrasonic();
        setInitial(resp.data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const combined = useMemo(() => {
    const data = [
      ...wsState.ultrasonicReadings.map((msg) => msg.payload),
      ...initial,
    ];
    // sort by timestamp ascending
    return data.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }, [wsState.ultrasonicReadings, initial]);

  if (loading) return <div className="p-4 text-gray-200">Loading water level data…</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-100">Water Level Monitoring</h2>
      {combined.length === 0 ? (
        <p className="text-gray-300">No ultrasonic readings yet.</p>
      ) : (
        <ul className="space-y-2">
          {combined.map((reading, idx) => (
            <li key={idx} className="bg-gray-800 p-3 rounded">
              <div className="flex justify-between text-gray-200">
                <span>Device: {reading.device_id}</span>
                <span>Distance: {reading.distance_cm} cm</span>
              </div>
              <div className="text-sm text-gray-400">{new Date(reading.timestamp).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
