// src/pages/Overview.tsx
import React, { useEffect, useState } from "react";
import { fetchOverview } from "../services/api";
import { StatCard } from "../components/StatCard";
import { useMonitoringWS } from "../hooks/useMonitoringWS";

const Overview = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const wsState = useMonitoringWS(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");

  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetchOverview();
        setData(resp.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <div className="p-4 text-gray-200">Loading...</div>;
  if (!data) return <div className="p-4 text-gray-200">No data</div>;

  return (
    <div className="p-4 grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <StatCard title="Total Devices" value={data.total_devices} />
      <StatCard title="Online Devices" value={data.online_devices} />
      <StatCard title="Human Detections (1h)" value={data.human_detections_last_hour} />
      <StatCard title="PIR Motions (1h)" value={data.pir_movements_last_hour} />
      <StatCard title="Latest Ultrasonic (cm)" value={data.latest_ultrasonic_cm ?? "-"} />
      <StatCard title="Active Alerts" value={data.active_alerts} />
    </div>
  );
};

export default Overview;
