import time
import datetime
import serial
import threading
import tkinter as tk
from tkinter import ttk
import pygame

# --- CONFIGURATION ---
PORT_SERIE = "COM4"
BAUD_RATE = 9600
FICHIER_AUDIO = "rick_sanction.mp3"
GRACE_PERIOD_SEC = 10      # doit correspondre à DELAI_GRACE_MS / 1000 côté Arduino !
SIGNAL_TIMEOUT_SEC = 5     # au-delà, on considère le signal Arduino perdu

# Initialisation audio
pygame.mixer.init()
son_sanction = None
try:
    son_sanction = pygame.mixer.Sound(FICHIER_AUDIO)
except Exception as e:
    print(f"Erreur audio : {e}")

# --- FENÊTRE GRAPHIQUE (DASHBOARD RICKLAB) ---
root = tk.Tk()
root.title("RickLab - Somniférator C-137 Control Center")
root.geometry("700x760")
root.configure(bg="#0B0F19")

titre = tk.Label(root, text="SOMNIFÉRATOR C-137", font=("Helvetica", 22, "bold"), fg="#00FF9D", bg="#0B0F19")
titre.pack(pady=(15, 0))

sous_titre = tk.Label(root, text="Protocole de Confinement Nocturne de Morty", font=("Helvetica", 11, "italic"), fg="#8892B0", bg="#0B0F19")
sous_titre.pack()

# --- Indicateur de connexion Arduino ---
cadre_connexion = tk.Frame(root, bg="#0B0F19")
cadre_connexion.pack(pady=8)
lbl_dot = tk.Label(cadre_connexion, text="●", font=("Helvetica", 14), fg="#FF0055", bg="#0B0F19")
lbl_dot.pack(side="left", padx=4)
lbl_connexion = tk.Label(cadre_connexion, text="Arduino : déconnecté", font=("Consolas", 10), fg="#8892B0", bg="#0B0F19")
lbl_connexion.pack(side="left")

# --- Cadre principal d'état ---
cadre = tk.Frame(root, bg="#111A2E", bd=2, relief="groove")
cadre.pack(pady=15, padx=30, fill="x")

lbl_heure = tk.Label(cadre, text="HEURE SYSTÈME : 23:00", font=("Consolas", 15, "bold"), fg="#E6F1FF", bg="#111A2E")
lbl_heure.pack(pady=10)

lbl_status = tk.Label(cadre, text="ATTENTE DU DÉPÔT", font=("Helvetica", 18, "bold"), fg="#FFB800", bg="#111A2E")
lbl_status.pack(pady=10)

lbl_countdown = tk.Label(cadre, text="", font=("Consolas", 26, "bold"), fg="#FFB800", bg="#111A2E")
lbl_countdown.pack(pady=5)

lbl_loquet = tk.Label(cadre, text="Loquet Servomoteur : DÉVERROUILLÉ", font=("Helvetica", 13), fg="#CCD6F6", bg="#111A2E")
lbl_loquet.pack(pady=5)

lbl_action = tk.Label(cadre, text="Action : En attente du smartphone...", font=("Helvetica", 11), fg="#8892B0", bg="#111A2E")
lbl_action.pack(pady=(5, 15))

# --- Cadre statistiques de session ---
cadre_stats = tk.Frame(root, bg="#111A2E", bd=2, relief="groove")
cadre_stats.pack(pady=(0, 15), padx=30, fill="x")

tk.Label(cadre_stats, text="STATISTIQUES DE SESSION", font=("Helvetica", 11, "bold"), fg="#00FF9D", bg="#111A2E").pack(pady=(8, 4))

lbl_stats = tk.Label(cadre_stats, text="Infractions : 0    |    Temps scellé : 00:00", font=("Consolas", 12), fg="#CCD6F6", bg="#111A2E")
lbl_stats.pack(pady=(0, 10))

# --- Cadre historique des événements ---
cadre_historique = tk.Frame(root, bg="#111A2E", bd=2, relief="groove")
cadre_historique.pack(pady=(0, 15), padx=30, fill="both", expand=True)

tk.Label(cadre_historique, text="JOURNAL DES ÉVÉNEMENTS", font=("Helvetica", 11, "bold"), fg="#00FF9D", bg="#111A2E").pack(pady=(8, 4))

frame_liste = tk.Frame(cadre_historique, bg="#111A2E")
frame_liste.pack(fill="both", expand=True, padx=10, pady=(0, 10))

scrollbar = tk.Scrollbar(frame_liste)
scrollbar.pack(side="right", fill="y")

liste_historique = tk.Listbox(frame_liste, bg="#0B0F19", fg="#CCD6F6", font=("Consolas", 10),
                               yscrollcommand=scrollbar.set, bd=0, highlightthickness=0)
liste_historique.pack(side="left", fill="both", expand=True)
scrollbar.config(command=liste_historique.yview)

