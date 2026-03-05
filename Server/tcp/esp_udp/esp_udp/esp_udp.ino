#include <ESP8266WiFi.h>

const char* ssid = "Empl";
const char* password = "gmfi5678okx";

const char* host = "192.168.18.36"; // IP сервера
const uint16_t port = 9000;

WiFiClient client;
const int analogPin = A0;
const int sampleRate = 2000;
const int sampleDelay = 1000000 / sampleRate;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.println("Підключення до Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi підключено!");

  if (!client.connect(host, port)) {
    Serial.println("Не вдалося підключитися до сервера");
  } else {
    Serial.println("Підключено до сервера");
  }
}

void loop() {
  if (client.connected()) {
    int raw = analogRead(analogPin); // 0-1023

    // Надсилаємо як два байти (Little Endian)
    byte bytes[2];
    bytes[0] = raw & 0xFF;
    bytes[1] = (raw >> 8) & 0xFF;
    client.write(bytes, 2);

    delayMicroseconds(sampleDelay);

  } else {
    Serial.println("Втрата з'єднання, перепідключення...");
    client.stop();
    delay(1000);
    if (client.connect(host, port)) {
      Serial.println("Підключено до сервера");
    }
  }
}
