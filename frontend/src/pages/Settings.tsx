// src/pages/Settings.tsx
import React, { useState, useEffect } from "react";

// Simple settings persisted to localStorage for demo purposes
interface Settings {
  waterWarning: number;
  waterCritical: number;
  yoloModelPath: string;
}

const defaultSettings: Settings = {
  waterWarning: 30,
  waterCritical: 10,
  yoloModelPath: "backend/app/models/best.pt",
};

export const Settings = () => {
  const [settings, setSettings] = useState<Settings>(defaultSettings);

  useEffect(() => {
    const stored = localStorage.getItem("jeevaSettings");
    if (stored) {
      try {
        setSettings(JSON.parse(stored));
      } catch {
        // ignore parse errors
      }
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSettings((prev) => ({
      ...prev,
      [name]: name.includes("water") ? Number(value) : value,
    }));
  };

  const saveSettings = () => {
    localStorage.setItem("jeevaSettings", JSON.stringify(settings));
    alert("Settings saved locally. Refresh to apply in the UI.");
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4 text-gray-100">Settings</h2>
      <div className="space-y-4 max-w-md">
        <div>
          <label className="block text-gray-200 mb-1">Water Warning Threshold (cm)</label>
          <input
            type="number"
            name="waterWarning"
            value={settings.waterWarning}
            onChange={handleChange}
            className="w-full p-2 rounded bg-gray-800 text-gray-100"
          />
        </div>
        <div>
          <label className="block text-gray-200 mb-1">Water Critical Threshold (cm)</label>
          <input
            type="number"
            name="waterCritical"
            value={settings.waterCritical}
            onChange={handleChange}
            className="w-full p-2 rounded bg-gray-800 text-gray-100"
          />
        </div>
        <div>
          <label className="block text-gray-200 mb-1">YOLO Model Path</label>
          <input
            type="text"
            name="yoloModelPath"
            value={settings.yoloModelPath}
            onChange={handleChange}
            className="w-full p-2 rounded bg-gray-800 text-gray-100"
          />
        </div>
        <button
          onClick={saveSettings}
          className="px-4 py-2 bg-indigo-600 rounded hover:bg-indigo-500"
        >
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default Settings;
