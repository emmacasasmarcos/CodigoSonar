#include <Servo.h>

#define TRIG_PIN 10
#define ECHO_PIN 11
#define SERVO_PIN 12

Servo myServo;

int angle = 15;
int step = 1;
bool servoActivo = true;   // 👈 control del servo

// --- Medir distancia ---
int medirDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  int distance = duration * 0.034 / 2;

  return distance;
}

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.begin(9600);
  myServo.attach(SERVO_PIN);
}

void loop() {

  if (Serial.available()) {
  char cmd = Serial.read();

  if (cmd == 'S') {
    servoActivo = false;
  }
  if (cmd == 'R') {
    servoActivo = true;
  }
}

  // --- Medición SIEMPRE activa ---
  int distancia = medirDistancia();

  // --- Envío SIEMPRE activo ---
  Serial.print(angle);
  Serial.print(",");
  Serial.print(distancia);
  Serial.print(".");

  // --- Control del servo ---
  if (servoActivo) {
    myServo.write(angle);

    angle += step;

    if (angle >= 165 || angle <= 15) {
      step = -step;
    }
  }

  delay(50);
}
