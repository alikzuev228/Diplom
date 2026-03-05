#include <ESP8266WiFi.h>

const char* ssid = "empl";
const char* pass = "gmfi5678okx";

IPAddress serverIP(192,168,18,36);
const uint16_t serverPort = 9000;

WiFiClient client;

#define SAMPLE_RATE 16000
#define BUF_SIZE 512

uint16_t pcm_buf[BUF_SIZE];

void connectTCP() {
  while (!client.connected()) {
    Serial.println("Connecting TCP...");
    if (client.connect(serverIP, serverPort)) {
      Serial.println("TCP connected");
    } else {
      delay(1000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) delay(100);
  Serial.println("Connecting Wi-Fi");
  connectTCP();
}

void loop() {
  if (!client.connected()) {
    client.stop();
    connectTCP();
    Serial.println("Connecting try for server");
  }

  uint32_t t0 = micros();

  for (int i = 0; i < BUF_SIZE; i++) {
    uint16_t adc = analogRead(A0);   // 0..1023
    pcm_buf[i] = adc << 6;           // → 16 bit

    while (micros() - t0 < (1000000UL / SAMPLE_RATE) * (i + 1));
    Serial.println("Download data...");
  }

  client.write((uint8_t*)pcm_buf, BUF_SIZE * 2);
}
