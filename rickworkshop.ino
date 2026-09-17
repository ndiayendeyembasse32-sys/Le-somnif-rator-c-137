#include <Servo.h>

#define TRIG_PIN 9
#define ECHO_PIN 10
#define LED_VERTE 7
#define LED_ROUGE 8
#define SERVO_PIN 6

const int SEUIL_DISTANCE_CM = 8;
Servo servoVerrou;

// Réglage démo jury : 10 secondes (ou 60000 pour 1 min)
const unsigned long DELAI_GRACE_MS = 10000; 

enum EtatSysteme {
  ATTENTE_DEPOT,   // 23:00 : Alerte début, Morty a un délai pour poser son tel
  SCELLE_CONFORME, // Posé à temps : Loquet verrouillé (90°), LED Verte
  INFRACTION       // Non posé à temps ou retiré : Alerte son intensifié + battement servo
};

EtatSysteme etatCourant = ATTENTE_DEPOT;
unsigned long debutAttenteMs = 0;

float mesurerDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duree = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duree == 0) return 999.0;
  return (duree * 0.034) / 2.0;
}

void setup() {
  Serial.begin(9600);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_VERTE, OUTPUT);
  pinMode(LED_ROUGE, OUTPUT);

  servoVerrou.attach(SERVO_PIN);
  servoVerrou.write(0); // Loquet ouvert au départ

  // 23:00 - Mise sous tension
  digitalWrite(LED_ROUGE, HIGH);
  digitalWrite(LED_VERTE, LOW);
  debutAttenteMs = millis();
  
  Serial.println("STATUS:23H_START");
}

void loop() {
  float distance = mesurerDistance();
  bool telephonePresent = (distance > 0 && distance <= SEUIL_DISTANCE_CM);

  switch (etatCourant) {
    case ATTENTE_DEPOT:
      // Pendant la phase de grâce : LED Rouge allumée
      digitalWrite(LED_ROUGE, HIGH);
      digitalWrite(LED_VERTE, LOW);
      servoVerrou.write(0); // Boîte ouverte, attend le téléphone

      if (telephonePresent) {
        // Le téléphone a été déposé : VERROUILLAGE
        etatCourant = SCELLE_CONFORME;
        servoVerrou.write(90); // Loquet tourne à 90° et scelle la boîte
        digitalWrite(LED_ROUGE, LOW);
        digitalWrite(LED_VERTE, HIGH);
        Serial.println("STATUS:SCELLE");
      } 
      else if (millis() - debutAttenteMs >= DELAI_GRACE_MS) {
        // Temps écoulé sans téléphone -> INFRACTION
        etatCourant = INFRACTION;
        Serial.println("STATUS:INFRACTION");
      }
      break;

    case SCELLE_CONFORME:
      // Le téléphone doit rester dedans
      if (telephonePresent) {
        digitalWrite(LED_VERTE, HIGH);
        digitalWrite(LED_ROUGE, LOW);
        servoVerrou.write(90); // Reste scellé
        Serial.println("STATUS:SCELLE");
      } else {
        // Vol ou retrait interdit : Infraction immédiate
        etatCourant = INFRACTION;
        Serial.println("STATUS:INFRACTION");
      }
      break;

    case INFRACTION:
      // Alerte rouge permanente + agitation servo de sanction
      digitalWrite(LED_VERTE, LOW);
      digitalWrite(LED_ROUGE, HIGH);
      
      servoVerrou.write(80);
      delay(120);
      servoVerrou.write(10);
      
      Serial.println("STATUS:INFRACTION");

      // Si Morty finit par le reposer
      if (telephonePresent) {
        etatCourant = SCELLE_CONFORME;
        servoVerrou.write(90);
        Serial.println("STATUS:SCELLE");
      }
      break;
  }

  delay(200);
}
