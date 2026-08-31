from picamera2 import Picamera2
import numpy as np
import Cam as C
import Led as L
import cv2
import time
import math
import libcamera
from datetime import datetime
import os


class CameraModules:

    def __init__(self):

        self.blob_detector = None
        self.hindernis_detector = None

        self.o_mask = None
        self.b_mask = None
        self.g_mask = None
        self.r_mask = None
        self.maskL = None
        self.maskR = None

        self.hsv_full = None
        self.hsv_main = None
        self.bgr_main = None
        self.hsv_line = None
        self.bgr_line = None

        self.line_height = 60 # die pixel von unten nach oben ausgewählt
        # self.top_cut = 0 # die pixel von oben nach unten abgeschnitten
        self.top_cut = 27 # die pixel von oben nach unten abgeschnitten

        self.frontcam = None
        self.backcam = None

        self.video_writer = None
        self.recording = False


# ================= INIT =================

    def init(self, mode="obstacle"):

        blob_params = cv2.SimpleBlobDetector_Params()
        blob_params.filterByArea = True
        blob_params.minArea = 6000 # if mode == "open" else 200
        blob_params.maxArea = 10000

        hindernis_params = cv2.SimpleBlobDetector_Params()
        hindernis_params.filterByArea = True
        hindernis_params.minArea = 200
        hindernis_params.maxArea = 50000

        self.blob_detector = cv2.SimpleBlobDetector_create(blob_params)
        self.hindernis_detector = cv2.SimpleBlobDetector_create(hindernis_params)

        self.get_colorfilter_data()

        self.frontcam = C.Cam(1)
        self.frontcam.start()

        self.backcam = C.Cam(0)
        self.backcam.start()

        time.sleep(2.0)


# ================= VIDEO =================

    def start_video_recording(self, folder="/home/pi/FE_2026/Videos", fps=20.0):

        os.makedirs(folder, exist_ok=True)

        height, width = self.bgr_main.shape[:2]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(folder, f"fahrt_{timestamp}.avi")

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        self.recording = self.video_writer.isOpened()

        if self.recording:
            print("Videoaufnahme gestartet:", filename)
        else:
            print("Fehler: VideoWriter konnte nicht geöffnet werden.")


# ================= BILD EINLESEN =================

    def get_image(self):

        frame = self.frontcam.get_image()

        # HSV komplett
        self.hsv_full = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        h = frame.shape[0]

        # Hauptbild (oben etwas abgeschnitten)
        self.bgr_main = frame[self.top_cut:h, :]
        self.hsv_main = self.hsv_full[self.top_cut:h, :]

        # Linienbild (unterer Bereich)
        self.bgr_line = frame[h-self.line_height:h, :]
        self.hsv_line = self.hsv_full[h-self.line_height:h, :]

        return self.hsv_full, self.hsv_main, self.bgr_main, self.hsv_line, self.bgr_line


    def stop(self):
        self.frontcam.stop()
        self.backcam.stop()

        if self.video_writer is not None:
            self.video_writer.release()


