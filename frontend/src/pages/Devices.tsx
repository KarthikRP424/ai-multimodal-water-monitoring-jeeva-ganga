// src/pages/Devices.tsx
import React, { useEffect, useState } from "react";
import { fetchDevicesStatus } from "../services/api";
import { useMonitoringWS } from "../hooks/useMonitoringWS";
import { DeviceCard } from "../components/DeviceCard";

const Devices = () => {
  const [devices, setDevices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const wsState = useMonitoringWS(import.meta.env.VITE_BACKEND_URL || "http://localhost:8000");

  // Initial load
  useEffect(() => {
    const load = async () => {
      try {
        const resp = await fetchDevicesStatus();
        setDevices(Object.values(resp.data) || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Live updates – ws sends generic messages; we treat "device_status" same as device heartbeat updates
  useEffect(() => {
    const live = wsState.deviceStatus.map((msg) => msg.payload);
    if (live.length) {
      setDevices((prev) => {
        const map = new Map(prev.map((d) => [d.device_id, d]));
        live.forEach((d) => map.set(d.device_id, d));
        return Array.from(map.values());
      });
    }
  }, [wsState.deviceStatus]);

  if (loading) return <div className="p-4 text-gray-200">Loading devices…</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-100">Device Management</h2>
      {devices.length === 0 ? (
        <p className="text-gray-300">No devices registered.</p>
      ) : (
        devices.map((dev) => <DeviceCard key={dev.device_id} device={dev} />)
      )}
    </div>
  );
};

export default Devices;
