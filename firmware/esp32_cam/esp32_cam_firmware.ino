# firmware/esp32_cam/esp32_cam_firmware.ino

/*
  ESP32‑CAM Firmware (Firmware A)
  Board: AI‑Thinker ESP32‑CAM
  Sensors: Camera module, HC‑SR501 PIR (GPIO13)
  Functions:
    - Connect to Wi‑Fi (SSID/PWD from wifi_config.h)
    - Monitor PIR pin; on motion capture JPEG image
    - POST JSON event to /api/camera/events
    - POST multipart image to /api/camera/upload
    - Cool‑down interval to avoid spamming (default 30 s)
    - Reconnect Wi‑Fi on disconnect
    - Report errors via JSON payload
*/

#include "wifi_config.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

// ---------- PIN CONFIGURATION ----------
#define PIR_PIN 13  // Confirm wiring before flashing

// ---------- CAMERA CONFIGURATION ----------
#define PWDN_GPIO_NUM    32
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM    0
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27
#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      21
#define Y4_GPIO_NUM      19
#define Y3_GPIO_NUM      18
#define Y2_GPIO_NUM      5
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

// ---------- USER SETTINGS ----------
const char* DEVICE_ID = "esp32_cam_01"; // change per device
const unsigned long MOTION_COOLDOWN_MS = 30000; // 30 s cooldown

// ---------- GLOBAL STATE ----------
unsigned long lastMotionTime = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);

  // Init camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA; // 640x480
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    // Send error event to backend (motion false, image not sent)
    sendEvent(false, true);
  }

  // Wi‑Fi connect
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

  bool motion = digitalRead(PIR_PIN) == HIGH;
  unsigned long now = millis();
  if (motion && (now - lastMotionTime) > MOTION_COOLDOWN_MS) {
    lastMotionTime = now;
    // Capture image
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      sendEvent(true, true); // motion true, error flag
      return;
    }
    // POST event JSON (motion true)
    sendEvent(true, false);
    // POST image multipart
    uploadImage(fb);
    esp_camera_fb_return(fb);
  }
  // Send heartbeat (online) every minute
  static unsigned long lastHeartbeat = 0;
  unsigned long now = millis();
  if (now - lastHeartbeat > 60000) { // 60 s
    lastHeartbeat = now;
    sendHeartbeatStatus();
  }

  delay(200);
}

void sendEvent(bool motion, bool errorFlag) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(String(backendUrl) + "/api/camera/events");
  http.addHeader("Content-Type", "application/json");
  String payload = "{\"device_id\":\"" + String(DEVICE_ID) + "\",\"motion\":" + (motion ? "true" : "false") + ",\"timestamp\":\"" + isoTimestamp() + "\"}";
  int httpCode = http.POST(payload);
  if (httpCode > 0) {
    Serial.printf("Event POST code: %d\n", httpCode);
  } else {
    Serial.printf("Event POST error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void uploadImage(camera_fb_t *fb) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(String(backendUrl) + "/api/camera/upload");
  // multipart form-data
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

  String head = "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n" + String(DEVICE_ID) + "\r\n";
  head += "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"file\"; filename=\"capture.jpg\"\r\n";
  head += "Content-Type: image/jpeg\r\n\r\n";
  String foot = "\r\n--" + boundary + "--\r\n";

  int totalLen = head.length() + fb->len + foot.length();
  http.addHeader("Content-Length", String(totalLen));

  WiFiClient *stream = http.getStreamPtr();
  stream->print(head);
  stream->write(fb->buf, fb->len);
  stream->print(foot);

  int httpCode = http.POST("", totalLen); // empty body because we already wrote to stream
  if (httpCode > 0) {
    Serial.printf("Image upload code: %d\n", httpCode);
  } else {
    Serial.printf("Image upload error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

String isoTimestamp() {
  // Simple ISO‑8601 UTC timestamp (no milliseconds)
  time_t now = time(nullptr);
  struct tm *ptm = gmtime(&now);
  char buf[25];
  snprintf(buf, sizeof(buf), "%04d-%02d-%02dT%02d:%02d:%02dZ",
           ptm->tm_year + 1900, ptm->tm_mon + 1, ptm->tm_mday,
           ptm->tm_hour, ptm->tm_min, ptm->tm_sec);
  return String(buf);
}
