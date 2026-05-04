#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <Preferences.h>

// --------- WIFI CONFIG ----------
WebServer server(80);
Preferences preferences;

// Глобальні змінні
WiFiUDP udp;
String savedSSID;
String savedPASS;
String savedSERV;
String savedPORT;

unsigned long apStartTime;
bool configMode = true;


// --------- WEB PAGE ----------
String htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
<body>
<h2>ESP32 WiFi Setup</h2>
<form action="/save">
SSID:<br>
<input type="text" name="ssid"><br>
Password:<br>
<input type="text" name="pass"><br><br>
SERVER IP:<br>
<input type="text" name="serv"><br><br>
SERVER PORT:<br>
<input type="number" name="port"><br><br>
<input type="submit" value="Save">
</form>
</body>
</html>
)rawliteral";


void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

void handleSave() {
// Парсинг данних переданих з веб-морди
  String ssid = server.arg("ssid");
  String pass = server.arg("pass");
  String serv = server.arg("serv");
  String port = server.arg("port");

// Запис у флеш пам'ять
  preferences.begin("wifi", false);
  preferences.putString("ssid", ssid);
  preferences.putString("pass", pass);
  preferences.end();

// Запис у флеш пам'ять
  preferences.begin("serv", false);
  preferences.putString("serv", serv);
  preferences.putString("port", port);
  preferences.end();

  server.send(200, "text/html", "Saved! Rebooting...");
  delay(1000);

  ESP.restart();
}

// --------- WIFI CONNECT ----------
void connectToSavedWiFi() {

// Витягування з пам'яті
  preferences.begin("wifi", true);
  savedSSID = preferences.getString("ssid", "");
  savedPASS = preferences.getString("pass", "");
  preferences.end();

  if (savedSSID == "") {
    Serial.println("No saved WiFi");
    return;
  }

// Підключення до WiFi
  Serial.println("Connecting to saved WiFi...");
  WiFi.begin(savedSSID.c_str(), savedPASS.c_str());

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {

    Serial.println("\nConnected!");
    Serial.println(WiFi.localIP());

    udp.begin(1234);

  } else {
    Serial.println("WiFi failed");
  }
}

void sendUDP(uint8_t* data, int length){
  udp.beginPacket(savedSERV.c_str(), savedPORT.toInt()); // Початок пакету
  udp.write((uint8_t*)data, length); // Данні
  udp.endPacket(); // Кінець пакету
}

// --------- UDP ----------
void startUDP(){
  // Витягування з пам'яті
  preferences.begin("serv", true);
  savedSERV = preferences.getString("serv", "");
  savedPORT = preferences.getString("port", "");
  preferences.end();
}

// --------- SETUP ----------
void setup() {

  Serial.begin(115200);

  startUDP();

  WiFi.mode(WIFI_AP);
  WiFi.softAP("ESP32_Config");

  Serial.println("Config AP started");
  Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/save", handleSave);
  server.begin();

  apStartTime = millis();
}

// --------- LOOP ----------
void loop() {


// CONFIG MODE 30 seconds
  if (configMode) {

    server.handleClient();
    //Serial.println(WiFi.softAPgetStationNum());

    if(WiFi.softAPgetStationNum() <= 0){

      if (millis() - apStartTime > 15000) {

        Serial.println("Config timeout");
        WiFi.softAPdisconnect(true);
        WiFi.mode(WIFI_STA);
        connectToSavedWiFi();
        configMode = false;
      }
    }

    return;
  }

  //Serial.println(savedSERV);
  //Serial.println(savedSERV.c_str());

  sendUDP((uint8_t*)savedSERV.c_str(), savedSERV.length());

}