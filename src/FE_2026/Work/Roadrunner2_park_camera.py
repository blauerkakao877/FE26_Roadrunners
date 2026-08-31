import DrivingBase as d
import Led as l
import Cam_moduls_contours as c
import Gyro as g
import lidar_data as ld
import Write_Logfile as wl
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from Color_defs import *
from Roadrunner_state import State

import time
import math
import cv2


class Roadrunner:

    def __init__(self):
        self.state = State()
        self.state.Rennen_laeuft = False

        self.speed = 0.3

        #TEST
        self.TEST = False
        
        # Presets
        self.state.slow = False
        self.state.medium = True
        self.state.fast = False

        self.D = d.DrivingBase()
        self.L = l.Led()
        self.C = c.CameraModules(self.state)
        self.C.init("obstacle")
        self.G = g.Gyro()
        self.LD = ld.LIDAR_DATA()
        self.WL = wl.Logwriter()

    # -------------------- START --------------------

    def start_sequence(self):
        self.LDV = 50
        self.LDL = 0
        self.LDR = 0
        self.ausfahrt_L = False
        self.ausfahrt_R = False
        self.WL.open_Log(self)
        self.G.start()

        if self.state.slow:
            self.L.waiting_S()
        elif self.state.medium:
            self.L.waiting_M()
        elif self.state.fast:
            self.L.waiting_F()
        else:
            self.L.waiting()

        self.D.wait_for_button_press()
        time.sleep(0.5)
        self.LD.send_start_signal()
        time.sleep(0.2)

        # Aufnahme starten
        self.C.enable_recording(True)
        #self.C.enable_recording(False)

        #hsv_full, hsv_main, bgr_main, hsv_line, bgr_line = self.C.get_image()
        #ausfahrt_L, ausfahrt_R = self.C.finde_ausfahrt(hsv_main)
        
        #Lidar Messung durchführen, vorne, links, rechts
        _, self.LDV = self.LD.getMin_Dist_Bereich_RR(353, 7)
        _, self.LDL = self.LD.getMin_Dist_Bereich_RR(260, 280)
        _, self.LDR = self.LD.getMin_Dist_Bereich_RR(80, 100)
        
        if self.LDV < 200 and self.LDV > 0:
            if self.LDL < 400:
                self.ausfahrt_R = True
            elif self.LDR < 400:
                self.ausfahrt_L = True

        if self.ausfahrt_L:
            self.state.mode = "obstacle"
            self.state.current_direction = "l"
            self.WL.write_Log("Ausfahrt: Links")
            
            self.state.slow = True 
            self.state.ausfahrt_L = True
            
            self.L.all_off()
            self.L.on(0, MAGENTA)
            self.L.on(3, MAGENTA)
            #print("Ausfahrt links")
        elif self.ausfahrt_R:
            self.state.mode = "obstacle"
            self.state.current_direction = "r"
            self.WL.write_Log("Ausfahrt: Rechts")
            
            self.state.slow = True
            self.state.ausfahrt_R = True
            
            self.L.all_off()
            self.L.on(1, MAGENTA)
            self.L.on(2, MAGENTA)
            #print("Ausfahrt rechts")
        else:
            self.state.mode = "open"
            self.state.current_direction = "n"
            
            self.state.fast = True
            
            self.L.all_W()
            print("Openrace")

        self.WL.write_Log("Mode: "+str(self.state.mode))
        self.D.gerade()
        self.state.Rennen_laeuft = True
        self.state.stop_time = time.time() + 180000.0
        self.stop_time_set = False

    def stop_sequence(self):
        self.state.Rennen_laeuft = False
        self.D.stop()
        self.L.stop()
        self.C.enable_recording(False)
        self.LD.send_stop_signal()
        self.WL.write_Log("stop_sequence")
        self.WL.close_Log()
        
    def safe_run(self):
        try:
            self.main_launcher()

        except Exception as e:
            print("Fehlermeldung:", e)
            self.D.stop()
            self.D.gerade()
            self.L.all_on(RED)
            
            self.C.enable_recording(False)
            self.LD.send_stop_signal()

            self.WL.write_Log("==!CRASH!==")
            self.WL.write_Log(str(e))
            self.WL.close_Log()

            print("!EXCEPTION STOPPED SYSTEM!")
         
    # -------------------- Ausparken --------------------
        
    def ausparken(self):

        self.state.geradeaus = 0
        self.state.gesamt = 0
        self.state.winkel, self.state.gesamt = self.G.WinkelMessen()

        # ================= LINKS =================
        if self.state.ausfahrt_L:

            # -------- ZUG 1: Vor + links --------
            self.D.steer(-30)
            self.D.vor(0.12)

            while self.state.gesamt > self.state.geradeaus -20:
                self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
                time.sleep(0.01)

            self.D.stop()
            time.sleep(0.15)

            # -------- ZUG 2: Rück + rechts --------
            self.D.steer(20)
            self.D.ruck(0.08)

            while self.state.gesamt > self.state.geradeaus -30:
                self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
                time.sleep(0.01)

            self.D.stop()
            time.sleep(0.15)

            # -------- ZUG 3: Vor + links --------
            self.D.steer(-30)
            self.D.vor(0.12)

            while self.state.gesamt > self.state.geradeaus -55:
                self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
                time.sleep(0.01)

            self.D.stop()
            time.sleep(0.1)

            # -------- Gerade ausrichten --------
            self.D.gerade()
            self.D.vor(0.15)
            time.sleep(0.1)
            
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()

        # ================= RECHTS =================
        elif self.state.ausfahrt_R:

            # -------- ZUG 1: Vor + rechts --------
            self.D.steer(30)
            self.D.vor(0.12)

            while self.state.gesamt < self.state.geradeaus +20:
                self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
                time.sleep(0.01)

            self.D.stop()
            time.sleep(0.15)

            # -------- ZUG 2: Rück + links --------
            self.D.steer(-20)
            self.D.ruck(0.08)

            while self.state.gesamt < self.state.geradeaus +30:
                self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
                time.sleep(0.01)

            self.D.stop()
            time.sleep(0.15)

            # -------- ZUG 3: Vor + rechts --------
            self.D.steer(30)
            self.D.vor(0.12)

            while self.state.gesamt < self.state.geradeaus +55:
                self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
                time.sleep(0.01)

            self.D.stop()
            time.sleep(0.1)

            # -------- Gerade ausrichten --------
            self.D.gerade()
            self.D.vor(0.15)
            time.sleep(0.1)
            
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()

    # -------------------- LINIEN --------------------

    def linien_suchen_obstacle(self, hsv_line):
        
        if self.state.current_direction == "l":
            if self.state.letzte_farbe == "G":
                self.state.linie_zaehlen = self.state.linie_zaehlen_LG
                self.state.linie_warten = self.state.linie_warten_LG
            elif self.state.letzte_farbe == "R":
                self.state.linie_zaehlen = self.state.linie_zaehlen_LR
                self.state.linie_warten = self.state.linie_warten_LR

        elif self.state.current_direction == "r":
            if self.state.letzte_farbe == "G":
                self.state.linie_zaehlen = self.state.linie_zaehlen_RG
                self.state.linie_warten = self.state.linie_warten_RG
            elif self.state.letzte_farbe == "R":
                self.state.linie_zaehlen = self.state.linie_zaehlen_RR
                self.state.linie_warten = self.state.linie_warten_RR

        if self.state.linien_counter >= 12 and not self.stop_time_set:
            self.stop_time_set = True
            self.state.stop_time = time.time() + 3.0

            if self.state.letzte_farbe == "G":
                if self.state.current_direction == "l":
                    self.state.stop_time = time.time() + self.state.stop_time_LG
                elif self.state.current_direction == "r":
                    self.state.stop_time = time.time() + self.state.stop_time_RG

            elif self.state.letzte_farbe == "R":
                if self.state.current_direction == "l":
                    self.state.stop_time = time.time() + self.state.stop_time_LR
                elif self.state.current_direction == "r":
                    self.state.stop_time = time.time() + self.state.stop_time_RR


        # ================= LINKS =================
        if self.state.current_direction == "l":

            if ((time.time() - self.state.linie_zeit) > self.state.linie_warten) and not self.state.linie_imbild:
                linie = self.C.finde_blau(hsv_line)
                if linie:
                    self.state.linie_zeit = time.time()
                    self.state.blaue_linie = True
                    self.state.linie_imbild = True
                    self.L.on(1, BLUE)

            else:
                if self.state.blaue_linie and (time.time() - self.state.linie_zeit > self.state.linie_zaehlen):

                    self.state.linien_counter += 1
                    self.L.on(1, BLUE)

                    self.state.geradeaus -= 90

                    # ---- WICHTIG: sofortige Sperre gegen Doppelzählung ----
                    self.state.blaue_linie = False
                    self.state.linie_imbild = False
                    self.state.linie_zeit = time.time()

                    self.L.off(1)


        # ================= RECHTS =================
        elif self.state.current_direction == "r":

            if ((time.time() - self.state.linie_zeit) > self.state.linie_warten) and not self.state.linie_imbild:
                linie = self.C.finde_orange(hsv_line)
                if linie:
                    self.state.linie_zeit = time.time()
                    self.state.orange_linie = True
                    self.state.linie_imbild = True
                    self.L.on(1, ORANGE)

            else:
                if self.state.orange_linie and (time.time() - self.state.linie_zeit > self.state.linie_zaehlen):

                    self.state.linien_counter += 1
                    self.L.on(1, ORANGE)

                    self.state.geradeaus += 90

                    # ---- WICHTIG: Sperre ----
                    self.state.orange_linie = False
                    self.state.linie_imbild = False
                    self.state.linie_zeit = time.time()
                    
                    self.WL.write_Log("linie_warten: "+str(self.state.linie_warten))
                    self.WL.write_Log("linie_zaehlen: "+str(self.state.linie_zaehlen))

                    self.L.off(1)


        # ================= INITIAL (keine Richtung bekannt) =================
        else:
            self.state.blaue_linie = self.C.finde_blau(hsv_line)
            self.state.orange_linie = self.C.finde_orange(hsv_line)

            if self.state.blaue_linie:
                self.L.on(1, BLUE)
                self.state.current_direction = "l"

                if self.state.letzte_farbe == "G":
                    self.state.linie_zaehlen = self.state.linie_zaehlen_LG
                    self.state.linie_warten = self.state.linie_warten_LG
                elif self.state.letzte_farbe == "R":
                    self.state.linie_zaehlen = self.state.linie_zaehlen_LR
                    self.state.linie_warten = self.state.linie_warten_LR

                self.state.linie_zeit = time.time()

            elif self.state.orange_linie:
                self.L.on(1, ORANGE)
                self.state.current_direction = "r"

                if self.state.letzte_farbe == "G":
                    self.state.linie_zaehlen = self.state.linie_zaehlen_RG
                    self.state.linie_warten = self.state.linie_warten_RG
                elif self.state.letzte_farbe == "R":
                    self.state.linie_zaehlen = self.state.linie_zaehlen_RR
                    self.state.linie_warten = self.state.linie_warten_RR

                self.state.linie_zeit = time.time()


    def linien_suchen_open(self, hsv_line):
        if self.state.current_direction == "l":
            if (time.time() - self.state.linie_zeit) > self.state.linie_warten:
                if self.C.finde_blau(hsv_line):
                    self.state.linie_zeit = time.time()
                    self.state.blaue_linie = True
                    self.L.B()
                    if self.state.linien_counter == 12:
                        self.state.Rennen_laeuft = False
            else:
                zeit_limit = self.state.linie_zaehlen if self.state.linien_counter > 0 else self.state.linie_zaehlen_first

                if self.state.blaue_linie and (time.time() - self.state.linie_zeit > zeit_limit):
                    self.state.linien_counter += 1
                    self.state.geradeaus = self.state.linien_counter * (-90)
                    self.state.blaue_linie = False
                    self.L.all_off()

                    self.draw_line_until = time.time() + 0.5

        elif self.state.current_direction == "r":
            if (time.time() - self.state.linie_zeit) > self.state.linie_warten:
                
                if self.C.finde_orange(hsv_line):
                    self.state.linie_zeit = time.time()
                    self.state.orange_linie = True
                    self.L.O()
                    if self.state.linien_counter == 12:
                        self.state.Rennen_laeuft = False
            else:
                zeit_limit = self.state.linie_zaehlen if self.state.linien_counter > 0 else self.state.linie_zaehlen_first

                if self.state.orange_linie and (time.time() - self.state.linie_zeit > zeit_limit):
                    self.state.linien_counter += 1
                    self.state.geradeaus = self.state.linien_counter * 90
                    self.state.orange_linie = False
                    self.L.all_off()

                    self.draw_line_until = time.time() + 0.5

        else:
            if self.C.finde_blau(hsv_line):
                self.state.current_direction = "l"
                self.WL.write_Log("Richtung: Links")
                self.state.linie_zeit = time.time()
                self.state.blaue_linie = True

            elif self.C.finde_orange(hsv_line):
                self.state.current_direction = "r"
                self.WL.write_Log("Richtung: Rechts")
                self.state.linie_zeit = time.time()
                self.state.orange_linie = True
            
    # -------------------- GERADEAUS LENKEN --------------------        
    def geradeaus_lenken(self):        
        self.state.winkel, raw_gesamt = self.G.WinkelMessen()
        self.state.gesamt = raw_gesamt + self.state.drift_kor * self.state.linien_counter
        
        offset = self.state.k * (self.state.geradeaus - self.state.gesamt)
        offset = max(-30, min(30, offset))
        
        if offset < 0 and self.state.LDL < 120:
            offset = 0
            self.L.on(2, PINK)
            self.pink_last = time.time()
            self.WL.write_Log("Lidar verhindert lenken nach links/geradeaus")
            
            
        if offset > 0 and self.state.LDR < 120:
            offset = 0
            self.L.on(2, PINK)
            self.pink_last = time.time()
            self.WL.write_Log("Lidar verhindert lenken nach rechts/geradeaus")
        
        self.D.steer(offset)
        
    # -------------------- MESSEN -------------------- 
    def messen(self): 
        #--Winkel von Gyro auslesen--
        self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
        #--Kamerabilder abholen--
        self.hsv_full, self.hsv_main, self.bgr_main, self.hsv_line, self.bgr_line = self.C.get_image()
        #--Wände finden + auswerten--
        self.links, self.rechts, self.hellL, self.hellR = self.C.waende(self.bgr_main)
        #--Magenta Wände finden + auswerten--
        self.linksMag, self.rechtsMag, self.hellLMag, self.hellRMag = self.C.waende_Magenta(self.hsv_main)
        #--Korrekturen für falsche Magenta Wände--
        if self.state.current_direction == "r":
            if self.rechtsMag:
                self.rechtsMag = False #korektur, weil magenta kann nicht an der rechten wand stehen
        elif self.state.current_direction == "l":
            if self.linksMag:
                self.linksMag = False #korektur, weil magenta kann nicht an der linken wand stehen
        else:
            self.rechtsMag = False
            self.linksMag = False
        #--Hindernisse finden + auswerten--
        self.x, self.y, self.s, self.state.farbe = self.C.finde_hindernisse(self.hsv_main)
        self.center = 160
        #--Lidar auslesen--
        _, self.state.LDR = self.LD.getMin_Dist_Bereich_RR(0, 90)
        _, self.state.LDL = self.LD.getMin_Dist_Bereich_RR(270, 0)
        _, self.state.LDV = self.LD.getMin_Dist_Bereich_RR(353, 7)
            
    # -------------------- PARKEN -------------------- 
    def einparken_l(self):
        self.state.eingeparkt = False
        self.linksMag = False
        self.rechtsMag = False
        self.hellLMag = 0
        self.hellRMag = 0
        self.ziel_winkel = 0.0
        self.weiterfahren = 0
        
        
        self.WL.write_Log("starte einparken_l ")
        self.D.stop()
        self.D.gerade()
        time.sleep(0.3)
        if self.state.letzte_farbe == "G":
            self.L.all_on(GREEN)
            self.D.ruck(0.15)
            self.D.nach_links()
            time.sleep(0.7)
            self.D.stop()
            self.D.nach_rechts()
            time.sleep(0.1)
            self.D.vor(0.2)
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
            while self.state.gesamt < -1080:   #korrekturzug
                time.sleep(0.1)
                self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
            self.D.stop()
            time.sleep(0.1)
        self.L.all_off()
        self.D.gerade()
        self.D.vor(0.2)
        self.state.geradeaus = -1080
        weiterfahren = time.time() + 1.0 #fahrt in die Kurve vor dem lenken
        while time.time() < weiterfahren:
            self.geradeaus_lenken()
        self.D.nach_rechts()
        self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
        #self.WL.write_Log(str(gesamt))
        while self.state.gesamt < -990:
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
            time.sleep(0.1)
        self.D.stop()
        self.D.gerade()
        time.sleep(0.1)
        self.D.vor(0.2)
        time.sleep(1.5)
        self.D.vor(0.4)
        time.sleep(0.1)
        self.D.stop()
        #--------------steht an der wand----------------    
        self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
        self.WL.write_Log("Winkel an Wand")
        self.WL.write_Log(str(self.state.winkel))
        self.WL.write_Log(str(self.state.gesamt))
        
        self.geradeaus = self.state.gesamt +90
        self.WL.write_Log("geradeaus: "+str(self.geradeaus))
        time.sleep(0.3)
        self.D.ruck(0.15)
        time.sleep(0.2)
        while self.state.LDV < 50:
            time.sleep(0.05)
            _, self.state.LDV = self.LD.getMin_Dist_Bereich_RR(353, 7)
        self.D.stop()
        time.sleep(0.1)
        self.D.ruck(0.15)
        self.D.nach_links()
        while self.state.gesamt < self.geradeaus +10:
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
            time.sleep(0.1)
        self.D.stop()
        self.D.gerade()
        time.sleep(0.3)
        self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
        self.WL.write_Log("Winkel vor fahren zum Parkplatz")
        self.WL.write_Log("winkel: "+str(self.state.winkel))
        self.WL.write_Log("gesamt: "+str(self.state.gesamt))
        
        self.state.current_direction = "r"
        
        hellRMag = 0
        _, self.b_hsv_main, _, _, _ = self.C.get_image_back()
        _, _, _, hellRMag = self.C.waende_Magenta(self.b_hsv_main)
        #self.WL.write_Log(str(hellRMag))
        self.D.vor(0.2)
        while hellRMag < 500:
            _, self.b_hsv_main, _, _, _ = self.C.get_image_back()
            _, _, _, hellRMag = self.C.waende_Magenta(self.b_hsv_main)
            #self.WL.write_Log(str(hellRMag))
        self.L.all_on(MAGENTA)
        self.D.stop()
        time.sleep(0.1)
        self.D.gerade()
        #self.D.vor(0.3)
        #time.sleep(0.2)
        #self.D.stop()
        #-----------fahre in parkbox rein--------
        self.L.all_off()
        self.D.nach_links()
        self.D.ruck(0.15)
            
        while self.state.gesamt < self.geradeaus +70:
            time.sleep(0.1)
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
        self.D.stop()
        self.D.gerade()
        time.sleep(0.1)
        
        #wiggel tief in box in linke Ecke aus Kamerasicht
        self.WL.write_Log("Wiggel in Box")
        _, self.b_hsv_main, _, _, _ = self.C.get_image_back()
        _, _, hellLMag, hellRMag = self.C.waende_Magenta(self.b_hsv_main)
        self.WL.write_Log("hellLMag: "+str(hellLMag)+" hellRMag: "+str(hellRMag))
        #alarm_HL, alarm_VL, alarm_HR, alarm_VR, alarm_HM = P.prox_alarm()
        self.D.ruck(0.35)
        
        weiterfahren = time.time() + 3.0
        #while (time.time() < weiterfahren) and (alarm_HR == False) and (alarm_HL == False) and (alarm_HM == False):
        while (time.time() < weiterfahren):

            if (hellLMag > hellRMag) and (hellLMag > 500):
                self.D.nach_links()
            elif (hellRMag > hellLMag) or (hellLMag < 500):
                self.D.nach_rechts()
            else:
                self.D.gerade()
                
            _, self.b_hsv_main, _, _, _ = self.C.get_image_back()
            _, _, hellLMag, hellRMag = self.C.waende_Magenta(self.b_hsv_main)
            #alarm_HL, alarm_VL, alarm_HR, alarm_VR, alarm_HM = P.prox_alarm()
            self.WL.write_Log("hellLMag: "+str(hellLMag)+" hellRMag: "+str(hellRMag))
            
        self.D.stop()
        ########################
        #if parken_paral:
        #    einparken_parallel()
        ########################  
    
    def einparken_r(self):
        self.state.eingeparkt = False
        self.linksMag = False
        self.rechtsMag = False
        self.hellLMag = 0
        self.hellRMag = 0
        
        self.WL.write_Log("starte einparken_r ")
        self.WL.write_Log("Geradeaus vor Park-Sequenz_r: "+str(self.state.geradeaus))
        self.D.stop()
        self.L.all_on(WHITE)
        time.sleep(0.3)
        self.D.vor(0.2)
        self.D.nach_links()
        while self.state.gesamt > self.state.geradeaus -85:
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
            time.sleep(0.1)
        self.D.stop()
        self.D.gerade()
        time.sleep(0.1)
        self.D.vor(0.2)
        while self.state.LDV > 50:
            time.sleep(0.1)
            _, self.state.LDV = self.LD.getMin_Dist_Bereich_RR(353, 7)
        time.sleep(1.0)
        self.D.vor(0.5)
        time.sleep(0.2)
        self.D.stop()
        
        #steht an der wand
        self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
        self.WL.write_Log("Winkel an der Wand")
        self.WL.write_Log("winkel: "+str(self.state.winkel))
        self.WL.write_Log("gesamt: "+str(self.state.gesamt))
        self.WL.write_Log("Geradeaus an der Wand: "+str(self.state.geradeaus))
        
        self.state.geradeaus = self.state.gesamt -90
        time.sleep(0.3)
        self.D.ruck(0.2)
        time.sleep(0.2)
        while self.state.LDV < 50:
            time.sleep(0.1)
            _, self.state.LDV = self.LD.getMin_Dist_Bereich_RR(353, 7)
        self.D.stop()
        time.sleep(0.1)
        self.D.ruck(0.2)
        self.D.nach_rechts()
        
        self.state.geradeaus = 900
        while self.state.gesamt > self.state.geradeaus:
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
            time.sleep(0.1)
        self.D.stop()
        self.D.gerade()
        time.sleep(0.1)
        self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
        self.WL.write_Log("Winkel vor dem fahren zum Parkplatz")
        self.WL.write_Log("winkel: "+str(self.state.winkel))
        self.WL.write_Log("gesamt: "+str(self.state.gesamt))
        self.WL.write_Log("Geradeaus vor dem fahren zum Parkplatz: "+str(self.state.geradeaus))
        self.state.current_direction = "l"
        
        self.hellRMag = 0
        _, self.b_hsv_main, _, _, _ = self.C.get_image_back()
        _, _, self.hellLMag, _ = self.C.waende_Magenta(self.b_hsv_main)
        self.L.all_on(WHITE)
        self.D.vor(0.15)
        while self.hellLMag < 1500:
            self.geradeaus_lenken()
            _, self.b_hsv_main, _, _, _ = self.C.get_image_back()
            _, _, self.hellLMag, _ = self.C.waende_Magenta(self.b_hsv_main)
            self.WL.write_Log("hellLMag bei Parksuche: "+str(self.hellLMag))
            
            _, self.state.LDL = self.LD.getMin_Dist_Bereich_RR(270, 359)
            _, self.state.LDR = self.LD.getMin_Dist_Bereich_RR(1, 90)
            if self.state. LDL < 10 and self.state.LDL > 0:
                self.D.nach_rechts()
            elif self.state. LDR < 10 and self.state.LDR > 0:
                self.D.nach_links()
        time.sleep(0.1)
        self.L.all_on(MAGENTA)
        self.D.stop()
        self.D.gerade()
        time.sleep(0.1)
        #fahre in parkbox rein
        self.L.all_off()
        self.D.nach_rechts()
        self.D.ruck(0.2)
            
        while self.state.gesamt > self.state.geradeaus -70:
            self.state.winkel, self.state.gesamt = self.G.WinkelMessen()
            time.sleep(0.1)
        self.D.stop()
        self.D.gerade()
        time.sleep(0.1)
        self.D.ruck(0.2)
        #alarm_HL, alarm_VL, alarm_HR, alarm_VR, alarm_HM = P.prox_alarm()
        weiterfahren = time.time() + 3.0
        while (time.time() < weiterfahren):
            _, self.b_hsv_main, _, _, _ = self.C.get_image_back()
            _, _, hellLMag, hellRMag = self.C.waende_Magenta(self.b_hsv_main)
            
            if (hellLMag > hellRMag) and (hellLMag > 500):
                self.D.nach_links()
            elif (hellRMag > hellLMag) or (hellLMag < 500):
                self.D.nach_rechts()
            else:
                self.D.gerade()
            #alarm_HL, alarm_VL, alarm_HR, alarm_VR, alarm_HM = P.prox_alarm()
            #self.WL.write_Log("hellLMag: "+str(hellLMag)+" hellRMag: "+str(hellRMag))
            time.sleep(0.05)
        self.D.stop()
        self.WL.write_Log("gesamt im Parkplatz: "+str(self.state.gesamt))
        self.WL.write_Log("Geradeaus im Parkplatz: "+str(self.state.geradeaus))
        time.sleep(0.1)
        self.state.geradeaus = 820
        self.geradeaus_lenken()
        self.D.vor(0.15)
        time.sleep(0.5)
        self.D.stop()
        self.D.gerade()
        time.sleep(0.1)
        self.D.ruck(0.15)
        time.sleep(1.0)
        self.D.stop()
        self.L.all_on(GREEN)
        
        ########################
        #if parken_paral:
        #    einparken_parallel()
        ########################
        
    def einparken(self):
        self.state.eingeparkt = False
        self.linksMag = False
        self.echtsMag = False
        self.hellLMag = 0
        self.hellRMag = 0
        
        self.D.stop()
        #self.L.led_R21()
        #self.L.led_R1()
        time.sleep(0.3)

        if self.state.current_direction == "l":
            self.einparken_l()
        elif self.state.current_direction == "r":
            self.einparken_r()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-MAIN-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    def main_launcher(self):
        self.D.stop()
        self.L.booting()
        self.start_sequence()

        if self.state.mode == "open":
            self.main_open()
        elif self.state.mode == "obstacle":
            self.main_obstacle()

