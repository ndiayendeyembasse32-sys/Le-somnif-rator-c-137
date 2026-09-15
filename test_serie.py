import serial
import time

PORT_SERIE = "COM4"  # Ton port Arduino
BAUDRATE = 9600

try:
    ser = serial.Serial(PORT_SERIE, BAUDRATE, timeout=1)
    time.sleep(2)
    print(f"Connecte a l'Arduino sur {PORT_SERIE} ! En attente du capteur...")

    while True:
        if ser.in_waiting > 0:
            message = ser.readline().decode('utf-8', errors='ignore').strip()
            if message:
                print(f"[RECU ARDUINO] : {message}")

except serial.SerialException as e:
    print(f"Erreur d'acces a {PORT_SERIE} : ferme bien le moniteur serie Arduino !")
except KeyboardInterrupt:
    print("\nArret du test.")
    ser.close()