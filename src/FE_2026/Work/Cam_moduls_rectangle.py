from picamera2 import Picamera2
import numpy as np
import Cam as C
import Led as L
import cv2
import time
from datetime import datetime
from Roadrunner_state import State
import os

class CameraModules:

    def __init__(self, RRState):
        self.state = RRState
        self.blob_detector = None
        self.hindernis_detector = None

        # Masken
        self.o_mask = None
        self.b_mask = None
        self.g_mask = None
        self.r_mask = None
        self.maskL = None
        self.maskR = None
        self.M_mask = None

        # Bilder
        self.hsv_full = None
        self.hsv_main = None
        self.bgr_main = None
        self.hsv_line = None
        self.bgr_line = None

        self.line_height = 60
        self.top_cut = 10 #27 ohne über Bande sehen
        
        self.ignore_top_pixels = 15   # 🔧 REGELBAR

        self.frontcam = None
        self.backcam = None

        # Videoaufnahme
        self.video_writer = None
        self.recording = False
        self.record_enabled = False

        self.ML_hue = 140
        self.MU_hue = 170
        self.ML_sat = 50
        self.MU_sat = 255
        self.ML_val = 50
        self.MU_val = 255

    # ================= INITIAL =================
    def init(self, mode="obstacle"):
        # Blob-Detektoren
        blob_params = cv2.SimpleBlobDetector_Params()
        blob_params.filterByArea = True
        blob_params.minArea = 6000
        blob_params.maxArea = 10000

        hindernis_params = cv2.SimpleBlobDetector_Params()
        hindernis_params.filterByArea = True
        hindernis_params.minArea = 2000
        hindernis_params.maxArea = 50000

        self.blob_detector = cv2.SimpleBlobDetector_create(blob_params)
        self.hindernis_detector = cv2.SimpleBlobDetector_create(hindernis_params)

        self.get_colorfilter_data()

        # Kameras starten
        self.frontcam = C.Cam(1)
        self.frontcam.start()
        self.backcam = C.Cam(0)
        self.backcam.start()

        time.sleep(2.0)

    # ================= VIDEO =================
    def enable_recording(self, state, folder="/home/pi/FE_2026/Videos", fps=20.0):
        self.record_enabled = state
        if state:
            if self.bgr_main is None:
                self.get_image()
            os.makedirs(folder, exist_ok=True)
            h, w = self.bgr_main.shape[:2]
            filename = os.path.join(folder, f"fahrt_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.avi")
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (w, h))
            self.recording = self.video_writer.isOpened()
        else:
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
                self.recording = False

    def write_frame(self, frame):
        if self.record_enabled and self.recording and self.video_writer is not None:
            self.video_writer.write(frame)

    # ================= BILDER =================
    def get_image(self):
        frame = self.frontcam.get_image()
        self.hsv_full = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h = frame.shape[0]
        self.bgr_main = frame[self.top_cut:h, :]
        self.hsv_main = self.hsv_full[self.top_cut:h, :]
        self.bgr_line = frame[h-self.line_height:h, :]
        self.hsv_line = self.hsv_full[h-self.line_height:h, :]
        return self.hsv_full, self.hsv_main, self.bgr_main, self.hsv_line, self.bgr_line

    def get_image_back(self):
        frame = self.backcam.get_image()
        frame = frame[self.top_cut:, :]
        self.hsv_full = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.bgr_main = frame
        self.hsv_main = self.hsv_full
        h = frame.shape[0]
        self.bgr_line = frame[h-self.line_height:h, :]
        self.hsv_line = self.hsv_full[h-self.line_height:h, :]
        return self.hsv_full, self.hsv_main, self.bgr_main, self.hsv_line, self.bgr_line

    def stop(self):
        self.frontcam.stop()
        self.backcam.stop()
        if self.video_writer is not None:
            self.video_writer.release()

    # ================= COLOR FILTER =================
    def get_colorfilter_data(self):
        # Standardwerte falls Datei fehlt
        self.BL_hue, self.BU_hue = 90, 130
        self.BL_sat, self.BU_sat = 80, 255
        self.BL_val, self.BU_val = 80, 255

        self.OL_hue, self.OU_hue = 5, 25
        self.OL_sat, self.OU_sat = 80, 255
        self.OL_val, self.OU_val = 80, 255

        self.RL_hue, self.RU_hue = 10, 170
        self.RL_sat, self.RU_sat = 80, 255
        self.RL_val, self.RU_val = 80, 255

        self.GL_hue, self.GU_hue = 35, 85
        self.GL_sat, self.GU_sat = 80, 255
        self.GL_val, self.GU_val = 80, 255

        self.ML_hue, self.MU_hue = 125, 160
        self.ML_sat, self.MU_sat = 80, 255
        self.ML_val, self.MU_val = 80, 255

        # ---------------- Datei einlesen ----------------
        try:
            with open("/home/pi/FE_2026/Data/Colorfilter.dat", "r") as f:
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) >= 15:
                # Blau
                self.BL_hue, self.BU_hue = map(int, lines[0].split(","))
                self.BL_sat, self.BU_sat = map(int, lines[1].split(","))
                self.BL_val, self.BU_val = map(int, lines[2].split(","))

                # Orange
                self.OL_hue, self.OU_hue = map(int, lines[3].split(","))
                self.OL_sat, self.OU_sat = map(int, lines[4].split(","))
                self.OL_val, self.OU_val = map(int, lines[5].split(","))

                # Rot
                self.RL_hue, self.RU_hue = map(int, lines[6].split(","))
                self.RL_sat, self.RU_sat = map(int, lines[7].split(","))
                self.RL_val, self.RU_val = map(int, lines[8].split(","))

                # Grün
                self.GL_hue, self.GU_hue = map(int, lines[9].split(","))
                self.GL_sat, self.GU_sat = map(int, lines[10].split(","))
                self.GL_val, self.GU_val = map(int, lines[11].split(","))

                # Magenta
                self.ML_hue, self.MU_hue = map(int, lines[12].split(","))
                self.ML_sat, self.MU_sat = map(int, lines[13].split(","))
                self.ML_val, self.MU_val = map(int, lines[14].split(","))
            else:
                print("Colorfilter.dat unvollständig, benutze Standardwerte")
        except Exception as e:
            print("Fehler beim Laden der Colorfilter.dat:", e)

    # ================= LINIEN =================
    def finde_blau(self, hsv):
        lower = np.array([self.BL_hue, self.BL_sat, self.BL_val])
        upper = np.array([self.BU_hue, self.BU_sat, self.BU_val])
        mask = cv2.inRange(hsv, lower, upper)
        self.b_mask = cv2.medianBlur(mask, 5)
        contours, _ = cv2.findContours(self.b_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return any(cv2.contourArea(cnt) > 500 for cnt in contours)

    def finde_orange(self, hsv):
        lower = np.array([self.OL_hue, self.OL_sat, self.OL_val])
        upper = np.array([self.OU_hue, self.OU_sat, self.OU_val])
        mask = cv2.inRange(hsv, lower, upper)
        self.o_mask = cv2.medianBlur(mask, 5)
        contours, _ = cv2.findContours(self.o_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return any(cv2.contourArea(cnt) > 500 for cnt in contours)

    # ================= HINDERNISSE =================
    def finde_rot(self, hsv):
        lower1 = np.array([0, self.RL_sat, self.RL_val])
        upper1 = np.array([self.RL_hue, self.RU_sat, self.RU_val])
        lower2 = np.array([self.RU_hue, self.RL_sat, self.RL_val])
        upper2 = np.array([179, self.RU_sat, self.RU_val])

        mask = cv2.bitwise_or(
            cv2.inRange(hsv, lower1, upper1),
            cv2.inRange(hsv, lower2, upper2)
        )

        mask = cv2.bitwise_not(mask)
        self.r_mask = cv2.medianBlur(mask, 5)

        contours, _ = cv2.findContours(self.r_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0,0,0

        gültige = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 2000:   # 🔧 MIN GRÖSSE (wie vorher)
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            y_unten = y + h

            if y_unten > self.ignore_top_pixels:
                gültige.append((cnt, area, x, y, w, h))

        if not gültige:
            return 0,0,0

        # größtes Objekt wählen
        cnt, area, x, y, w, h = max(gültige, key=lambda item: item[1])

        cx = x + w // 2
        cy = y + h // 2

        return cx, cy, area



    def finde_gruen(self, hsv):
        lower = np.array([self.GL_hue, self.GL_sat, self.GL_val])
        upper = np.array([self.GU_hue, self.GU_sat, self.GU_val])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.bitwise_not(mask)
        self.g_mask = cv2.medianBlur(mask, 5)

        contours, _ = cv2.findContours(self.g_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0,0,0

        gültige = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 2000:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            y_unten = y + h

            if y_unten > self.ignore_top_pixels:
                gültige.append((cnt, area, x, y, w, h))

        if not gültige:
            return 0,0,0

        cnt, area, x, y, w, h = max(gültige, key=lambda item: item[1])

        cx = x + w // 2
        cy = y + h // 2

        return cx, cy, area


    def finde_hindernisse(self, hsv):
        rx, ry, rs = self.finde_rot(hsv)
        gx, gy, gs = self.finde_gruen(hsv)
        if rs > gs and rs > 0:
            return rx, ry, rs, "R"
        elif gs >= rs and gs > 0:
            return gx, gy, gs, "G"
        else:
            return 0,0,0,"N"

    # ================= WÄNDE (SCHWARZ) =================
    def wand_filter(self, bgr):
        # Schwarze Wände erkennen
        lower = np.array([0, 0, 0])
        upper = np.array([120, 90, 90])
        return cv2.inRange(bgr, lower, upper)

    def waende(self, bgr_img):
        # Letzte 150 Pixel Höhe für Wände
        crop_image = bgr_img[-200:, :]
        mask = self.wand_filter(crop_image)
        self.maskL = mask[:, 5:144]
        self.maskR = mask[:, 179:315]
        histL = np.sum(self.maskL, axis=0)
        histR = np.sum(self.maskR, axis=0)
        
        kollL = np.max(histL) > 10000
        kollR = np.max(histR) > 10000
        
        return kollL, kollR, np.max(histL), np.max(histR)

    def parken_waende(self, bgr_img):
        # Kürzere Höhe für Parkprüfung
        crop_image = bgr_img[-120:, :]
        mask = self.wand_filter(crop_image)
        maskL = mask[:, 0:159]
        maskR = mask[:, 160:320]
        return np.max(np.sum(maskL, axis=1)), np.max(np.sum(maskR, axis=1))

    # ================= MAGENTA =================
    def wand_Magenta_filter(self, hsv_img):
        lower_color = np.array([self.ML_hue, self.ML_sat, self.ML_val])
        upper_color = np.array([self.MU_hue, self.MU_sat, self.MU_val])
        self.M_mask = cv2.inRange(hsv_img, lower_color, upper_color)
        return self.M_mask


    def waende_Magenta(self, hsv_img):
        mask = self.wand_Magenta_filter(hsv_img)

        # Ausschnitte links / rechts
        maskL = mask[0:150, 20:159]
        maskR = mask[0:150, 160:300]

        # Histogramme
        histL = np.sum(maskL, axis=0)
        histR = np.sum(maskR, axis=0)

        maxHistL = np.max(histL)
        maxHistR = np.max(histR)

        kollL = maxHistL > 10000
        kollR = maxHistR > 10000

        return kollL, kollR, maxHistL, maxHistR


    def finde_ausfahrt(self, hsv_img):
        mask = self.wand_Magenta_filter(hsv_img)

        maskL = mask[0:150, 5:159]
        maskR = mask[0:150, 160:315]

        histL = np.sum(maskL, axis=0)
        histR = np.sum(maskR, axis=0)

        maxHistL = np.max(histL)
        maxHistR = np.max(histR)

        # ❗ NEU: prüfen ob überhaupt Wand existiert
        if maxHistL < 500 and maxHistR < 500:
            return False, False  # keine Wand → keine Ausfahrt

        i = 1
        max_i = min(len(histL), len(histR))

        while i < max_i and histL[139 - i] > 0 and histR[i] > 0:
            i += 1

        ausfahrt_L = False
        ausfahrt_R = False

        if histL[139 - i] == 0:
            ausfahrt_L = True
        else:
            ausfahrt_R = True

        return ausfahrt_L, ausfahrt_R


    def detect_park_korrektur(self, hsv_img):
        crop_img = hsv_img[0:50, 0:320]

        mask_park = self.wand_Magenta_filter(crop_img)
        mask_park = cv2.copyMakeBorder(mask_park, 1, 1, 1, 1,
                                       cv2.BORDER_CONSTANT, value=[0, 0, 0])
        mask_park = cv2.bitwise_not(mask_park)

        park_keypoints = self.hindernis_detector.detect(mask_park)

        if not park_keypoints:
            return False

        # größtes Blob suchen
        s_max = 0
        for kp in park_keypoints:
            if kp.size > s_max:
                s_max = kp.size

        return s_max > 3000
# >>>>>>>>>>>>>>>>>>>>>Main<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

if __name__ == "__main__":

    state = State()
    cam = CameraModules(state)

    cam.init("open")

    # ==== Kamera auswählen ====
    cam.frontcam = cam.frontcam   # Frontkamera aktivieren
    # cam.frontcam = cam.backcam   # Backkamera aktivieren

    first_frame = True  # initialisieren für Fenster & Recording

    while True:
        hsv_full, hsv_main, bgr_main, hsv_line, bgr_line = cam.get_image()

        if first_frame:
            cv2.namedWindow("Main Image", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Record View", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Magenta Mask", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Wall Left", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Wall Right", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Blue Mask", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Orange Mask", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Red Mask", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Green Mask", cv2.WINDOW_NORMAL)
            cam.enable_recording(True, "/home/pi/FE_2026/Videos", fps=20.0)
            first_frame = False

        # Linien erkennen
        b_linie = cam.finde_blau(hsv_line)
        o_linie = cam.finde_orange(hsv_line)

        # Hindernisse erkennen
        x, y, s, farbe = cam.finde_hindernisse(hsv_main)

        # Magenta-Wände erkennen
        kollL_mag, kollR_mag, hellL, hellR = cam.waende_Magenta(hsv_main)

        # Schwarze Wände erkennen (separate Masken)
        kollL_schwarz, kollR_schwarz, histL_schwarz, histR_schwarz = cam.waende(bgr_main)
        h_crop = bgr_main[-200:, :]
        mask_schwarz = cam.wand_filter(h_crop)
        cam.maskL = mask_schwarz[:, 5:144]
        cam.maskR = mask_schwarz[:, 179:315]

        # Parkhindernis prüfen
        park = cam.detect_park_korrektur(hsv_main)

        # Ausfahrt erkennen
        ausfahrt_L, ausfahrt_R = cam.finde_ausfahrt(hsv_main)

        # ===== Kopie für Aufnahme =====
        record_img = bgr_main.copy()
        
        # IGNORIER-LINIE FÜR HINDERNISSE
        cv2.line(record_img,
                 (0, cam.ignore_top_pixels),
                 (record_img.shape[1], cam.ignore_top_pixels),
                 (255, 255, 0), 2)

        # Linien einzeichnen
        if b_linie:
            cv2.line(record_img,
                     (0, record_img.shape[0] - cam.line_height//2),
                     (record_img.shape[1], record_img.shape[0] - cam.line_height//2),
                     (255, 0, 0), 2)
        if o_linie:
            cv2.line(record_img,
                     (0, record_img.shape[0] - cam.line_height//2 + 4),
                     (record_img.shape[1], record_img.shape[0] - cam.line_height//2 + 4),
                     (0, 128, 255), 2)

        if farbe in ["R", "G"] and s > 0:
            color = (0,0,255) if farbe == "R" else (0,255,0)

            # Rechteck zeichnen
            cv2.rectangle(record_img,
                          (x-20, y-20),
                          (x+20, y+20),
                          color, 2)

            # Mittelpunkt
            cv2.circle(record_img, (x, y), 5, color, -1)

        # Wände einzeichnen
        if kollL_schwarz:
            cv2.line(record_img, (10, 0), (10, record_img.shape[0]), (50, 50, 50), 2)
        if kollR_schwarz:
            cv2.line(record_img, (record_img.shape[1]-10, 0), (record_img.shape[1]-10, record_img.shape[0]), (50, 50, 50), 2)

        if kollL_mag:
            cv2.line(record_img, (30, 0), (30, record_img.shape[0]), (255, 0, 255), 2)
        if kollR_mag:
            cv2.line(record_img, (record_img.shape[1]-30, 0), (record_img.shape[1]-30, record_img.shape[0]), (255, 0, 255), 2)

        # Anzeigen
        cv2.imshow("Main Image", bgr_main)
        cv2.imshow("Record View", record_img)

        # Masken anzeigen
        if cam.b_mask is not None:
            cv2.imshow("Blue Mask", cam.b_mask)
        if cam.o_mask is not None:
            cv2.imshow("Orange Mask", cam.o_mask)
        if cam.r_mask is not None:
            cv2.imshow("Red Mask", cam.r_mask)
        if cam.g_mask is not None:
            cv2.imshow("Green Mask", cam.g_mask)
        if cam.maskL is not None:
            cv2.imshow("Wall Left", cam.maskL)


        if cam.maskR is not None:
            cv2.imshow("Wall Right", cam.maskR)

        # Magenta-Maske
        magenta_mask = cam.wand_Magenta_filter(hsv_main)
        cv2.imshow("Magenta Mask", magenta_mask)

        # Video speichern
        cam.write_frame(record_img)

        # Beenden mit 'x'
        if cv2.waitKey(1) == ord("x"):
            break

    cam.enable_recording(False)
    cam.stop()
    cv2.destroyAllWindows()