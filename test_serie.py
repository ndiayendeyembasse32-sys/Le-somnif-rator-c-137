import time
import serial
import threading
import tkinter as tk
from tkinter import ttk
import pygame

# --- CONFIGURATION ---
PORT_SERIE = "COM4"
BAUD_RATE = 9600
FICHIER_AUDIO = "rick_sanction.mp3"

# Initialisation audio
pygame.mixer.init()
try:
    son_sanction = pygame.mixer.Sound(FICHIER_AUDIO)
except Exception as e:
    print(f"Erreur audio : {e}")

# --- FENÊTRE GRAPHIQUE (DASHBOARD RICKLAB) ---
root = tk.Tk()
root.title("RickLab - Somniférator C-137 Control Center")
root.geometry("650x520")
root.configure(bg="#0B0F19")

# Titres
titre = tk.Label(root, text="SOMNIFÉRATOR C-137", font=("Helvetica", 22, "bold"), fg="#00FF9D", bg="#0B0F19")
titre.pack(pady=15)

sous_titre = tk.Label(root, text="Protocole de Confinement Nocturne de Morty", font=("Helvetica", 11, "italic"), fg="#8892B0", bg="#0B0F19")
sous_titre.pack()

# Cadre principal d'état
cadre = tk.Frame(root, bg="#111A2E", bd=2, relief="groove")
cadre.pack(pady=20, padx=30, fill="both", expand=True)

lbl_heure = tk.Label(cadre, text="HEURE SYSTÈME : 23:00", font=("Consolas", 15, "bold"), fg="#E6F1FF", bg="#111A2E")
lbl_heure.pack(pady=10)

lbl_status = tk.Label(cadre, text="ATTENTE DU DÉPÔT (1 min)", font=("Helvetica", 18, "bold"), fg="#FFB800", bg="#111A2E")
lbl_status.pack(pady=15)

lbl_loquet = tk.Label(cadre, text="Loquet Servomoteur : DÉVERROUILLÉ", font=("Helvetica", 13), fg="#CCD6F6", bg="#111A2E")
lbl_loquet.pack(pady=5)

lbl_action = tk.Label(cadre, text="Action : En attente du smartphone...", font=("Helvetica", 11), fg="#8892B0", bg="#111A2E")
lbl_action.pack(pady=10)

son_actif = False

# Mise à jour graphique
def actualiser_interface(statut):
    global son_actif
    if "23H_START" in statut:
        lbl_status.config(text="23:00 - ATTENTE DU DÉPÔT", fg="#FFB800")
        lbl_loquet.config(text="Loquet Servomoteur : OUVERT (Prêt à sceller)", fg="#FFB800")
        lbl_action.config(text="Morty a quelques secondes pour poser son smartphone.", fg="#CCD6F6")
        if not son_actif:
            son_sanction.play(loops=-1)
            son_actif = True

    elif "SCELLE" in statut:
        lbl_status.config(text="ÉTAPE 1 : BOÎTE SCELLÉE (JUSQU'À 07H)", fg="#00FF9D")
        lbl_loquet.config(text="Loquet Servomoteur : VERROUILLÉ (90°)", fg="#00FF9D")
        lbl_action.config(text="Smartphone confisqué avec succès. Nuit calme.", fg="#00FF9D")
        if son_actif:
            son_sanction.stop()
            son_actif = False

    elif "INFRACTION" in statut:
        lbl_status.config(text="ÉTAPE 2 : INFRACTION MORTY DÉTECTÉE !", fg="#FF0055")
        lbl_loquet.config(text="Loquet Servomoteur : AGITATION / SANCTION", fg="#FF0055")
        lbl_action.config(text="Alerte sonore maximale déclenchée !", fg="#FF0055")
        if not son_actif:
            son_sanction.play(loops=-1)
            son_actif = True

# Thread de lecture Série Arduino
def boucle_serie():
    try:
        ser = serial.Serial(PORT_SERIE, BAUD_RATE, timeout=1)
        time.sleep(2)
        while True:
            ligne_bytes = ser.readline()
            if ligne_bytes:
                ligne = ligne_bytes.decode("utf-8", errors="ignore").strip()
                if "STATUS:" in ligne:
                    statut = ligne.split("STATUS:")[1]
                    root.after(0, actualiser_interface, statut)
    except Exception as e:
        print(f"Erreur série : {e}")

threading.Thread(target=boucle_serie, daemon=True).start()

root.mainloop()
