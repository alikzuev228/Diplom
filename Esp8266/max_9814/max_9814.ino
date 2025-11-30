void setup() {
  Serial.begin(115200);
}

float max_size = 0.0;

void loop() {
  //Serial.println(max_size);
  
  float old_size = analogRead(0);
  if (old_size > max_size)
  {
    max_size = old_size;
    Serial.print("Максимальне значення: ");
    Serial.println(max_size);
  }

  if (analogRead(0) >= 715) Serial.println("pulse!");


  delay(10);
}