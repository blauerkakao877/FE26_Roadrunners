# Programm, um Lidar Daten in CSV-Datei zu schreiben
# Format: Ein Scan pro Zeile, 360 Zahlen in mm mit Komma getrennt von 0 Grad bis 359 Grad

from multiprocessing import shared_memory
from multiprocessing.resource_tracker import unregister
import numpy as np
import time
from datetime import datetime
import os
import csv
import signal

ARRAY_SIZE = 360
SHM_NAME = "lidar360"
SHM_SIGNAL_NAME = "rr_signal"


class LIDAR_LOGGER:
    def __init__(self):
        # 1. Shared Memory öffnen, nicht initialisieren
        try:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=ARRAY_SIZE * 4)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME)
        
        # 2. WICHTIG: Den Resource Tracker anweisen, dieses Segment zu ignorieren.
        # Damit wird verhindert, dass der Tracker beim Beenden 'unlink()' ruft.
        unregister(self.shm._name, 'shared_memory')

        self.distances = np.ndarray((ARRAY_SIZE,), dtype=np.int32, buffer=self.shm.buf)

# Shared Memory für Start-Signal:
        try:
            self.shm_signal = shared_memory.SharedMemory(name=SHM_SIGNAL_NAME, create=True, size=4)
        except FileExistsError:
            self.shm_signal = shared_memory.SharedMemory(name=SHM_SIGNAL_NAME)
            
        # Den Wert auf 0 setzen macht schon der Lidar_reader!
        
        #Öffne Log-Datei
        folder="/home/pi/FE_2026/Lidar_Logs"
        os.makedirs(folder, exist_ok=True)
        self.filename = os.path.join(folder, f"fahrt_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")
        

    def wait_for_start(self):
        while self.shm_signal.buf[0] == 0:
            time.sleep(0.02)

    def close(self):
        """Zentralisierte Aufräum-Logik."""
        #schließe Lidar logfile
        #Shared Memory freigeben
        self.shm.close()
        self.shm_signal.close()

    # 1. Der "klassische" Destruktor (Garbage Collection)
    def __del__(self):
        self.close()

    # 2. Context Manager (für das 'with'-Statement)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

if __name__ == "__main__":
    print("Start Lidar Logger")
    lidar = LIDAR_LOGGER()
    
    #warte auf Startknopf-Signal wg Regel 6.12
    print("Warte auf Start Signal")
    lidar.wait_for_start()
    print("Start Signal")
    with open(lidar.filename, 'w', newline='') as csvfile:
        
        ldwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        try:
            while True:
                #Lese Lidar Daten, generiere csv-Zeile
                    
                ldwriter.writerow(lidar.distances)
                # Check stop signal
                if (lidar.shm_signal.buf[1] == 1):
                    raise(KeyboardInterrupt)
                    break
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopping Lidar Data Logger.")
        finally:
            lidar.close()
