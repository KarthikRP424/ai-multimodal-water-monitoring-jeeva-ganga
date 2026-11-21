# firmware/esp8266/esp8266_ultrasonic_firmware.ino

/*
  ESP8266 Firmware (Firmware B)
  Board: NodeMCU ESP8266
  Sensors: JSN‑SR04T ultrasonic (TRIG D1/GPIO5, ECHO D2/GPIO4 via voltage divider), Buzzer D5/GPIO14
  Functions:
    - Connect to Wi‑Fi (SSID/PWD from wifi_config.h)
    - Periodically measure distance (default every 5 s)
    - Filter out invalid readings (e.g., 0 cm or > 500 cm)
    - POST JSON reading to /api/sensors/ultrasonic
    - POST heartbeat JSON to /api/devices/heartbeat (keep‑alive every 30 s)
    - Configurable warning/critical thresholds (set via constants)
    - Activate buzzer when distance <= warning (short beep) or <= critical (long beep)
    - Re‑connect Wi‑Fi on disconnect
    - Report status/errors via heartbeat payload
*/

#include "wifi_config.h"
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// ---------- PIN CONFIGURATION ----------
#define TRIG_PIN 5   // D1 (GPIO5)
#define ECHO_PIN 4   // D2 (GPIO4) – must be voltage‑divided to 3.3 V
#define BUZZER_PIN 14 // D5 (GPIO14)

// ---------- USER SETTINGS ----------
const char* DEVICE_ID = "esp8266_ultrasonic_01"; // change per device
const unsigned long MEASURE_INTERVAL_MS = 5000; // 5 s
const unsigned long HEARTBEAT_INTERVAL_MS = 30000; // 30 s

// Thresholds (cm) – adjust as needed for your installation
const float WARNING_THRESHOLD_CM = 150.0; // e.g., water approaching
const float CRITICAL_THRESHOLD_CM = 80.0; // imminent overflow

// ---------- GLOBAL STATE ----------
unsigned long lastMeasureTime = 0;
unsigned long lastHeartbeatTime = 0;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.println(" connected");
}

void loop() {
  // Re‑connect Wi‑Fi if lost
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    return;
  }

  unsigned long now = millis();

  // ---- Measurement ----
  if (now - lastMeasureTime >= MEASURE_INTERVAL_MS) {
    lastMeasureTime = now;
    float distance = measureDistance();
    if (distance >= 0) { // valid reading
      bool warning = distance <= WARNING_THRESHOLD_CM;
      bool critical = distance <= CRITICAL_THRESHOLD_CM;
      sendUltrasonicReading(distance, warning, critical);
      handleBuzzer(warning, critical);
    } else {
      // Invalid reading – still send heartbeat indicating sensor error
      sendHeartbeat("sensor_error");
    }
  }

  // ---- Heartbeat ----
  if (now - lastHeartbeatTime >= HEARTBEAT_INTERVAL_MS) {
    lastHeartbeatTime = now;
    sendHeartbeat("online");
  }
}

float measureDistance() {
  // Send 10 µs pulse to trigger
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Read echo pulse length (microseconds)
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout 30 ms (~5 m)
  if (duration == 0) {
    Serial.println("Ultrasonic timeout");
    return -1.0; // invalid
  }
  // Speed of sound = 343 m/s = 0.0343 cm/µs (round‑trip /2)
  float distance = (duration * 0.0343) / 2.0;
  Serial.printf("Measured distance: %.2f cm\n", distance);
  // Basic sanity filter
  if (distance < 2.0 || distance > 500.0) {
    Serial.println("Distance out of range");
    return -1.0;
  }
  return distance;
}

void sendUltrasonicReading(float distance, bool warning, bool critical) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(String(BACKEND_URL) + "/api/sensors/ultrasonic");
  http.addHeader("Content-Type", "application/json");
  String payload = "{\"device_id\":\"" + String(DEVICE_ID) + "\",\"distance_cm\":" + String(distance, 2) + ",\"warning\":" + (warning ? "true" : "false") + ",\"critical\":" + (critical ? "true" : "false") + ",\"timestamp\":\"" + isoTimestamp() + "\"}";
  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    Serial.printf("Ultrasonic POST %d\n", httpCode);
  } else {
    Serial.printf("Ultrasonic POST error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void sendHeartbeat(const char* status) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(String(BACKEND_URL) + "/api/devices/heartbeat");
  http.addHeader("Content-Type", "application/json");
  String payload = "{\"device_id\":\"" + String(DEVICE_ID) + "\",\"status\":\"" + String(status) + "\",\"timestamp\":\"" + isoTimestamp() + "\"}";
  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    Serial.printf("Heartbeat POST %d\n", httpCode);
  } else {
    Serial.printf("Heartbeat POST error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void handleBuzzer(bool warning, bool critical) {
  // Simple beep logic – short beep for warning, long beep for critical
  if (critical) {
    // Long beep (1 s)
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000);
    digitalWrite(BUZZER_PIN, LOW);
  } else if (warning) {
    // Short beep (200 ms)
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

String isoTimestamp() {
  time_t now = time(nullptr);
  struct tm *ptm = gmtime(&now);
  char buf[25];
  snprintf(buf, sizeof(buf), "%04d-%02d-%02dT%02d:%02d:%02dZ",
           ptm->tm_year + 1900, ptm->tm_mon + 1, ptm->tm_mday,
           ptm->tm_hour, ptm->tm_min, ptm->tm_sec);
  return String(buf);
}
