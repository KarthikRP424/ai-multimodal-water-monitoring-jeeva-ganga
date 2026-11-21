// src/App.tsx
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./layouts/Sidebar";
import TopBar from "./layouts/TopBar";
import Overview from "./pages/Overview";
import CameraPage from "./pages/Camera";
import PIRPage from "./pages/PIR";
import WaterPage from "./pages/Water";
import AlertsPage from "./pages/Alerts";
import HistoryPage from "./pages/History";
import DevicesPage from "./pages/Devices";
import SettingsPage from "./pages/Settings";

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-primary text-white">
        <Sidebar />
        <div className="flex flex-col flex-1">
          <TopBar />
          <main className="p-4 overflow-auto">
            <Routes>
              <Route path="/" element={<Navigate to="/overview" replace />} />
              <Route path="/overview" element={<Overview />} />
              <Route path="/camera" element={<CameraPage />} />
              <Route path="/pir" element={<PIRPage />} />
              <Route path="/water" element={<WaterPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/devices" element={<DevicesPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
