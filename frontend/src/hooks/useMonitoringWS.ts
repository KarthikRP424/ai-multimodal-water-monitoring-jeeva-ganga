// src/hooks/useMonitoringWS.ts
import { useEffect, useRef, useState } from "react";

export type WSMessage = {
  type: string;
  payload: any;
};

export type MonitoringState = {
  cameraEvents: WSMessage[];
  pirEvents: WSMessage[];
  ultrasonicReadings: WSMessage[];
  deviceStatus: WSMessage[];
  alerts: WSMessage[];
};

const initialState: MonitoringState = {
  cameraEvents: [],
  pirEvents: [],
  ultrasonicReadings: [],
  deviceStatus: [],
  alerts: [],
};

export const useMonitoringWS = (backendUrl: string) => {
  const [state, setState] = useState<MonitoringState>(initialState);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(`${backendUrl.replace("http", "ws")}/ws/monitoring`);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectAttempts.current = 0;
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data);
          // Dispatch based on type
          setState((prev) => {
            const next = { ...prev };
            switch (msg.type) {
              case "camera_event":
                next.cameraEvents = [msg, ...prev.cameraEvents];
                break;
              case "pir_event":
                next.pirEvents = [msg, ...prev.pirEvents];
                break;
              case "ultrasonic_reading":
                next.ultrasonicReadings = [msg, ...prev.ultrasonicReadings];
                break;
              case "device_status":
                next.deviceStatus = [msg, ...prev.deviceStatus];
                break;
              case "alert":
                next.alerts = [msg, ...prev.alerts];
                break;
              default:
                // ignore unknown types
                break;
            }
            return next;
          });
        } catch (e) {
          console.error("Failed to parse WS message", e);
        }
      };

      const cleanup = () => {
        if (wsRef.current) {
          wsRef.current.close();
          wsRef.current = null;
        }
      };

      ws.onclose = () => {
        console.warn("WebSocket closed, attempting reconnection");
        cleanup();
        // exponential back‑off, max 5 attempts
        if (reconnectAttempts.current < 5) {
          const timeout = Math.pow(2, reconnectAttempts.current) * 1000;
          reconnectAttempts.current += 1;
          setTimeout(connect, timeout);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error", err);
        ws.close();
      };
    };

    connect();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [backendUrl]);

  return state;
};
