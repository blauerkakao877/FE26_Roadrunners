import DrivingBase as d
import Led as l
import Cam_moduls as c
import Gyro as g
import lidar_data as ld
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from Color_defs import *
from Roadrunner_state import State

import time
import cv2

class Roadrunner:

    def __init__(self):
        self.state = State()
        self.state.Rennen_laeuft = False
        self.speed = 0.35
        # Presets
        self.state.slow = False
        self.state.medium = False
        self.state.fast = True

        self.D = d.DrivingBase()
        self.L = l.Led()
        self.C = c.CameraModules(self.state)
        self.C.init("open")
        self.G = g.Gyro()
        self.LD = ld.LIDAR_DATA()

    def start_sequence(self):
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
        self.LD.send_start_signal()
        time.sleep(0.1)

        hsv_full, hsv_main, bgr_main, hsv_line, bgr_line = self.C.get_image()
        ausfahrt_L, ausfahrt_R = self.C.finde_ausfahrt(hsv_main)

        if ausfahrt_L:
            self.state.mode = "obstacle"
            self.L.all_off()
            self.L.on(0, MAGENTA)
            self.L.on(3, MAGENTA)
            print("Ausfahrt links")
        elif ausfahrt_R:
            self.state.mode = "obstacle"
            self.L.all_off()
            self.L.on(1, MAGENTA)
            self.L.on(2, MAGENTA)
            print("Ausfahrt rechts")
        else:
            self.state.mode = "open"
            self.L.all_W()
            print("Openrace")

        self.D.gerade()
        self.state.Rennen_laeuft = True
        print("Starting Roadrunner_Open main sequence...")

    def stop_sequence(self):
        self.state.Rennen_laeuft = False
        self.D.stop()
        self.L.stop()
        self.C.enable_recording(False)
        print("Roadrunner_Open main sequence stopped.")

    def linien_suchen(self, hsv_line):
        # Linie links (blau)
        if self.state.current_direction == "l":
            if (time.time() - self.state.linien_zeit) > self.state.linien_warten:
                if self.C.finde_blau(hsv_line):
                    self.state.linien_zeit = time.time()
                    self.state.blaue_linie = True
                    self.state.linien_zaehlen = self.state.linien_zaehlen_b
                    if self.state.linien_counter == 12:
                        self.state.Rennen_laeuft = False
            else:
                if self.state.blaue_linie and time.time() - self.state.linien_zeit > self.state.linien_zaehlen:
                    self.state.linien_counter += 1
                    self.L.led_B1()
                    self.state.geradeaus = self.state.linien_counter * (-90)
                    self.state.blaue_linie = False

        # Linie rechts (orange)
        elif self.state.current_direction == "r":
            if (time.time() - self.state.linien_zeit) > self.state.linien_warten:
                if self.C.finde_orange(hsv_line):
                    self.state.linien_zeit = time.time()
                    self.state.orange_linie = True
                    self.state.linien_zaehlen = self.state.linien_zaehlen_o
                    if self.state.linien_counter == 12:
                        self.state.Rennen_laeuft = False
            else:
                if self.state.orange_linie and time.time() - self.state.linien_zeit > self.state.linien_zaehlen:
                    self.state.linien_counter += 1
                    self.L.led_O1()
                    self.state.geradeaus = self.state.linien_counter * 90
                    self.state.orange_linie = False

        # Noch keine Richtung gesetzt
        else:
            if self.C.finde_blau(hsv_line):
                self.state.current_direction = "l"
                self.state.linien_zeit = time.time()
                self.state.blaue_linie = True
                self.speed = self.speed * 1.2
                self.D.vor(self.speed)
            elif self.C.finde_orange(hsv_line):
                self.state.current_direction = "r"
                self.state.linien_zeit = time.time()
                self.state.orange_linie = True
                self.speed = self.speed * 1.2
                self.D.vor(self.speed)


    def main(self):
        self.state.linien_counter = 0
        stop_time = None
        current_direction = None
        found_line = False
        last_line_time = 0.0
        geradeaus = 0
        drift_kor = 0.0
        k = 0.6
        draw_line_until = 0

        # Presetwerte
        presets = {
            "slow":   {"endstop": 3.0, "linie_warten": 0.6, "line_cooldown": 1.0, "run_speed": 0.4},
            "medium": {"endstop": 2.5, "linie_warten": 0.4, "line_cooldown": 1.0, "run_speed": 0.55},
            "fast":   {"endstop": 2.0, "linie_warten": 0.25, "line_cooldown": 1.0, "run_speed": 0.64}
        }

        # Aktuelles Preset wählen
        if self.state.slow:
            preset = presets["slow"]
        elif self.state.medium:
            preset = presets["medium"]
        elif self.state.fast:
            preset = presets["fast"]
        else:
            preset = presets["slow"]

        endstop = preset["endstop"]
        linie_warten = preset["linie_warten"]
        line_cooldown = preset["line_cooldown"]
        run_speed = preset["run_speed"]

        self.D.stop()
        self.L.booting()
        self.start_sequence()
        time.sleep(0.2)
        self.D.anfahren()
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

            # Linien-Erkennung
            line_found = False
            if hsv_line is not None:
                try:
                    if not found_line:
                        if self.C.finde_blau(hsv_line):
                            current_direction = "b"
                            self.L.B()
                            found_line = True
                            drift_kor = -0.3
                        elif self.C.finde_orange(hsv_line):
                            current_direction = "o"
                            self.L.O()
                            found_line = True
                            drift_kor = 0.3
                    else:
                        if current_direction == "b" and self.C.finde_blau(hsv_line):
                            self.L.B()
                        elif current_direction == "o" and self.C.finde_orange(hsv_line):
                            self.L.O()
                    line_found = found_line
                except Exception as e:
                    print("Fehler bei Linien-Erkennung:", e)

            # Gyro + Linien-Offset berechnen
            try:
                winkel, gesamt = self.G.WinkelMessen()
                if found_line:
                    geradeaus = self.state.linien_counter * (-90 if current_direction=="b" else 90)
                    print("geradeaus: ", geradeaus)
                    print("linien: ", self.state.linien_counter)
                else:
                    geradeaus = 0

                gesamt += drift_kor * self.state.linien_counter
                offset = k * (geradeaus - gesamt)
                offset = max(-30, min(30, offset))
                self.D.steer(offset)
            except Exception as e:
                print("Gyro-Fehler:", e)

            # Linien-Counter & Pause
            if line_found and (time.time() - last_line_time) > line_cooldown:
                last_line_time = time.time()
                time.sleep(linie_warten)
                self.state.linien_counter += 1
                self.L.all_off()
                draw_line_until = time.time() + line_cooldown

                if self.state.linien_counter > 0:
                    self.D.vor(run_speed)

            # Wände-Steuerung
            if links and not rechts:
                self.D.steer(25)
            elif rechts and not links:
                self.D.steer(-25)
            elif links and rechts:
                if found_line:
                    if gesamt >= geradeaus:
                        self.D.steer(-30)
                    else:
                        self.D.steer(30)

            # Video / Linien einzeichnen
            if bgr_main is not None:
                record_img = bgr_main.copy()
                if time.time() < draw_line_until:
                    if current_direction == "b":
                        cv2.line(record_img, (0, 150), (320, 150), (255, 0, 0), 5)
                    elif current_direction == "o":
                        cv2.line(record_img, (0, 154), (320, 154), (0, 128, 255), 5)
                if links:
                    cv2.line(record_img, (10, 0), (10, record_img.shape[0]), (128, 128, 128), 5)
                if rechts:
                    cv2.line(record_img, (310, 0), (310, record_img.shape[0]), (128, 128, 128), 5)
                self.C.write_frame(record_img)

            # Rennen stoppen nach Linienanzahl
            if self.state.linien_counter >= 12:
                if stop_time is None:
                    stop_time = time.time() + endstop
                if time.time() > stop_time:
                    self.stop_sequence()
                    break

        self.D.stop()
        self.D.gerade()
        self.L.stop()
        time.sleep(10)
        self.L.all_off()


if __name__ == "__main__":
    rr = Roadrunner()
    rr.main()