# --- ÉTAT PARTAGÉ ---
son_actif = False
etat_precedent = None
nb_infractions = 0
temps_scelle_total = 0     # en secondes
countdown_restant = GRACE_PERIOD_SEC
countdown_actif = False
dernier_message_ts = 0
arduino_connecte = False


def ajouter_historique(texte):
    horodatage = datetime.datetime.now().strftime("%H:%M:%S")
    liste_historique.insert(tk.END, f"[{horodatage}] {texte}")
    liste_historique.yview(tk.END)


def formater_mmss(secondes):
    m, s = divmod(int(secondes), 60)
    return f"{m:02d}:{s:02d}"


def maj_stats():
    lbl_stats.config(text=f"Infractions : {nb_infractions}    |    Temps scellé : {formater_mmss(temps_scelle_total)}")


def maj_connexion(connecte):
    global arduino_connecte
    arduino_connecte = connecte
    if connecte:
        lbl_dot.config(fg="#00FF9D")
        lbl_connexion.config(text=f"Arduino : connecté ({PORT_SERIE})")
    else:
        lbl_dot.config(fg="#FF0055")
        lbl_connexion.config(text="Arduino : déconnecté")


# Mise à jour graphique sur réception d'un STATUS (une seule fois par transition)
def actualiser_interface(statut):
    global son_actif, etat_precedent, nb_infractions, countdown_restant, countdown_actif, dernier_message_ts

    dernier_message_ts = time.time()
    if not arduino_connecte:
        maj_connexion(True)

    if statut == etat_precedent:
        return  # on ignore les répétitions, on ne journalise que les transitions
    etat_precedent = statut

    if "23H_START" in statut:
        lbl_status.config(text="23:00 - ATTENTE DU DÉPÔT", fg="#FFB800")
        lbl_loquet.config(text="Loquet Servomoteur : OUVERT (Prêt à sceller)", fg="#FFB800")
        lbl_action.config(text="Morty a quelques secondes pour poser son smartphone.", fg="#CCD6F6")
        countdown_restant = GRACE_PERIOD_SEC
        countdown_actif = True
        ajouter_historique("Démarrage — attente du dépôt du smartphone")
        if not son_actif:
            if son_sanction:
                son_sanction.play(loops=-1)
            son_actif = True

    elif "SCELLE" in statut:
        countdown_actif = False
        lbl_countdown.config(text="")
        lbl_status.config(text="ÉTAPE 1 : BOÎTE SCELLÉE (JUSQU'À 07H)", fg="#00FF9D")
        lbl_loquet.config(text="Loquet Servomoteur : VERROUILLÉ (90°)", fg="#00FF9D")
        lbl_action.config(text="Smartphone confisqué avec succès. Nuit calme.", fg="#00FF9D")
        ajouter_historique("Smartphone déposé — boîte scellée")
        if son_actif:
            if son_sanction:
                son_sanction.stop()
            son_actif = False

    elif "INFRACTION" in statut:
        countdown_actif = False
        lbl_countdown.config(text="")
        lbl_status.config(text="ÉTAPE 2 : INFRACTION MORTY DÉTECTÉE !", fg="#FF0055")
        lbl_loquet.config(text="Loquet Servomoteur : AGITATION / SANCTION", fg="#FF0055")
        lbl_action.config(text="Alerte sonore maximale déclenchée !", fg="#FF0055")
        nb_infractions += 1
        ajouter_historique("Infraction détectée — sanction déclenchée")
        maj_stats()
        if not son_actif:
            if son_sanction:
                son_sanction.play(loops=-1)
            son_actif = True


# Boucle locale (1x/seconde) : countdown, temps scellé cumulé, surveillance du signal
def tick():
    global countdown_restant, temps_scelle_total

    if countdown_actif:
        countdown_restant = max(0, countdown_restant - 1)
        lbl_countdown.config(text=formater_mmss(countdown_restant))

    if etat_precedent is not None and "SCELLE" in etat_precedent:
        temps_scelle_total += 1
        maj_stats()

    if arduino_connecte and dernier_message_ts and (time.time() - dernier_message_ts) > SIGNAL_TIMEOUT_SEC:
        maj_connexion(False)
        ajouter_historique("Signal Arduino perdu")

    root.after(1000, tick)


# Thread de lecture Série Arduino
def boucle_serie():
    try:
        ser = serial.Serial(PORT_SERIE, BAUD_RATE, timeout=1)
        time.sleep(2)
        root.after(0, maj_connexion, True)
        root.after(0, ajouter_historique, f"Connexion série établie sur {PORT_SERIE}")
        while True:
            ligne_bytes = ser.readline()
            if ligne_bytes:
                ligne = ligne_bytes.decode("utf-8", errors="ignore").strip()
                if "STATUS:" in ligne:
                    statut = ligne.split("STATUS:")[1]
                    root.after(0, actualiser_interface, statut)
    except Exception as e:
        print(f"Erreur série : {e}")
        root.after(0, maj_connexion, False)


threading.Thread(target=boucle_serie, daemon=True).start()
root.after(1000, tick)
root.mainloop()