#//////////////////////////////////////////////////////////////////////////

    def main_open(self):

        # Initialwerte
        self.state.linien_counter = 0
        self.state.geradeaus = 0
        self.state.linie_zeit = 0
        self.state.blaue_linie = False
        self.state.orange_linie = False
        self.state.linie_zaehlen = 0
        self.state.stop_time = 0.0
        self.draw_line_until = 0

        presets = {
            "slow": {
                "endstop": 3.0,
                "run_speed": 0.4,
                "linie_warten": 2.5,
                "linie_zaehlen": 0.5,
                "linie_zaehlen_first": 0.7
            },
            "medium": {
                "endstop": 2.5,
                "run_speed": 0.55,
                "linie_warten": 2.0,
                "linie_zaehlen": 0.35,
                "linie_zaehlen_first": 0.55
            },
            "fast": {
                "endstop": 1.7,
                "run_speed": 0.7,#0.64
                "linie_warten": 1.5,
                "linie_zaehlen": 0.4,#0.45
                "linie_zaehlen_first": 0.6
            }
        }

        if self.state.slow:
            preset = presets["slow"]
        elif self.state.medium:
            preset = presets["medium"]
        elif self.state.fast:
            preset = presets["fast"]
        else:
            preset = presets["slow"]

        endstop = preset["endstop"]
        run_speed = preset["run_speed"]
        self.state.linie_warten = preset["linie_warten"]
        self.state.linie_zaehlen = preset["linie_zaehlen"]
        self.state.linie_zaehlen_first = preset["linie_zaehlen_first"]

        time.sleep(0.2)
        self.D.vor(self.speed)

        while self.state.Rennen_laeuft and not self.D.button_pressed():

            try:
                hsv_full, hsv_main, bgr_main, hsv_line, bgr_line = self.C.get_image()
            except Exception as e:
                print("Kamera-Fehler:", e)
                hsv_line = None
                bgr_main = None

            links = False
            rechts = False
            if bgr_main is not None:
                links, rechts, hellL, hellR = self.C.waende(bgr_main)

            if hsv_line is not None:
                self.linien_suchen_open(hsv_line)

            self.geradeaus_lenken()

            if links and not rechts:
                self.D.steer(25)
            elif rechts and not links:
                self.D.steer(-25)
            elif links and rechts:
                if self.state.geradeaus != 0:
                    if self.G.WinkelMessen()[1] >= self.state.geradeaus:
                        self.D.steer(-30)
                    else:
                        self.D.steer(30)

            if self.state.linien_counter > 0:
                self.D.vor(run_speed)

            # ---------------- VIDEO ----------------
            if bgr_main is not None:
                record_img = bgr_main.copy()

                if time.time() < self.draw_line_until:
                    if self.state.current_direction == "l":
                        cv2.line(record_img, (0, 150), (320, 150), (255, 0, 0), 5)
                    elif self.state.current_direction == "r":
                        cv2.line(record_img, (0, 150), (320, 150), (0, 140, 255), 5)

                if links:
                    cv2.line(record_img, (10, 0), (10, record_img.shape[0]), (150,150,150), 4)
                if rechts:
                    cv2.line(record_img,
                             (record_img.shape[1]-10, 0),
                             (record_img.shape[1]-10, record_img.shape[0]),
                             (150,150,150), 4)

                self.C.write_frame(record_img)

            if self.state.linien_counter >= 12:
                if self.state.stop_time == 0.0:
                    self.state.stop_time = time.time() + endstop
                if time.time() > self.state.stop_time:
                    self.stop_sequence()
                    break

        self.D.stop()
        self.D.gerade()
        self.L.stop()
        time.sleep(5)
        self.L.all_off()

