#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#define LED_PIN 2 

const char* ssid = "710_2";         //  Wi-Fi
const char* password = "admin1qAZ";
const char* serverUrl = "http://192.168.0.100:5000";  // IP сервера

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
    if (analogRead(0) >= 810){

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
  WiFiClient client = server.available();
  if (!client) return;

  while (!client.available()) delay(1);
  String request = client.readStringUntil('\r');
  client.flush();



// Обробка подій на сервері
  String inputValue = "";
  if (request.indexOf("GET /?text=") >= 0) {
    int start = request.indexOf("GET /?text=") + 11;
    int end = request.indexOf(" ", start);
    inputValue = request.substring(start, end);
    inputValue.replace("%20", " ");
    inputValue.replace("+", " ");

    Serial.println("Отримано: " + inputValue);

// Відпарвка тексту на сервер у формі "message=text"
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      WiFiClient httpClient;
      http.begin(httpClient, serverUrl);
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      String postData = "message=" + inputValue;
      int httpCode = http.POST(postData);
      Serial.printf("HTTP-відповідь сервера: %d\n", httpCode);
      http.end();
    }
  }
// Опис Веб-сторінки
  String html = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n";
  html += "<!DOCTYPE HTML><html><head><meta charset='utf-8'>";
  html += "<title>ESP8266 форма</title></head><body>";
  html += "<h2>Введіть текст:</h2>";
  html += "<form action='/' method='GET'>";
  html += "<input type='text' name='text'>";
  html += "<input type='submit' value='Надіслати'>";
  html += "</form>";
  html += "</body></html>";

  client.print(html);
  delay(1);
}
