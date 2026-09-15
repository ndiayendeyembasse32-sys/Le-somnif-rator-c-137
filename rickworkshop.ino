#define TRIG_PIN 9
#define ECHO_PIN 10
#define LED_VERTE 7
#define LED_ROUGE 8

// Seuil de détection en cm
const int SEUIL_DISTANCE_CM = 8;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_VERTE, OUTPUT);
  pinMode(LED_ROUGE, OUTPUT);

  digitalWrite(LED_VERTE, LOW);
  digitalWrite(LED_ROUGE, LOW);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duree = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = duree * 0.034 / 2.0;

  // Si un objet est détecté à moins de 8 cm
  if (distance > 0 && distance <= SEUIL_DISTANCE_CM) {
    digitalWrite(LED_VERTE, HIGH);
    digitalWrite(LED_ROUGE, LOW);
    Serial.println("PRESENT");
  } else {
    digitalWrite(LED_VERTE, LOW);
    digitalWrite(LED_ROUGE, HIGH);
    Serial.println("ABSENT");
  }

  delay(300);
}