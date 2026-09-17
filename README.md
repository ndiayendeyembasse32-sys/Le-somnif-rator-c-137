[README (2).md](https://github.com/user-attachments/files/32326746/README.2.md)
# Somniférator C-137

**Workshop National B2 EPSI — Thème RickLab™**

Dispositif interdimensionnel qui force Morty à déposer son smartphone au coucher (23h00), sous peine de sanction sonore et mécanique.

## Équipe

| Membre | Rôle |
|---|---|
| Lamine | Lead Robotique & Scripting Ned2 |
| Ndeye Mbasse | Lead Électronique & Embarqué |
| Yanis | Lead Intégration Logicielle & Audio |
| Awa | Lead Fabrication myDiL & Design CAO |
| Amar | Lead Gestion de Projet, Livrables & Vidéo |

## Concept

À 23h00, le système s'active (LED rouge + signal sonore). Morty a un délai de grâce pour déposer son smartphone devant le capteur.

- **Téléphone déposé à temps** → boîte scellée (loquet verrouillé à 90°) jusqu'à 7h, LED verte, son coupé.
- **Téléphone non déposé ou retiré** → infraction : alerte sonore intensifiée + agitation du loquet.

**Idée initiale et perspectives** : le concept d'origine prévoyait un bras robotisé Niryo Ned2 saisissant physiquement le téléphone (mode pince) en cas de dépôt conforme, et un tir au « pistolet portail » pour envoyer le téléphone dans une autre dimension en cas d'infraction. Le Ned2 ayant présenté des dysfonctionnements pendant le workshop, l'équipe a pivoté vers un mécanisme de confinement par servomoteur pour garantir une démonstration fiable. La réintégration du Ned2 est présentée en amélioration future (voir dossier technique).

## Architecture

```
[HC-SR04] --distance--> [Arduino Uno] --USB série 9600 bauds--> [PC / somniferator_audio.py]
    |                         |
 mesure                  LEDs + Servo (loquet)
```

### Partie embarquée — `rickworkshop.ino`

Machine à états (`ATTENTE_DEPOT` → `SCELLE_CONFORME` / `INFRACTION`) pilotée par la distance mesurée sur le capteur à ultrasons. Envoie l'état courant sur le port série (`STATUS:23H_START`, `STATUS:SCELLE`, `STATUS:INFRACTION`).

### Partie logicielle — `somniferator_audio.py`

Dashboard Tkinter qui lit le port série et affiche en direct :
- l'état du système et du loquet
- un compte à rebours pendant la phase d'attente
- un journal horodaté des événements
- les statistiques de session (nb d'infractions, temps total scellé)
- l'état de connexion Arduino (avec détection de signal perdu)

Déclenche également la lecture d'une réplique audio (`rick_sanction.mp3`) via `pygame` selon l'état.

## Matériel & câblage

| Composant | Broche / Fil | Connexion Arduino / Breadboard |
|---|---|---|
| Alimentation générale | Broche `5V` | Rail rouge (+) |
| Masse générale | Broche `GND` | Rail bleu (-) |
| LED Verte | Anode | `D7` |
| LED Verte | Cathode | Rail bleu (-) via résistance 220Ω |
| LED Rouge | Anode | `D8` |
| LED Rouge | Cathode | Rail bleu (-) via résistance 220Ω |
| HC-SR04 | `VCC` | Rail rouge (+) 5V |
| HC-SR04 | `TRIG` | `D9` |
| HC-SR04 | `ECHO` | `D10` |
| HC-SR04 | `GND` | Rail bleu (-) |
| Servomoteur SG90 | Fil rouge (alim) | Rail rouge (+) 5V |
| Servomoteur SG90 | Fil marron/noir (masse) | Rail bleu (-) |
| Servomoteur SG90 | Fil orange/jaune (signal) | `D6` |

## Installation & lancement

1. Flasher `rickworkshop.ino` sur l'Arduino Uno via l'IDE Arduino (sélectionner le bon port COM).
2. Vérifier/ajuster `PORT_SERIE` dans `somniferator_audio.py` (par défaut `COM4`).
3. Placer le fichier `rick_sanction.mp3` dans le même dossier que `somniferator_audio.py`.
4. Installer les dépendances Python :
   ```
   pip install pyserial pygame
   ```
5. Lancer le dashboard :
   ```
   python somniferator_audio.py
   ```

## Structure du dépôt

```
.
├── rickworkshop.ino          # code embarqué Arduino
├── somniferator_audio.py     # dashboard Python (audio + interface)
├── rick_sanction.mp3         # réplique audio de sanction
├── schema/                   # export Tinkercad du montage
└── docs/                     # dossier technique, poster, support de présentation
```

## Difficultés & limites connues

- Bras robotisé Niryo Ned2 non intégré à la démo finale (dysfonctionnement matériel pendant le workshop).
- Délai de grâce réglé à 10 secondes pour la démonstration jury (au lieu d'1 minute en usage réel) — voir `DELAI_GRACE_MS` dans `rickworkshop.ino`.

## Améliorations futures

- Réintégration du bras Niryo Ned2 (préhension physique du téléphone + scénario « pistolet portail »).
- Persistance des statistiques de session entre les lancements du dashboard.
