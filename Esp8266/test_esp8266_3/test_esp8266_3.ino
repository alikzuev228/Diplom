#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#define LED_PIN 2 

const char* ssid = "Empl";         //  Wi-Fi
const char* password = "gmfi5678okx";
const char* serverUrl = "http://192.168.18.36:5000";  // IP сервера

WiFiServer server(80);

// Підключення до Wi-Fi
void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("\nПідключення до Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi підключено!");
  Serial.print("ESP IP: ");
  Serial.println(WiFi.localIP());

  server.begin();
  Serial.println("Веб-сервер запущено");
}

void loop() {
    if (analogRead(0) >= 660){

    // Відпарвка тексту на сервер у формі "message=text"
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("Гучна подія!");
      HTTPClient http;
      WiFiClient httpClient;
      http.begin(httpClient, serverUrl);
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      String postData = "message=Гучна подія!";
      int httpCode = http.POST(postData);
      Serial.printf("HTTP-відповідь сервера: %d\n", httpCode);
      http.end();
      delay(10);
    }
    
  } 
}