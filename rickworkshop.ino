#define TRIG_PIN 9
#define ECHO_PIN 10
#define LED_VERTE 7
#define LED_ROUGE 8

// Seuil de détection en centimètres
const int SEUIL_DISTANCE_CM = 8;

void setup() {
  Serial.begin(9600);

  // Configuration des broches
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_VERTE, OUTPUT);
  pinMode(LED_ROUGE, OUTPUT);

  // Initialisation : les LED sont éteintes au démarrage
  digitalWrite(LED_VERTE, LOW);
  digitalWrite(LED_ROUGE, LOW);
}

void loop() {
  // Génération de l'impulsion ultrasonique de 10 microsecondes
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Mesure du temps de retour de l'écho (timeout à 30 ms pour éviter le blocage)
  long duree = pulseIn(ECHO_PIN, HIGH, 30000);

  // Calcul de la distance en cm (vitesse du son : 340 m/s => 0.034 cm/µs)
  float distance = (duree * 0.034) / 2.0;

  // Affichage de contrôle dans le moniteur série
  Serial.print("Distance mesuree : ");
  Serial.print(distance);
  Serial.print(" cm -> Statut : ");

  // Condition : objet détecté entre 0 et 8 cm
  if (distance > 0 && distance <= SEUIL_DISTANCE_CM) {
    digitalWrite(LED_VERTE, HIGH);
    digitalWrite(LED_ROUGE, LOW);
    Serial.println("PRESENT");
  } else {
    digitalWrite(LED_VERTE, LOW);
    digitalWrite(LED_ROUGE, HIGH);
    Serial.println("ABSENT");
  }

  // Pause de lecture pour stabiliser les mesures
  delay(200);
}
