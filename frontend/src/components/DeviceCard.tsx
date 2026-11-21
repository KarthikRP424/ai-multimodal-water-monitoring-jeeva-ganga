// src/components/DeviceCard.tsx
import React from "react";

type Device = {
  device_id: string;
  status: string;
  timestamp: string;
};

export const DeviceCard: React.FC<{device: Device}> = ({device}) => {
  return (
    <div className="bg-gray-800 p-3 rounded mb-2">
      <div className="flex justify-between text-gray-200">
        <span className="font-medium">{device.device_id}</span>
        <span>{device.status}</span>
      </div>
      <div className="text-xs text-gray-400 mt-1">{new Date(device.timestamp).toLocaleString()}</div>
    </div>
  );
};
