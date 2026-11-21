// ESP8266 firmware for JEEVA GANGA
// Reads distance from JSN‑SR04T ultrasonic sensor, posts to backend, and triggers a buzzer on low distance.
// Dependencies (Arduino IDE / PlatformIO):
//   - ESP8266 board package
//   - WiFi.h, ESP8266HTTPClient.h, ArduinoJson (optional for JSON payload)

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// ***** USER SETTINGS *****
const char* ssid = "YOUR_WIFI_SSID";          // TODO: set your Wi‑Fi
const char* password = "YOUR_WIFI_PASSWORD"; // TODO: set your Wi‑Fi password
const char* backendUrl = "http://YOUR_BACKEND_HOST:8000/api/ultrasonic"; // change host
const char* deviceId = "esp8266-01"; // unique device identifier

// Pin assignments – adjust to your wiring
const uint8_t trigPin = D5;   // GPIO14
const uint8_t echoPin = D6;   // GPIO12
const uint8_t buzzerPin = D7; // GPIO13 (connected to a buzzer via transistor)

// Threshold distance (cm) at which the buzzer will sound
const float buzzerThreshold = 30.0; // example: alarm when <30 cm

// Helper to generate a simple UUID (not RFC‑4122 compliant, but enough for demo)
String generateUUID() {
  char uuid[37];
  const char* chars = "0123456789abcdef";
  for (int i = 0; i < 36; i++) {
    if (i == 8 || i == 13 || i == 18 || i == 23) uuid[i] = '-';
    else uuid[i] = chars[random(16)];
  }
  uuid[36] = '\0';
  return String(uuid);
}

void connectWiFi() {
  Serial.println("Connecting to Wi‑Fi…");
  WiFi.begin(ssid, password);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print('.');
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi‑Fi connected");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWi‑Fi connection failed");
  }
}

// Measure distance using the JSN‑SR04T sensor (returns cm)
float readDistance() {
  // Trigger a 10 µs pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Listen for echo pulse
  long duration = pulseIn(echoPin, HIGH, 30000L); // timeout 30 ms (~5 m)
  if (duration == 0) {
    return -1.0; // no echo
  }
  // Speed of sound = 340 m/s => 29 µs per cm (round‑trip 58 µs per cm)
  float distance = (duration / 58.0);
  return distance;
}

void postReading(float distance, const String& eventId, const String& ts) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi‑Fi disconnected – reconnecting");
    connectWiFi();
    if (WiFi.status() != WL_CONNECTED) return;
  }

  HTTPClient http;
  http.begin(backendUrl);
  http.addHeader("Content-Type", "application/json");

  // Build JSON payload
  StaticJsonDocument<256> doc;
  doc["device_id"] = deviceId;
  doc["event_id"] = eventId;
  doc["timestamp"] = ts;
  doc["distance_cm"] = distance;
  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);
  Serial.printf("POST %d, response: %s\n", httpCode, http.getString().c_str());
  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  randomSeed(analogRead(0));

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);

  connectWiFi();
}

void loop() {
  float distance = readDistance();
  if (distance < 0) {
    Serial.println("Failed to read distance");
  } else {
    Serial.printf("Distance: %.1f cm\n", distance);
    String eventId = generateUUID();
    String timestamp = String(millis()); // simple ms timestamp; replace with ISO if needed
    postReading(distance, eventId, timestamp);

    // Buzzer logic
    if (distance <= buzzerThreshold && distance > 0) {
      digitalWrite(buzzerPin, HIGH);
      delay(500); // beep 0.5 s
      digitalWrite(buzzerPin, LOW);
    }
  }

  // Re‑connect if Wi‑Fi drops
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  delay(2000); // sample every 2 seconds
}
