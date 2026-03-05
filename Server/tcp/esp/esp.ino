#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// ---------- НАЛАШТУВАННЯ ----------
const char* WIFI_SSID = "Empl";
const char* WIFI_PASS = "gmfi5678okx";

const char* SERVER_IP = "192.168.18.36"; // IP сервера
const uint16_t SERVER_PORT = 9000;

const uint16_t SAMPLE_RATE = 8000; // 16 kHz
const uint16_t SAMPLE_DELAY_US = 1000000 / SAMPLE_RATE;

// ----------------------------------

WiFiClient client;

void connectWiFi() {
  Serial.println("[WiFi] Connecting...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[WiFi] Connected");
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());
}

void connectTCP() {
  Serial.println("[TCP] Connecting to server...");

  while (!client.connect(SERVER_IP, SERVER_PORT)) {
    Serial.println("[TCP] Failed, retrying...");
    delay(1000);
  }

  Serial.println("[TCP] Connected");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== ESP8266 AUDIO STREAMER ===");

  connectWiFi();
  connectTCP();
}

void loop() {
  if (!client.connected()) {
    Serial.println("[TCP] Disconnected, reconnecting...");
    connectTCP();
  }

  // ----- Зчитування з A0 -----
  uint16_t adc = analogRead(A0); // 0..1023

  // Little-endian
  uint8_t buffer[2];
  buffer[0] = adc & 0xFF;
  buffer[1] = (adc >> 8) & 0xFF;
  // Відправка
  client.write(buffer, 2);
/*
  static float phase = 0;
  int16_t pcm = sin(phase) * 12000;
  phase += 0.05;
  client.write((uint8_t*)&pcm, 2);
*/

  // Лог (можна закоментувати для швидкості)
 // Serial.print("[AUDIO] ADC=");
 // Serial.print(adc);
 // Serial.print(" PCM=");
//  Serial.println(pcm);

  delayMicroseconds(SAMPLE_DELAY_US);
}
