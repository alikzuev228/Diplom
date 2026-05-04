#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <Preferences.h> 

//UDP
WiFiUDP udp;              // Об'єкт для роботи з протоколом UDP

// Параметри для аудіо потоку
#define ADC_PIN 34           // Пін, до якого підключено мікрофон (аналоговий вхід)
#define SAMPLE_RATE 16000    // Частота дискретизації (16 кГц)
#define SAMPLES_PER_PACKET 256 // Кількість семплів в одному пакеті даних
#define BYTES_PER_SAMPLE 2   // Розмір одного семпла (16 біт = 2 байти)

uint16_t audioBuffer[SAMPLES_PER_PACKET]; // Буфер для накопичення аудіоданих
uint16_t sampleIndex = 0;                 // Поточний індекс у буфері

unsigned long lastSampleMicros = 0;                // Час останнього зняття заміру (мікросекунди)
const unsigned long sampleInterval = 1000000UL / SAMPLE_RATE; // Інтервал між замірами в мкс

WebServer server(80); // Веб-сервер на 80-му порту для сторінки конфігурації

Preferences preferences; // Об'єкт для збереження налаштувань у пам'ять

IPAddress savedIP; // Змінна для зберігання IP-адреси сервера
String savedSSID; // Назва Wi-Fi мережі
String savedPASS; // Пароль Wi-Fi
String savedSERV; // IP-адреса сервера
int savedPORT;    // Порт сервера

unsigned long apStartTime; // Час запуску точки доступу
bool configMode = true;    // Прапорець режиму конфігурації


// Веб інтерфейс для налаштування
// HTML-код сторінки, яка відображається при підключенні до ESP32
String htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Налаштування ESP32</title></head>
<body>
<h2>Налаштування стрімінгу</h2>
<form action="/save">
  Назва Wi-Fi (SSID):<br><input type="text" name="ssid"><br>
  Пароль:<br><input type="text" name="pass"><br><br>
  IP сервера:<br><input type="text" name="serv"><br>
  Порт:<br><input type="number" name="port"><br><br>
  <input type="submit" value="Зберегти та перезавантажити">
</form>
</body>
</html>
)rawliteral";

// Обробник головної сторінки веб-сервера
void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

// Обробник збереження даних з форми
void handleSave() {
  String ssid = server.arg("ssid");
  String pass = server.arg("pass");
  String serv = server.arg("serv");
  String port = server.arg("port");

// Відкриваємо сховище "config" у режимі читання/запису
  preferences.begin("config", false);
  preferences.putString("ssid", ssid);
  preferences.putString("pass", pass);
  preferences.putString("serv", serv);
  preferences.putInt("port", port.toInt());
  preferences.end();

  server.send(200, "text/html", "Дані збережено! ESP32 перезавантажується...");
  delay(1000);
  ESP.restart(); // Перезавантаження пристрою для застосування змін
}


// Підключення до вай-фаю
void connectToSavedWiFi() {
// Читаємо збережені дані з пам'яті
  preferences.begin("config", true);
  savedSSID = preferences.getString("ssid", "");
  savedPASS = preferences.getString("pass", "");
  savedSERV = preferences.getString("serv", "");
  savedPORT = preferences.getInt("port", 9000);
  
  savedIP.fromString(savedSERV); // Конвертуємо рядок IP у тип IPAddress
  preferences.end();

  if (savedSSID == "") {
    Serial.println("Помилка: Wi-Fi не налаштовано");
    return;
  }

  Serial.println("Підключення до: " + savedSSID);
  WiFi.begin(savedSSID.c_str(), savedPASS.c_str());

  int attempts = 0;
// Чекаємо підключення (максимум 20 спроб по 0.5 сек)
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nПідключено успішно!");
    Serial.println(WiFi.localIP());
    udp.begin(1234); // Відкриваємо локальний порт для UDP
  } else {
    Serial.println("\nНе вдалося підключитися до Wi-Fi");
  }
}


// Ініціалізація
void setup() {
  Serial.begin(115200);

// Налаштування АЦП (ADC)
  analogReadResolution(12);           // Роздільна здатність 12 біт (0-4095)
  analogSetPinAttenuation(ADC_PIN, ADC_11db); // Чутливість до 3.3В

// Спочатку запускаємо режим точки доступу (AP) для налаштування
  WiFi.mode(WIFI_AP);
  WiFi.softAP("ESP32_Config"); // Назва мережі, яку створює ESP32

  Serial.println("Точка доступу запущена. IP: ");
  Serial.println(WiFi.softAPIP());

// Налаштування шляхів веб-сервера
  server.on("/", handleRoot);
  server.on("/save", handleSave);
  server.begin();

  apStartTime = millis(); // Запам'ятовуємо час старту
}


// Основний цикл
void loop() {

// РЕЖИМ КОНФІГУРАЦІЇ (перші 20 секунд після ввімкнення)
  if (configMode) {
    server.handleClient(); // Обробляємо запити веб-користувачів

// Якщо час очікування (20 сек) вийшов
    if (millis() - apStartTime > 20000) {
      Serial.println("Час конфігурації вичерпано. Перехід у робочий режим.");
      
      WiFi.softAPdisconnect(true); // Вимикаємо точку доступу
      WiFi.mode(WIFI_STA);         // Перемикаємося в режим клієнта
      
      connectToSavedWiFi();        // Підключаємося до роутера
      configMode = false;          // Виходимо з режиму конфігурації
    }
    return; 
  // Поки ми в режимі конфігурації, аудіо не передаємо
  }

// Далі передача аудіо

  unsigned long now = micros(); // Отримуємо поточний час у мікросекундах

// Перевіряємо, чи настав час робити новий замір
  if (now - lastSampleMicros >= sampleInterval) {
    lastSampleMicros += sampleInterval;

// Зчитуємо значення з піна мікрофона та записуємо в буфер
    audioBuffer[sampleIndex++] = analogRead(ADC_PIN);

// Якщо буфер заповнився (256 замірів)
    if (sampleIndex >= SAMPLES_PER_PACKET) {
      // Відправляємо дані пакетною передачею по UDP
      udp.beginPacket(savedIP, savedPORT);
      udp.write((uint8_t*)audioBuffer, SAMPLES_PER_PACKET * BYTES_PER_SAMPLE);
      udp.endPacket();

      sampleIndex = 0; // Скидаємо індекс для нового накопичення
    }
  }
}