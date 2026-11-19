# 🌊 JEEVA GANGA
### *Intelligence That Protects Life.*

**An AI-Enabled Multimodal IoT Framework for Early Detection of Potential Water Emergencies**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?style=for-the-badge)](https://ultralytics.com/)
[![ESP32-CAM](https://img.shields.io/badge/ESP32--CAM-Edge_Vision-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/)
[![ESP8266](https://img.shields.io/badge/ESP8266-Ultrasonic_Node-00979D?style=for-the-badge&logo=arduino&logoColor=white)](https://www.arduino.cc/)

---

## 📖 Overview

**JEEVA GANGA** is an industrial-grade, multimodal IoT and edge-to-cloud AI monitoring platform engineered to detect early signs of potential water hazards around rivers, ponds, reservoirs, and swimming zones. 

Instead of relying on error-prone single-sensor alarms, JEEVA GANGA fuses **computer vision (YOLOv8)**, **passive infrared (PIR) motion sensing**, and **waterproof ultrasonic level telemetry** into a unified, real-time monitoring dashboard. Edge microcontrollers handle lightweight sensing and frame capture, while a local FastAPI server executes AI inference, evaluates explainable safety rules, persists telemetry, and streams live updates via WebSockets to an enterprise dark-themed command center.

### 🛡️ Core Safety Philosophy
> **Critical Design Principle:** Human detection alone, a single PIR motion trigger, or an isolated ultrasonic reading **never** independently triggers a confirmed drowning classification. 
>
> The platform uses transparent, explainable state classifications—**Human Detected**, **Motion Detected**, **Water Level Warning**, **Potential Emergency**, and **Emergency Alert**—and escalates alerts only when multi-sensor rules or operator-configured thresholds are met.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Edge["Edge Hardware Layer (LAN Wi-Fi)"]
        PIR["HC-SR501 PIR Sensor"] -->|Motion Trigger| ESP32["ESP32-CAM Node"]
        ESP32 -->|JPEG Capture & Telemetry| API
        US["JSN-SR04T Ultrasonic Sensor"] -->|5V ECHO via Voltage Divider| ESP8266["ESP8266 NodeMCU"]
        ESP8266 -->|Distance & Heartbeat| API
        ESP8266 -->|Threshold Alert| BUZ["Active Buzzer (Transistor Driver)"]
    end

    subgraph Backend["Laptop / Server Backend (FastAPI + Python)"]
        API["REST API Layer (/api/*)"] --> YOLO["YOLOv8 + OpenCV Inference Engine"]
        API --> DB[("SQLite / SQLModel Persistence")]
        YOLO --> DB
        API --> ALERT["Explainable Rule & Alert Engine"]
        YOLO --> ALERT
        ALERT --> DB
        ALERT --> WS["Async WebSocket Broadcaster (/ws/monitoring)"]
        API --> WS
    end

    subgraph Frontend["Enterprise Command Center (React + TypeScript)"]
        WS <-->|Real-Time Live Stream| UI["8-Page Industrial IoT Dashboard"]
        API <-->|REST Queries & Alert Ack| UI
    end
