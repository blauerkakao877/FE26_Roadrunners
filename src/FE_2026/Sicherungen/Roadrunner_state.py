class State:
    
    def __init__(self):
         
        # Presets / Modus
        self.slow = False
        self.medium = False
        self.fast = False
        self.mode = "obstacle"
        
        # Rennen
        self.Rennen_laeuft = False
        
        # Linien
        self.linien_counter = 0
        self.geradeaus = 0
        self.linie_imbild = False
        self.current_direction = "n"
        
        # Zeitsteuerung Linien (werden aus Presets gesetzt!)
        self.linie_zeit = 0.0
        
        self.linie_warten = 2.3
        self.linie_warten_LG = 2.3
        self.linie_warten_LR = 3.0
        self.linie_warten_RG = 3.0
        self.linie_warten_RR = 2.3
        
        self.linie_zaehlen_first = 0.45
        self.linie_zaehlen = 0.45
        self.linie_zaehlen_LG = 0.35
        self.linie_zaehlen_LR = 0.45
        self.linie_zaehlen_RG = 0.45
        self.linie_zaehlen_RR = 0.35
        
        # Zustände Linien
        self.blaue_linie = False
        self.orange_linie = False
        
        # Gyro
        self.winkel = 0.0
        self.gesamt = 0.0
        self.k = 0.6
        self.drift_kor = 0.2
        
        # Ende
        self.stop_time = 0.0
        self.stop_time_LG = 3.0
        self.stop_time_LR = 4.0
        self.stop_time_RG = 4.0
        self.stop_time_RR = 3.0
        
        # Ausfahrt
        self.ausfahrt_L = False
        self.ausfahrt_R = False
        
        # Hindernisse
        self.farbe = "n"
        self.hindernis = False
        self.hindernis_sperre = False
        self.h_zeit = 0.0
        self.h_warten = 0.5 #0.7
        self.kh = 0.4 #0.3
        self.letzte_farbe = "N"
        self.h_avoid_until = 0.0
        self.h_avoid_active = False
        
        #Lidar
        self.LDL = 0
        self.LDR = 0
        self.LDV = 0
        
        #Parken
        self.eingeparkt = False