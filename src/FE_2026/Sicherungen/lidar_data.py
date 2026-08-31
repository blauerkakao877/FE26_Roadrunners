
from multiprocessing import shared_memory
from multiprocessing.resource_tracker import unregister
import numpy as np
import time

ARRAY_SIZE = 360
SHM_NAME = "lidar360"
SHM_SIGNAL_NAME = "rr_signal"


class LIDAR_DATA:
    def __init__(self):
        # 1. Shared Memory öffnen, nicht initialisieren
        try:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=ARRAY_SIZE * 4)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=SHM_NAME)

        try:
            self.shm_signal = shared_memory.SharedMemory(name=SHM_SIGNAL_NAME, create=True, size=4)
        except FileExistsError:
            self.shm_signal = shared_memory.SharedMemory(name=SHM_SIGNAL_NAME)
        
        
        # 2. WICHTIG: Den Resource Tracker anweisen, dieses Segment zu ignorieren.
        # Damit wird verhindert, dass der Tracker beim Beenden 'unlink()' ruft.
        unregister(self.shm._name, 'shared_memory')
        unregister(self.shm_signal._name, 'shared_memory')

        self.distances = np.ndarray((ARRAY_SIZE,), dtype=np.int32, buffer=self.shm.buf)
        
        #self.mySize = np.zeros(360, dtype=int)
        #gemessene Abstände Lidar- Rand des Autos
        self.mySize = (48,48,48,48,48,48,48,48,47,47,48,49,49,50,50,51,51,51,51,52,52,52,53,52,52,52,52,52,52,52,52,52,52,52,52,53,53,53,53,54,54,54,54,54,54,54,55,55,55,55,55,55,55,55,55,54,53,52,52,53,53,54,54,53,53,53,52,52,52,51,51,50,50,50,49,48,48,48,48,48,49,49,49,49,49,49,49,49,49,49,49,49,49,49,50,50,50,52,52,53,53,54,55,55,55,55,56,56,56,57,57,58,59,59,60,61,62,63,64,65,65,65,66,67,68,68,69,71,72,75,75,77,77,78,81,82,84,86,88,91,93,96,99,101,105,108,113,114,116,118,119,122,123,124,124,124,123,123,123,122,122,120,119,119,118,118,117,115,115,115,115,115,114,114,113,111,110,108,108,108,108,108,109,109,110,112,113,114,115,115,115,115,116,116,116,117,118,119,120,120,120,121,120,120,119,118,117,114,113,112,109,106,104,99,97,95,91,89,88,85,84,82,81,79,77,76,73,72,69,69,69,69,67,66,66,64,63,62,61,61,60,60,60,59,58,57,57,56,56,56,55,55,54,54,53,53,52,52,52,51,51,51,51,51,51,51,51,51,51,50,50,51,51,51,52,52,52,52,52,52,53,54,54,54,54,55,55,56,56,57,57,57,57,57,55,54,54,54,54,54,54,55,57,57,57,56,55,54,54,54,54,54,54,54,54,54,54,53,53,53,53,54,54,54,53,53,53,53,53,53,53,52,51,51,52,52,51,50,50,50,50,50,50,50,50,50,50,50,50,50,49,49,49,49,49,47,47,47,47,47)
        
        
    # -----------------------------
    # Signal helper methods
    # -----------------------------
    def send_start_signal(self, my_delay=0.1):
        
        self.shm_signal.buf[0] = 1
        print("Sende start signal an Lidar Reader/Logger")
        time.sleep(my_delay)
        
    def send_stop_signal(self, my_delay=0.1):
        
        self.shm_signal.buf[1] = 1
        print("Sende stop signal an Lidar Reader/Logger")
        time.sleep(my_delay)

            
    def getDistance(self, winkel):
        # winkel relative zum Auto
        dist = self.distances[winkel]
        if  dist == 0: #Messfehler!
            #Mittel aus vorigem und nächtem Wert
            vor_winkel = winkel -1
            if vor_winkel == -1:
                vor_winkel = 359
                
            nach_winkel = winkel + 1
            if nach_winkel == 360:
                nach_winkel = 0
                
            dist = int((self.distances[vor_winkel] + self.distances[nach_winkel])/2)
        
        return dist
    
    def getDistance_Feld(self, feldwinkel,gyrowinkel):
        # feldwinkel: winkel relativ zum Spielfeld
        # z.B. für Wandabstände korrigiert um die Ausrichtung 
        # Lidar-Winkel: 0-360, feldwinkel und gyroWinkel: -180 - 180
        LDGyrowinkel = gyrowinkel % 360
        LDFeldwinkel = (360 + feldwinkel) % 360
        winkel = (LDFeldwinkel - LDGyrowinkel) % 360
        dist = self.distances[winkel]
        if  dist == 0: #Messfehler!
            #Mittel aus vorigem und nächtem Wert
            vor_winkel = winkel -1
            if vor_winkel == -1:
                vor_winkel = 359
                
            nach_winkel = winkel + 1
            if nach_winkel == 360:
                nach_winkel = 0
                
            dist = int((self.distances[vor_winkel] + self.distances[nach_winkel])/2)
        
        return dist


    def getMin_Dist_Bereich(self,start_winkel,end_winkel,im_uhrzeiger= True):
        #kürzester Abstand vom Lidar in Bereich
        # start_winkel im Uhrzeigersinn vor end_winkel!
        
        start = start_winkel % 360
        ende = end_winkel % 360
        
        if im_uhrzeiger:     #scan im Uhrzeigersinn
            minDist_winkel = start
            minDist_wert = self.distances[minDist_winkel]
            winkel = start

            while winkel != ende:
                winkel = (winkel + 1) % 360
                wert = self.distances[winkel]
                if wert > 0 and wert < minDist_wert:
                    minDist_winkel = winkel
                    minDist_wert = wert
                    
        else: #scan gegen den Uhrzeiger
            minDist_winkel = ende
            minDist_wert = self.distances[minDist_winkel]
            winkel = ende

            while winkel != start:
                if winkel == 0:
                    winkel = 360
                winkel = (winkel - 1) % 360
                wert = self.distances[winkel]
                if wert > 0 and wert < minDist_wert:
                    minDist_winkel = winkel
                    minDist_wert = wert
            
            
        return minDist_winkel, minDist_wert
    
    def getMin_Dist_Bereich_RR(self,start_winkel,end_winkel,im_uhrzeiger=True):
        # kürzester Abstand vom Auto in Bereich
        # start_winkel im Uhrzeigersinn vor end_winkel!
        
        start = start_winkel % 360
        ende = end_winkel % 360
        
        if im_uhrzeiger:
            minDist_winkel = start
            
            minDist_wert = self.distances[minDist_winkel] - self.mySize[minDist_winkel]
            if minDist_wert < 0:
                minDist_wert = 0
                    
            winkel = start
            while winkel != ende:
                winkel = (winkel + 1) % 360
                wert = self.distances[winkel] - self.mySize[winkel]
                if wert < 0:
                    wert= 0
                    
                if wert > 0 and wert < minDist_wert:
                    minDist_winkel = winkel
                    minDist_wert = wert
        else:
            minDist_winkel = ende
            
            minDist_wert = self.distances[minDist_winkel] - self.mySize[minDist_winkel]
            if minDist_wert < 0:
                minDist_wert = 0
                    
            winkel = ende
            while winkel != start:
                if winkel == 0:
                    winkel = 360
                winkel = (winkel - 1) % 360
                wert = self.distances[winkel] - self.mySize[winkel]
                if wert < 0:
                    wert= 0
                    
                if wert > 0 and wert < minDist_wert:
                    minDist_winkel = winkel
                    minDist_wert = wert
            
        return minDist_winkel, minDist_wert
    
        
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
        
        

    def main(self):
        try:
            while True:
                #Lese Lidar Daten
                for i in range(360):
                    wert = self.getDistance(i)
                    print(f"Winkel {i} Entfernung {wert}")
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nStopping Lidar Data")
        finally:
            close()
        
    
if __name__ == "__main__":
    print("Start Lidar Data")
    ld = LIDAR_DATA()
    ld.send_start_signal()
    #ld.main()
    try:
        while True:
            #winkel,wert = ld.getMin_Dist_Bereich_RR(270,0,False)
            winkel,wert = ld.getMin_Dist_Bereich(270,0,False)
            print(f"Winkel {winkel} Entfernung {wert}")
            time.sleep(0.1)
        
    except KeyboardInterrupt:
            print("\nStopping Lidar Data")
            ld.send_stop_signal()
    finally:
            ld.close()                                                                                                                                    
    
    