# ================= COLORFILTER =================

    def get_colorfilter_data(self):

        with open("/home/pi/FE_2026/Data/Colorfilter.dat", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        values = []
        for line in lines:
            p = line.split(",")
            values.append((int(p[0]), int(p[1])))

        self.BL_hue, self.BU_hue = values[0]
        self.BL_sat, self.BU_sat = values[1]
        self.BL_val, self.BU_val = values[2]

        self.OL_hue, self.OU_hue = values[3]
        self.OL_sat, self.OU_sat = values[4]
        self.OL_val, self.OU_val = values[5]

        self.RL_hue, self.RU_hue = values[6]
        self.RL_sat, self.RU_sat = values[7]
        self.RL_val, self.RU_val = values[8]

        self.GL_hue, self.GU_hue = values[9]
        self.GL_sat, self.GU_sat = values[10]
        self.GL_val, self.GU_val = values[11]


# ================= LINIEN =================

    def finde_blau(self, hsv):
        lower = np.array([self.BL_hue, self.BL_sat, self.BL_val])
        upper = np.array([self.BU_hue, self.BU_sat, self.BU_val])

        mask = cv2.inRange(hsv, lower, upper)
        self.b_mask = cv2.medianBlur(mask, 5)
        cv2.rectangle(self.b_mask, (0, 0), (self.b_mask.shape[1]-1, self.b_mask.shape[0]-1), 0, 1)

        contours, _ = cv2.findContours(self.b_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        blobs_found = False
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area > 50:
                blobs_found = True
                x, y, w, h = cv2.boundingRect(cnt)
                # print(f"Blob {i}: Fläche = {area}, BoundingBox = ({x},{y},{w},{h})")

        return blobs_found


    def finde_orange(self, hsv):
        lower = np.array([self.OL_hue, self.OL_sat, self.OL_val])
        upper = np.array([self.OU_hue, self.OU_sat, self.OU_val])

        mask = cv2.inRange(hsv, lower, upper)
        self.o_mask = cv2.medianBlur(mask, 5)
        cv2.rectangle(self.o_mask, (0, 0), (self.o_mask.shape[1]-1, self.o_mask.shape[0]-1), 0, 1)

        contours, _ = cv2.findContours(self.o_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        blobs_found = False
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area > 50:
                blobs_found = True
                x, y, w, h = cv2.boundingRect(cnt)
                # print(f"Blob {i}: Fläche = {area}, BoundingBox = ({x},{y},{w},{h})")

        return blobs_found


# ================= WÄNDE =================

    def wand_filter(self, bgr):

        lower = np.array([0, 0, 0])
        upper = np.array([120, 90, 90])

        return cv2.inRange(bgr, lower, upper)


    def waende(self, bgr):

        mask = self.wand_filter(bgr)

        self.maskL = mask[:, 20:159]
        cv2.rectangle(self.maskL, (0, 0), (self.maskL.shape[1]-1, self.maskL.shape[0]-1), 0, 1)

        self.maskR = mask[:, 160:300]
        cv2.rectangle(self.maskR, (0, 0), (self.maskR.shape[1]-1, self.maskR.shape[0]-1), 0, 1)

        histL = np.sum(self.maskL, axis=0)
        histR = np.sum(self.maskR, axis=0)

        maxHistL = np.max(histL)
        maxHistR = np.max(histR)

        kollL = maxHistL > 25000
        kollR = maxHistR > 25000

        return kollL, kollR, maxHistL, maxHistR


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
        cv2.rectangle(self.r_mask, (0, 0), (self.r_mask.shape[1]-1, self.r_mask.shape[0]-1), 255, 1)

        kp = self.hindernis_detector.detect(self.r_mask)

        s_max = 0
        x = 0
        y = 0

        for k in kp:
            if k.size > s_max:
                s_max = k.size
                x, y = k.pt

        return x, y, s_max


    def finde_gruen(self, hsv):

        lower = np.array([self.GL_hue, self.GL_sat, self.GL_val])
        upper = np.array([self.GU_hue, self.GU_sat, self.GU_val])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.bitwise_not(mask)

        self.g_mask = cv2.medianBlur(mask, 5)
        cv2.rectangle(self.g_mask, (0, 0), (self.g_mask.shape[1]-1, self.g_mask.shape[0]-1), 255, 1)

        kp = self.hindernis_detector.detect(self.g_mask)

        s_max = 0
        x = 0
        y = 0

        for k in kp:
            if k.size > s_max:
                s_max = k.size
                x, y = k.pt

        return x, y, s_max


    def finde_hindernisse(self, hsv):

        rx, ry, rs = self.finde_rot(hsv)
        gx, gy, gs = self.finde_gruen(hsv)

        if rs > gs and rs > 0:
            return round(rx), round(ry), round(rs), "R"

        elif gs >= rs and gs > 0:
            return round(gx), round(gy), round(gs), "G"

        else:
            return 0, 0, 0, "N"


# ================= MAIN =================

if __name__ == "__main__":

    cam = CameraModules()
    cam.init("open")

    first_frame = True

    while True:

        hsv_full, hsv_main, bgr_main, hsv_line, bgr_line = cam.get_image()

        if first_frame:
            cv2.namedWindow("main image", cv2.WINDOW_NORMAL)
            cv2.namedWindow("record view", cv2.WINDOW_NORMAL)

            cam.start_video_recording("/home/pi/FE_2026/Videos", fps=20.0)
            first_frame = False

        # Linien erkennen
        b_linie = cam.finde_blau(hsv_line)
        o_linie = cam.finde_orange(hsv_line)

        # Wände
        links, rechts, hellL, hellR = cam.waende(bgr_main)

        # Hindernisse
        x, y, s, farbe = cam.finde_hindernisse(hsv_main)

        # ===== Kopie für Aufnahme =====
        record_img = bgr_main.copy()

        # ===== Position des Linien-Suchbereichs ins record_img umrechnen =====
        full_h = hsv_full.shape[0]

        line_y1_full = full_h - cam.line_height
        line_y2_full = full_h - 1

        line_y1 = line_y1_full - cam.top_cut
        line_y2 = line_y2_full - cam.top_cut

        # Sicherheit: innerhalb des sichtbaren Bildes halten
        line_y1 = max(0, line_y1)
        line_y2 = min(record_img.shape[0] - 1, line_y2)

        # ===== Info-Leiste oben =====
        cv2.rectangle(record_img, (0, 0), (record_img.shape[1], 30), (30, 30, 30), -1)
        cv2.putText(record_img, f"Blau: {b_linie}  Orange: {o_linie}  Hindernis: {farbe}",
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # ===== Tatsächlichen Linien-Suchbereich markieren =====
        overlay = record_img.copy()
        cv2.rectangle(overlay, (0, line_y1), (record_img.shape[1], line_y2), (60, 60, 60), -1)
        cv2.addWeighted(overlay, 0.18, record_img, 0.82, 0, record_img)

        cv2.putText(record_img, "LINIENBEREICH", (10, max(45, line_y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

        # ===== Erkannte Linien im echten Bereich anzeigen =====
        if b_linie:
            cv2.rectangle(record_img, (0, line_y1), (record_img.shape[1], line_y2), (255, 0, 0), 2)
            cv2.putText(record_img, "BLAU", (record_img.shape[1] - 70, line_y1 + 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

        if o_linie:
            cv2.rectangle(record_img, (3, line_y1 + 3), (record_img.shape[1] - 3, line_y2 - 3), (0, 140, 255), 2)
            cv2.putText(record_img, "ORANGE", (record_img.shape[1] - 95, line_y1 + 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 2, cv2.LINE_AA)

        # ===== Wände als halbtransparente Flächen =====
        if links:
            overlay = record_img.copy()
            cv2.rectangle(overlay, (0, 0), (40, record_img.shape[0]), (80, 80, 80), -1)
            cv2.addWeighted(overlay, 0.35, record_img, 0.65, 0, record_img)
            cv2.putText(record_img, "WAND L", (5, record_img.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        if rechts:
            overlay = record_img.copy()
            cv2.rectangle(overlay, (record_img.shape[1] - 40, 0),
                          (record_img.shape[1], record_img.shape[0]), (80, 80, 80), -1)
            cv2.addWeighted(overlay, 0.35, record_img, 0.65, 0, record_img)
            cv2.putText(record_img, "WAND R", (record_img.shape[1] - 75, record_img.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # ===== Hindernisse schöner markieren =====
        if farbe == "R":
            cv2.line(record_img, (x, 0), (x, record_img.shape[0]), (0, 0, 255), 2)
            cv2.circle(record_img, (x, y), 8, (0, 0, 255), -1)
            cv2.putText(record_img, "ROT", (x + 10, max(20, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

        if farbe == "G":
            cv2.line(record_img, (x, 0), (x, record_img.shape[0]), (0, 255, 0), 2)
            cv2.circle(record_img, (x, y), 8, (0, 255, 0), -1)
            cv2.putText(record_img, "GRUEN", (x + 10, max(20, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        # ===== Anzeigen =====
        cv2.imshow("main image", bgr_main)
        cv2.imshow("record view", record_img)

        # ===== Video speichern =====
        if cam.recording and cam.video_writer is not None:
            cam.video_writer.write(record_img)

        # Maskenfenster
        if cam.b_mask is not None:
            cv2.imshow("blue mask", cam.b_mask)
        if cam.o_mask is not None:
            cv2.imshow("orange mask", cam.o_mask)
        if cam.r_mask is not None:
            cv2.imshow("red mask", cam.r_mask)
        if cam.g_mask is not None:
            cv2.imshow("green mask", cam.g_mask)
        if cam.maskL is not None:
            cv2.imshow("wall left", cam.maskL)
        if cam.maskR is not None:
            cv2.imshow("wall right", cam.maskR)

        if cv2.waitKey(1) == ord("x"):
            break

    cam.stop()
    cv2.destroyAllWindows()