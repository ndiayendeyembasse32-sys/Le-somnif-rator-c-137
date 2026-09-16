#include <Servo.h>

#define TRIG_PIN 9
#define ECHO_PIN 10
#define LED_VERTE 7
#define LED_ROUGE 8
#define SERVO_PIN 6

const int SEUIL_DISTANCE_CM = 8;
Servo servoSanction;

void setup() {
  Serial.begin(9600);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_VERTE, OUTPUT);
  pinMode(LED_ROUGE, OUTPUT);

  digitalWrite(LED_VERTE, LOW);
  digitalWrite(LED_ROUGE, LOW);

  // Initialisation du servomoteur
  servoSanction.attach(SERVO_PIN);

  // ==========================================
  // --- TESTEUR DE SERVOMOTEUR AU DEMARRAGE ---
  // ==========================================
  Serial.println("=== TEST DU SERVOMOTEUR EN COURS ===");

  // 1. Position zéro (repos)
  Serial.println("Position 0 degres");
  servoSanction.write(0);
  delay(1000);

  // 2. Balayage lent de 0 a 180 degres (pour observer la course complete)
  Serial.println("Balayage progressif de 0 a 180 degres...");
  for (int angle = 0; angle <= 180; angle += 10) {
    servoSanction.write(angle);
    delay(50);
  }
  delay(500);

  // 3. Retour a la position repos (0 degres)
  Serial.println("Retour a 0 degres (pret pour la detection)");
  servoSanction.write(0);
  delay(1000);

  Serial.println("=== FIN DU TEST - SYSTEME OPERATIONNEL ===");
}

void loop() {
  // Envoi de l'impulsion ultrasonique
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duree = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = (duree * 0.034) / 2.0;

  // CAS 1 : Objet / Smartphone detecte sur le socle (distance <= 8 cm)
  if (distance > 0 && distance <= SEUIL_DISTANCE_CM) {
    digitalWrite(LED_VERTE, HIGH);
    digitalWrite(LED_ROUGE, LOW);

    // Le bras reste au repos a plat
    servoSanction.write(0);

    Serial.print("Distance : ");
    Serial.print(distance);
    Serial.println(" cm -> PRESENT");
  } 
  // CAS 2 : Smartphone retire (infraction Morty)
  else {
    digitalWrite(LED_VERTE, LOW);
    digitalWrite(LED_ROUGE, HIGH);

    // Mouvement d'agitation de sanction
    servoSanction.write(80);
    delay(150);
    servoSanction.write(10);

    Serial.print("Distance : ");
    Serial.print(distance);
    Serial.println(" cm -> ABSENT (ALERTE)");
  }

  delay(200);
}
