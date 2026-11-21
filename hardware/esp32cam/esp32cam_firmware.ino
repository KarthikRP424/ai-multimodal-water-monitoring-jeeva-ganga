// ESP32-CAM firmware for JEEVA GANGA
// Connects to Wi‑Fi, monitors PIR HC‑SR501, captures a JPEG on motion and uploads it.
// Dependencies (Arduino IDE / PlatformIO):
//   - ESP32 board package
//   - WiFi.h, HTTPClient.h, ESP32CAM.h (or Arduino camera library)
//   - ArduinoJson for payload building (optional)

#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

// ***** USER SETTINGS *****
const char* ssid = "YOUR_WIFI_SSID";          // TODO: set your Wi‑Fi
const char* password = "YOUR_WIFI_PASSWORD"; // TODO: set your Wi‑Fi password
const char* backendUrl = "http://YOUR_BACKEND_HOST:8000/api/camera/upload"; // change host
const char* deviceId = "esp32cam-01"; // unique device identifier
const uint8_t pirPin = 13; // GPIO where PIR output is wired (adjust for your board)
const unsigned long cooldownMs = 5000; // minimum time between captures
// **************************

// Helper to generate a UUID (simple version)
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

// Camera configuration (adjust for your module)
void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Init with high resolution (QVGA) – increase if you have enough RAM
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    while (true) delay(1000);
  }
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
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWi‑Fi connection failed");
  }
}

void uploadImage(const uint8_t* jpg_buf, size_t jpg_len, const String& eventId, const String& ts) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi‑Fi not connected, retrying");
    connectWiFi();
    if (WiFi.status() != WL_CONNECTED) return;
  }

  HTTPClient http;
  http.begin(backendUrl);
  http.addHeader("Content-Type", "multipart/form-data; boundary=----Boundary123");

  // Build multipart body manually (simple, no library)
  String boundary = "----Boundary123";
  String bodyStart = "--" + boundary + "\r\n" +
                     "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n" +
                     deviceId + "\r\n" +
                     "--" + boundary + "\r\n" +
                     "Content-Disposition: form-data; name=\"event_id\"\r\n\r\n" +
                     eventId + "\r\n" +
                     "--" + boundary + "\r\n" +
                     "Content-Disposition: form-data; name=\"timestamp\"\r\n\r\n" +
                     ts + "\r\n" +
                     "--" + boundary + "\r\n" +
                     "Content-Disposition: form-data; name=\"file\"; filename=\"capture.jpg\"\r\n" +
                     "Content-Type: image/jpeg\r\n\r\n";

  String bodyEnd = "\r\n--" + boundary + "--\r\n";

  // Calculate total length
  size_t contentLength = bodyStart.length() + jpg_len + bodyEnd.length();
  http.addHeader("Content-Length", String(contentLength));

  // Start request
  int httpCode = http.sendRequest("POST", bodyStart.c_str(), bodyStart.length());
  if (httpCode < 0) {
    Serial.printf("Failed to start POST: %s\n", http.errorToString(httpCode).c_str());
    http.end();
    return;
  }
  // Write JPEG binary
  WiFiClient* stream = http.getStreamPtr();
  stream->write(jpg_buf, jpg_len);
  // Write ending
  stream->print(bodyEnd);

  httpCode = http.responseStatusCode();
  String payload = http.getString();
  Serial.printf("Upload response %d: %s\n", httpCode, payload.c_str());
  http.end();
}

unsigned long lastCapture = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  randomSeed(analogRead(0));
  pinMode(pirPin, INPUT);
  connectWiFi();
  setupCamera();
}

void loop() {
  // Simple polling of PIR pin – you can switch to interrupt if preferred
  if (digitalRead(pirPin) == HIGH) {
    unsigned long now = millis();
    if (now - lastCapture >= cooldownMs) {
      lastCapture = now;
      Serial.println("Motion detected – capturing image");
      camera_fb_t* fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("Camera capture failed");
        return;
      }
      String eventId = generateUUID();
      String timestamp = String(millis()); // simple ms timestamp; replace with ISO if needed
      uploadImage(fb->buf, fb->len, eventId, timestamp);
      esp_camera_fb_return(fb);
    }
  }
  // Re‑connect Wi‑Fi if lost
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  delay(200);
}
