import DrivingBase as d
import Led as l
import Cam_moduls as c
import Gyro as g
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from Color_defs import *

import time
import cv2

class Roadrunner_open:

    def __init__(self):
        self.Rennen_laeuft = False
        self.speed = 0.35
        #<<<<<<<activate presets>>>>>>>>>
        self.slow = False
        self.medium = False
        self.fast = True

        self.D = d.DrivingBase()
        self.L = l.Led()
        self.C = c.CameraModules()
        self.C.init("open")
        self.G = g.Gyro()

    def start_sequence(self):
        self.G.start()
        if self.slow:
            self.L.waiting_S()
        elif self.medium:
            self.L.waiting_M()
        elif self.fast:
            self.L.waiting_F()
        else:
            self.L.waiting()
            
        self.D.wait_for_button_press()
        time.sleep(0.1)
        self.D.gerade()
        self.Rennen_laeuft = True
        self.L.all_off()

        self.C.enable_recording(True)

        print("Starting Roadrunner_Open main sequence...")

    def stop_sequence(self):
        self.Rennen_laeuft = False
        self.D.stop()
        self.L.stop()
        self.C.enable_recording(False)
        print("Roadrunner_Open main sequence stopped.")

    def main(self):
        stop_time = None
        line_color = None
        found_line = False
        linien_counter = 0
        last_line_time = 0.0
        geradeaus = 0
        drift_kor = 0.0
        k = 0.6
        draw_line_until = 0
        
        #slow
        endstop1 = 3.0
        linie_warten1 = 0.6
        line_cooldown1 = 1.0
        endstop1 = 3.0
        run_speed1 = 0.4
        
        #medium
        endstop2 = 2.5
        linie_warten2 = 0.4
        line_cooldown2 = 1.0
        endstop2 = 2.5
        run_speed2 = 0.55
        
        #fast
        endstop3 = 2.0
        linie_warten3 = 0.2
        line_cooldown3 = 1.0
        endstop3 = 2.0
        run_speed3 = 0.64


        #set presets
        if self.slow:
            endstop = endstop1
            linie_warten = linie_warten1
            line_cooldown =  line_cooldown1
            endstop = endstop1
            run_speed = run_speed1
        elif self.medium:
            endstop = endstop2
            linie_warten = linie_warten2
            line_cooldown =  line_cooldown2
            endstop = endstop2
            run_speed = run_speed2
        elif self.fast:
            endstop = endstop3
            linie_warten = linie_warten3
            line_cooldown =  line_cooldown3
            endstop = endstop3
            run_speed = run_speed3
        else:
            #Standard slow bei Fehler beim setzten der Presets
            endstop = 3.0
            linie_warten = 0.6
            line_cooldown = 1.0
            endstop = 3.0
            run_speed = 0.4



        self.L.booting()
        self.start_sequence()
        time.sleep(0.2)
        self.D.anfahren()
        self.D.vor(self.speed)

        while self.Rennen_laeuft and not self.D.button_pressed():

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

            if line_color == "blau":
                geradeaus = linien_counter * (-90)
            elif line_color == "orange":
                geradeaus = linien_counter * (90)
            else:
                geradeaus = 0

            try:
                winkel, gesamt = self.G.WinkelMessen()
                gesamt = gesamt + (drift_kor * linien_counter)
                offset = k * (geradeaus - gesamt)
                offset = max(-30, min(30, offset))
                self.D.steer(offset)

            except Exception as e:
                print("Gyro-Fehler:", e)

            found = False
            if hsv_line is not None:
                try:
                    if not found_line:
                        if self.C.finde_blau(hsv_line):
                            found = True
                            line_color = "blau"
                            self.L.B()
                            found_line = True
                            drift_kor = -0.3
                        elif self.C.finde_orange(hsv_line):
                            found = True
                            line_color = "orange"
                            self.L.O()
                            found_line = True
                            drift_kor = 0.3   
                    else:
                        if line_color == "blau" and self.C.finde_blau(hsv_line):
                            found = True
                            self.L.B()
                        elif line_color == "orange" and self.C.finde_orange(hsv_line):
                            found = True
                            self.L.O()
                except Exception as e:
                    print("Fehler bei linien:", e)

            if found and (time.time() - last_line_time) > line_cooldown:
                last_line_time = time.time()
                time.sleep(linie_warten)
                linien_counter += 1
                self.L.all_off()

                draw_line_until = time.time() + line_cooldown

                if linien_counter > 0:
                    self.D.vor(run_speed)

            if links and not rechts:
                self.D.steer(25)
            elif rechts and not links:
                self.D.steer(-25)
            elif links and rechts:
                if gesamt >= geradeaus:
                    self.D.steer(-30)
                else:
                    self.D.steer(30)

            if bgr_main is not None:
                record_img = bgr_main.copy()

                if time.time() < draw_line_until:
                    if line_color == "blau":
                        cv2.line(record_img, (0, 150), (320, 150), (255, 0, 0), 5)
                    elif line_color == "orange":
                        cv2.line(record_img, (0, 154), (320, 154), (0, 128, 255), 5)

                if links:
                    cv2.line(record_img, (10, 0), (10, record_img.shape[0]), (128, 128, 128), 5)

                if rechts:
                    cv2.line(record_img, (310, 0), (310, record_img.shape[0]), (128, 128, 128), 5)

                self.C.write_frame(record_img)

            if linien_counter >= 12:
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
    rr = Roadrunner_open()
    rr.main()