#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <Preferences.h>

// --------- UDP ----------
const char* udpAddress = "192.168.18.36";
IPAddress savedIP;
const int udpPort = 9000;
WiFiUDP udp;

// --------- AUDIO --------
#define ADC_PIN 34
#define SAMPLE_RATE 16000
#define SAMPLES_PER_PACKET 256
#define BYTES_PER_SAMPLE 2

uint16_t audioBuffer[SAMPLES_PER_PACKET];
uint16_t sampleIndex = 0;

unsigned long lastSampleMicros = 0;
const unsigned long sampleInterval = 1000000UL / SAMPLE_RATE;

// --------- WIFI CONFIG ----------
WebServer server(80);
Preferences preferences;

String savedSSID;
String savedPASS;
String savedSERV;
int savedPORT;

unsigned long apStartTime;
bool configMode = true;


// --------- WEB PAGE ----------
String htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
<body>
<h2>ESP32 Setup</h2>

<form action="/save">
SSID:<br>
<input type="text" name="ssid"><br>

Password:<br>
<input type="text" name="pass"><br><br>

Server IP:<br>
<input type="text" name="serv"><br>

Port:<br>
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

  String ssid = server.arg("ssid");
  String pass = server.arg("pass");
  String serv = server.arg("serv");
  String port = server.arg("port");

  preferences.begin("config", false);

  preferences.putString("ssid", ssid);
  preferences.putString("pass", pass);
  preferences.putString("serv", serv);
  preferences.putInt("port", port.toInt());

  preferences.end();

  server.send(200, "text/html", "Saved! Rebooting...");
  delay(1000);

  ESP.restart();
}


// --------- WIFI CONNECT ----------
void connectToSavedWiFi() {

  preferences.begin("config", true);
  savedSSID = preferences.getString("ssid", "");
  savedPASS = preferences.getString("pass", "");
  savedSERV = preferences.getString("serv", "");
  savedPORT = preferences.getInt("port", 9000);

  savedIP.fromString(savedSERV);
  preferences.end();

  if (savedSSID == "") {
    Serial.println("No saved WiFi");
    return;
  }

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


// --------- SETUP ----------
void setup() {

  Serial.begin(115200);

  analogReadResolution(12);
  analogSetPinAttenuation(ADC_PIN, ADC_11db);

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

  // CONFIG MODE 15 seconds
  if (configMode) {

    server.handleClient();

    if (millis() - apStartTime > 15000) {

      Serial.println("Config timeout");

      WiFi.softAPdisconnect(true);
      WiFi.mode(WIFI_STA);

      connectToSavedWiFi();

      configMode = false;
    }

    return;
  }

  // -------- AUDIO STREAM --------

  unsigned long now = micros();

  if (now - lastSampleMicros >= sampleInterval) {

    lastSampleMicros += sampleInterval;

    audioBuffer[sampleIndex++] = analogRead(ADC_PIN);

    if (sampleIndex >= SAMPLES_PER_PACKET) {

      udp.beginPacket(savedIP, savedPORT);
      udp.write((uint8_t*)audioBuffer, SAMPLES_PER_PACKET * BYTES_PER_SAMPLE);
      udp.endPacket();

      sampleIndex = 0;
    }
  }
}