# race_state.py
# Obstaclerace_kamera_inter_paral.py in einem Objekt.

import time


class RaceState:
    """Gesamter Laufzustand des Obstacle-Race-Roboters."""

    def __init__(self):
        # --------------------------------------------------
        # Geschwindigkeitsprofile / Auswahl
        # --------------------------------------------------
        self.mid2: bool = True
        self.slow1: bool = False

        # --- aktuelles aktives Profil (Standard) ----------
        self.speed: float = 0.48
        self.startspeed: float = 0.47

        self.linien_warten: float = 2.4
        self.linien_zaehlen: float = 0.07
        self.linien_zaehlen_LG: float = 0.10
        self.linien_zaehlen_RG: float = 0.01
        self.linien_zaehlen_LR: float = 0.10
        self.linien_zaehlen_RR: float = 0.01

        self.stop_time_LG: float = 2.0
        self.stop_time_RG: float = 3.1
        self.stop_time_LR: float = 3.3
        self.stop_time_RR: float = 2.3

        self.h_warten: float = 0.69

        # --- Profil "mid2" --------------------------------
        self.speed2: float = 0.48
        self.startspeed2: float = 0.47
        self.linien_warten2: float = 2.4
        self.linien_zaehlen2: float = 0.07
        self.linien_zaehlen_LG2: float = 0.10
        self.linien_zaehlen_RG2: float = 0.01
        self.linien_zaehlen_LR2: float = 0.10
        self.linien_zaehlen_RR2: float = 0.01
        self.stop_time_LG2: float = 2.0
        self.stop_time_RG2: float = 3.1
        self.stop_time_LR2: float = 3.3
        self.stop_time_RR2: float = 2.3
        self.h_warten2: float = 0.69

        # --- Profil "slow1" -------------------------------
        self.speed1: float = 0.32
        self.startspeed1: float = 0.35
        self.linien_warten1: float = 2.8
        self.linien_zaehlen1: float = 0.10
        self.linien_zaehlen_LG1: float = 0.15
        self.linien_zaehlen_RG1: float = 0.09
        self.linien_zaehlen_LR1: float = 0.15
        self.linien_zaehlen_RR1: float = 0.06
        self.stop_time_LG1: float = 2.6
        self.stop_time_RG1: float = 3.9
        self.stop_time_LR1: float = 3.9
        self.stop_time_RR1: float = 2.9
        self.h_warten1: float = 0.75

        # --------------------------------------------------
        # Lenk- / Regel-Parameter
        # --------------------------------------------------
        self.steerangle: float = 95.0
        self.k: float = 0.6         # Geradeaus-Regler
        self.kh: float = 0.35       # Hindernis-Regler
        self.Seitehalten: int = 0
        self.servmitte: float = 95.0

        # --------------------------------------------------
        # Button / IO
        # --------------------------------------------------
        self.BUTTON_PIN: int = 16

        # --------------------------------------------------
        # Orientierung / Gyro
        # --------------------------------------------------
        self.geradeaus: float = 0.0
        self.gesamt: float = 0.0
        self.current_direction: str = "n"  # "l", "r" oder "n"

        # --------------------------------------------------
        # Linienerkennung / Linien-Status
        # --------------------------------------------------
        self.linie: bool = False
        self.linien_zeit: float = 0.0
        self.linien_counter: int = 0

        self.blaue_linie: bool = False
        self.orange_linie: bool = False
        self.linie_imbild: bool = False
        self.linie_korrigiert: bool = False

        # --------------------------------------------------
        # Farberkennung / Hindernisse
        # --------------------------------------------------
        self.x: int = 0
        self.y: int = 0
        self.s: int = 0
        self.farbe: str = "N"
        self.letzte_farbe: str = "N"

        self.links: bool = False
        self.rechts: bool = False
        self.hellL: float = 0.0
        self.hellR: float = 0.0

        self.linksMag: bool = False
        self.rechtsMag: bool = False
        self.hellLMag: float = 0.0
        self.hellRMag: float = 0.0

        self.abstand: float = 0.0
        self.hindernis: bool = False
        self.h_zeit: float = 0.0
        self.hindernis_sperre: bool = False

        # --------------------------------------------------
        # U-Turn / Speziallogik
        # --------------------------------------------------
        self.NowUturn: bool = False
        self.Uturn: bool = False
        self.Uturndetected: bool = False
        self.Uturndone: bool = False

        # --------------------------------------------------
        # Rennstatus & Zeitsteuerung
        # --------------------------------------------------
        self.Rennen_laeuft: bool = True

        self.stop_time: float = time.time() + 18000.0
        self.reduced: bool = False

        self.park_runde: bool = False
        self.park_stop_time: float = time.time() + 18000.0

        # --------------------------------------------------
        # Parken / Ausparken
        # --------------------------------------------------
        self.start_parkbande: bool = False
        self.parken: bool = False
        self.parken_aus: bool = True
        self.Ausparken: bool = True
        self.parken_paral: bool = True

        # --------------------------------------------------
        # Kamera / Bildgröße
        # --------------------------------------------------
        self.hoehe: int = 210
        self.breite: int = 320

        # --------------------------------------------------
        # Proximity / Alarm-Flags
        # --------------------------------------------------
        self.alarm_VR: bool = False
        self.alarm_HR: bool = False
        self.alarm_VL: bool = False
        self.alarm_HL: bool = False

        # --------------------------------------------------
        # Sonstiges / Steering-Tuning
        # --------------------------------------------------
        self.steeringpoint: int = 60

        # --------------------------------------------------
        # Testflags
        # --------------------------------------------------
        self.test: bool = False
        self.test_L: bool = False
        self.test_R: bool = False
        self.test_L_park: bool = False
        self.test_R_park: bool = False

        # Crash-Timer
        self.crash_timer_set: bool = False
        self.crash_timer: float | None = None

    def use_mid_profile(self):
        self.mid2 = True
        self.slow1 = False
        self.speed = self.speed2
        self.startspeed = self.startspeed2
        self.linien_warten = self.linien_warten2
        self.linien_zaehlen = self.linien_zaehlen2
        self.linien_zaehlen_LG = self.linien_zaehlen_LG2
        self.linien_zaehlen_RG = self.linien_zaehlen_RG2
        self.linien_zaehlen_LR = self.linien_zaehlen_LR2
        self.linien_zaehlen_RR = self.linien_zaehlen_RR2
        self.stop_time_LG = self.stop_time_LG2
        self.stop_time_RG = self.stop_time_RG2
        self.stop_time_LR = self.stop_time_LR2
        self.stop_time_RR = self.stop_time_RR2
        self.h_warten = self.h_warten2

    def use_slow_profile(self):
        self.mid2 = False
        self.slow1 = True
        self.speed = self.speed1
        self.startspeed = self.startspeed1
        self.linien_warten = self.linien_warten1
        self.linien_zaehlen = self.linien_zaehlen1
        self.linien_zaehlen_LG = self.linien_zaehlen_LG1
        self.linien_zaehlen_RG = self.linien_zaehlen_RG1
        self.linien_zaehlen_LR = self.linien_zaehlen_LR1
        self.linien_zaehlen_RR = self.linien_zaehlen_RR1
        self.stop_time_LG = self.stop_time_LG1
        self.stop_time_RG = self.stop_time_RG1
        self.stop_time_LR = self.stop_time_LR1
        self.stop_time_RR = self.stop_time_RR1
        self.h_warten = self.h_warten1