#/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=//=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/

    def main_obstacle(self):

        # ================= INIT =================
        self.state.linien_counter = 0
        self.state.hindernis = False
        self.state.h_zeit = 0.0
        self.state.letzte_farbe = "N"
        self.state.Rennen_laeuft = True
        self.state.blaue_linie = False
        self.state.orange_linie = False
        self.state.linie_imbild = False

        self.pink_last = 0

        presets = {
            "slow": {
                "endstop": 3.3,
                "run_speed": 0.25,
                "linie_warten": 2.3,
                "linie_zaehlen": 0.45
            },
            "medium": {
                "endstop": 2.5,
                "run_speed": 0.55,
                "linie_warten": 1.8,
                "linie_zaehlen": 0.35
            },
            "fast": {
                "endstop": 1.7,
                "run_speed": 0.7,
                "linie_warten": 1.2,
                "linie_zaehlen": 0.30
            }
        }

        if self.state.slow:
            preset = presets["slow"]
        elif self.state.medium:
            preset = presets["medium"]
        else:
            preset = presets["fast"]

        endstop = preset["endstop"]
        run_speed = preset["run_speed"]
        self.state.linie_warten = preset["linie_warten"]
        self.state.linie_zaehlen = preset["linie_zaehlen"]

        # ================= START =================
        self.WL.write_Log("linie_warten: "+str(self.state.linie_warten))
        self.WL.write_Log("linie_zaehlen: "+str(self.state.linie_zaehlen))
        self.WL.write_Log("endstop: "+str(endstop))
        self.WL.write_Log("mode slow: "+str(self.state.slow))
        self.WL.write_Log("mode medium: "+str(self.state.medium))
        self.WL.write_Log("mode fast: "+str(self.state.fast))
        
        if not self.TEST:
            self.ausparken()
        self.D.vor(self.speed)

        while not self.D.button_pressed() and self.state.Rennen_laeuft:

            if time.time() > self.state.stop_time:
                self.D.stop()
                self.L.stop()
                self.WL.write_Log("Runde Beendet")
                break

            self.messen()
            
            # ---------------- VIDEO ----------------
            record_img = self.bgr_main.copy()

            # ---- Linien anzeigen ----
            if self.state.current_direction == "l":
                if self.state.blaue_linie:
                    cv2.line(
                        record_img,
                        (0, 150),
                        (320, 150),
                        (255, 0, 0),   # Blau
                        5
                    )
                

            elif self.state.current_direction == "r":
                if self.state.orange_linie:
                    cv2.line(
                        record_img,
                        (0, 150),
                        (320, 150),
                        (0, 140, 255), # Orange
                        5
                    )

            # ---- Hindernis vertikal markieren ----
            if self.state.farbe == "R":
                cv2.line(
                    record_img,
                    (int(self.x), 0),
                    (int(self.x), record_img.shape[0]),
                    (0, 0, 255),   # Rot
                    4
                )

            elif self.state.farbe == "G":
                cv2.line(
                    record_img,
                    (int(self.x), 0),
                    (int(self.x), record_img.shape[0]),
                    (0, 255, 0),   # Grün
                    4
                )

            # ---- Wand links markieren ----
            if self.links:
                cv2.line(
                    record_img,
                    (10, 0),
                    (10, record_img.shape[0]),
                    (150, 150, 150),   # Grau
                    4
                )

            # ---- Wand rechts markieren ----
            if self.rechts:
                cv2.line(
                    record_img,
                    (record_img.shape[1]-10, 0),
                    (record_img.shape[1]-10, record_img.shape[0]),
                    (150, 150, 150),
                    4
                )

            # ---- Magenta-Wände markieren ----
            if self.linksMag:
                cv2.line(
                    record_img,
                    (25, 0),
                    (25, record_img.shape[0]),
                    (255, 0, 255),
                    4
                )

            if self.rechtsMag:
                cv2.line(
                    record_img,
                    (record_img.shape[1]-25, 0),
                    (record_img.shape[1]-25, record_img.shape[0]),
                    (255, 0, 255),
                    4
                )

            # ---- Frame speichern ----
            self.C.write_frame(record_img)

            self.linien_suchen_obstacle(self.hsv_line)

            special = False

            # =========================================================
            # 1. WAND / LIDAR (höchste Priorität)
            # =========================================================

            if self.hellLMag > 9600 and self.hellRMag > 9600:
                special = True
                self.WL.write_Log("hellLMag: "+str(self.hellLMag))
                self.WL.write_Log("hellRMag: "+str(self.hellRMag))
                
                if self.state.current_direction == "l":
                    self.D.nach_links()
                else:
                    self.D.nach_rechts()

            elif (self.links or self.linksMag) and not self.rechts:
                special = True
                self.WL.write_Log("links: "+str(self.links))
                if self.state.gesamt <= self.state.geradeaus + 60:
                    self.D.nach_rechts()
                else:
                    self.D.nach_links()

            elif (self.rechts or self.rechtsMag) and not self.links:
                special = True
                self.WL.write_Log("rechts: "+str(self.rechts))
                if self.state.gesamt >= self.state.geradeaus - 60:
                    self.D.nach_links()
                else:
                    self.D.nach_rechts()

                """elif self.state.LDL < 100 or self.state.LDR < 100:
                special = True
                self.pink_last = time.time()
                self.WL.write_Log("Lidar links: "+str(self.state.LDL))
                self.WL.write_Log("Lidar rechts: "+str(self.state.LDR))

                if self.state.LDL < self.state.LDR:
                    self.D.nach_rechts()
                    self.L.on(2, PINK)
                elif self.state.LDR < self.state.LDL:
                    self.D.nach_links()
                    self.L.on(2, PINK)"""
                    
            elif self.state.LDV < 70 and self.state.LDV > 0:
                special = True
                self.pink_last = time.time()
                self.WL.write_Log("Lidar vorne < 70: "+str(self.state.LDV))
                self.D.gerade()
                self.D.ruck(0.3)
                time.sleep(1.0)
                self.D.stop()
                self.geradeaus_lenken()
                time.sleep(0.2)
                self.D.vor(self.speed)
                

            # =========================================================
            # 2. HINDERNISLOGIK
            # =========================================================

            elif self.state.farbe == "R" and not self.state.linie_imbild:

                self.state.letzte_farbe = self.state.farbe
                self.L.on(0, RED)
                special = True
                
                #self.WL.write_Log("size rot: "+str(self.s))
                #self.WL.write_Log("X rot: "+str(self.x))

                # --- Steeringpoint ---
                if self.s < 500:
                    steeringpoint = 110
                elif self.s < 1000:
                    steeringpoint = 60
                elif self.s < 2500:
                    steeringpoint = 30
                else:
                    steeringpoint = 0

                # --- Hindernis > 100: direkt ausweichen ---
                if self.s >= 5000:
                    self.D.ausweichen_rechts()
                    self.state.hindernis = True
                    self.state.h_zeit = time.time()
                    self.WL.write_Log("Ausweichen hindernis rot")

                # --- Lenkphase ---
                elif (self.x > steeringpoint) and (self.x > 0):
                    abstand = self.x - steeringpoint
                    lenkwinkel = 96 + self.state.kh * abstand
                    
                    print("lenkwinkel rot: ", lenkwinkel)
                    print("abstand rot: ", abstand)
                    print("steerinpoint rot: ", steeringpoint)

                    if lenkwinkel > 96 and self.state.LDR < 100:
                        lenkwinkel = 96
                        #self.geradeaus_lenken()
                        self.L.on(2, PINK)
                        self.pink_last = time.time()
                        self.WL.write_Log("Lidar verhindert lenken nach rechts/Hindernis rot")

                    self.D.servo_angle(lenkwinkel)
                    #self.WL.write_Log("lenkwinkel rot: " + str(lenkwinkel))
                    if self.state.gesamt < self.state.geradeaus + 80:
                        self.D.servo_angle(lenkwinkel)
                        #self.WL.write_Log("lenkwinkel rot: " + str(lenkwinkel))
                    #else:
                        #self.D.gerade()

                    self.state.hindernis = True
                    self.state.h_zeit = time.time()

                # --- Geradeaus ---
                else:
                    self.D.gerade()
                    self.state.hindernis = True
                    self.state.h_zeit = time.time()


            elif self.state.farbe == "G" and not self.state.linie_imbild:

                self.state.letzte_farbe = self.state.farbe
                self.L.on(0, GREEN)
                special = True
                #self.WL.write_Log("size gruen: "+str(self.s))
                #self.WL.write_Log("X gruen: "+str(self.x))

                # --- Steeringpoint ---
                if self.s < 500:
                    steeringpoint = 110
                elif self.s < 1000:
                    steeringpoint = 60
                elif self.s < 2500:
                    steeringpoint = 30
                else:
                    steeringpoint = 0

                # --- Hindernis > 5000 ---
                if self.s >= 5000:
                    self.D.ausweichen_links()
                    self.state.hindernis = True
                    self.state.h_zeit = time.time()
                    self.WL.write_Log("Ausweichen hindernis gruen")

                # --- Lenkphase ---
                elif self.x < (320 - steeringpoint) and (self.x > 0):
                    abstand = self.x - (320 - steeringpoint)
                    lenkwinkel = 96 + self.state.kh * abstand
                    
                    print("lenkwinkel grun: ", lenkwinkel)
                    print("abstand grun: ", abstand)
                    print("steerinpoint grun: ", steeringpoint)
                    
                    if lenkwinkel < 96 and self.state.LDL < 100:
                        lenkwinkel = 96
                        #self.geradeaus_lenken()
                        self.L.on(2, PINK)
                        self.pink_last = time.time()
                        self.WL.write_Log("Lidar verhindert lenken nach links/Hindernis grun")

                    self.D.servo_angle(lenkwinkel)
                    #self.WL.write_Log("lenkwinkel gruen: " + str(lenkwinkel))
                    
                    if self.state.gesamt > self.state.geradeaus - 80:
                        self.D.servo_angle(lenkwinkel)
                        #self.WL.write_Log("lenkwinkel gruen: " + str(lenkwinkel))
                    #else:
                        #self.D.gerade()

                    self.state.hindernis = True
                    self.state.h_zeit = time.time()

                # --- Geradeaus ---
                else:
                    self.D.gerade()
                    self.state.hindernis = True
                    self.state.h_zeit = time.time()
                        

            # =========================================================
            # 3. HINDERNIS RESET
            # =========================================================
            if self.state.hindernis and not special:
                if time.time() - self.state.h_zeit > self.state.h_warten:
                    self.geradeaus_lenken()
                    self.state.hindernis = False
                    self.L.on(0, WHITE)
                else:
                    self.D.gerade()
                    
            # =========================================================
            # 4. NORMALFAHRT (nur wenn nichts aktiv)
            # =========================================================
            if not special and not self.state.hindernis:
                self.geradeaus_lenken()

            # =========================================================
            # 5. PINK RESET
            # =========================================================
            if time.time() > self.pink_last + 1.0:
                self.L.off(2)

        self.D.stop()
        self.L.countdown3()
        self.einparken()
        self.stop_sequence()
        self.D.stop()
        self.D.gerade()
        time.sleep(2)
        self.L.all_off()
        
#<<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>><<>>><<>><<>><<>>        

if __name__ == "__main__":
    rr = Roadrunner()
    rr.safe_run()
    
