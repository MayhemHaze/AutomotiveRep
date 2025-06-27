#include <Arduino.h>

// Ponte UART: ESP32 se comporta como um conversor USB-TTL

void setup() {
  Serial.begin(115200);      // Porta USB para comunicação com o PC
  Serial2.begin(9600, SERIAL_8N1, 16, 17); // RX (GPIO16), TX (GPIO17)

  Serial.println("ESP32 UART Bridge iniciado");
}

void loop() {
  // Transfere dados do PC para o dispositivo conectado na Serial2
  while (Serial.available()) {
    Serial2.write(Serial.read());
  }

  // Transfere dados do dispositivo Serial2 para o PC
  while (Serial2.available()) {
    Serial.write(Serial2.read());
  }
}