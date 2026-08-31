from picamera2 import Picamera2
import numpy as np
import Cam as C
import Led as L
import cv2
import time
import math
import libcamera


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

        self.line_height = 60 #die pixel von unten nach oben ausgewählt
        self.top_cut = 0 #die pixel von oben nach unten abgeschnitten

        self.frontcam = None
        self.backcam = None


# ================= INIT =================

    def init(self, mode="obstacle"):

        blob_params = cv2.SimpleBlobDetector_Params()
        blob_params.filterByArea = True
        blob_params.minArea = 50 #if mode == "open" else 200
        blob_params.maxArea = 100000
        #blob_params.blobColor = 0  # 0 = dunkle Blobs, 255 = helle Blobs

        hindernis_params = cv2.SimpleBlobDetector_Params()
        hindernis_params.filterByArea = True
        hindernis_params.minArea = 400
        hindernis_params.maxArea = 50000

        self.blob_detector = cv2.SimpleBlobDetector_create(blob_params)
        self.hindernis_detector = cv2.SimpleBlobDetector_create(hindernis_params)

        self.get_colorfilter_data()

        self.frontcam = C.Cam(1)
        self.frontcam.start()

        self.backcam = C.Cam(0)
        self.backcam.start()

        time.sleep(2.0)


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


# ================= COLORFILTER =================

    def get_colorfilter_data(self):

        with open("/home/pi/FE_2026/Data/Colorfilter.dat", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        values = []
        for line in lines:
            p = line.split(",")
            values.append((int(p[0]), int(p[1])))

        self.BL_hue,self.BU_hue = values[0]
        self.BL_sat,self.BU_sat = values[1]
        self.BL_val,self.BU_val = values[2]

        self.OL_hue,self.OU_hue = values[3]
        self.OL_sat,self.OU_sat = values[4]
        self.OL_val,self.OU_val = values[5]

        self.RL_hue,self.RU_hue = values[6]
        self.RL_sat,self.RU_sat = values[7]
        self.RL_val,self.RU_val = values[8]

        self.GL_hue,self.GU_hue = values[9]
        self.GL_sat,self.GU_sat = values[10]
        self.GL_val,self.GU_val = values[11]


# ================= LINIEN =================

    def finde_blau(self, hsv):
        lower = np.array([self.BL_hue, self.BL_sat, self.BL_val])
        upper = np.array([self.BU_hue, self.BU_sat, self.BU_val])

        # Maske erstellen
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.bitwise_not(mask)

        # 1-Pixel Border, damit Blobs am Rand erkannt werden
        self.b_mask = cv2.copyMakeBorder(mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        self.b_mask = cv2.medianBlur(self.b_mask, 5)

        # Blob Detection
        kp = self.blob_detector.detect(self.b_mask)

        # Debug-Ausgabe optional
        # print("Anzahl erkannter Blobs:", len(kp))
        # for i, k in enumerate(kp):
        #     print(f"Blob {i}: Größe = {k.size}, Mittelpunkt = {k.pt}")

        # True, wenn mindestens 1 Blob erkannt wurde
        return len(kp) > 0


    def finde_orange(self, hsv):
        lower = np.array([self.OL_hue, self.OL_sat, self.OL_val])
        upper = np.array([self.OU_hue, self.OU_sat, self.OU_val])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.bitwise_not(mask)

        self.o_mask = cv2.copyMakeBorder(mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        self.o_mask = cv2.medianBlur(self.o_mask, 5)

        kp = self.blob_detector.detect(self.o_mask)

        return len(kp) > 0


# ================= WÄNDE =================

    def wand_filter(self,bgr):

        lower = np.array([0,0,0])
        upper = np.array([120,90,90])

        return cv2.inRange(bgr,lower,upper)


    def waende(self,bgr):

        mask = self.wand_filter(bgr)

        self.maskL = mask[:,20:159]
        self.maskR = mask[:,160:300]

        histL = np.sum(self.maskL,axis=0)
        histR = np.sum(self.maskR,axis=0)

        maxHistL = np.max(histL)
        maxHistR = np.max(histR)

        kollL = maxHistL > 12000
        kollR = maxHistR > 12000

        return kollL,kollR,maxHistL,maxHistR


# ================= HINDERNISSE =================

    def finde_rot(self,hsv):

        lower1 = np.array([0,self.RL_sat,self.RL_val])
        upper1 = np.array([self.RL_hue,self.RU_sat,self.RU_val])

        lower2 = np.array([self.RU_hue,self.RL_sat,self.RL_val])
        upper2 = np.array([179,self.RU_sat,self.RU_val])

        mask = cv2.bitwise_or(
            cv2.inRange(hsv,lower1,upper1),
            cv2.inRange(hsv,lower2,upper2)
        )

        mask = cv2.bitwise_not(mask)

        self.r_mask = cv2.medianBlur(mask,5)

        kp = self.hindernis_detector.detect(self.r_mask)

        s_max=0; x=0; y=0

        for k in kp:
            if k.size > s_max:
                s_max = k.size
                x,y = k.pt

        return x,y,s_max


    def finde_gruen(self,hsv):

        lower = np.array([self.GL_hue,self.GL_sat,self.GL_val])
        upper = np.array([self.GU_hue,self.GU_sat,self.GU_val])

        mask = cv2.inRange(hsv,lower,upper)
        mask = cv2.bitwise_not(mask)

        self.g_mask = cv2.medianBlur(mask,5)

        kp = self.hindernis_detector.detect(self.g_mask)

        s_max=0; x=0; y=0

        for k in kp:
            if k.size > s_max:
                s_max = k.size
                x,y = k.pt

        return x,y,s_max


    def finde_hindernisse(self,hsv):

        rx,ry,rs = self.finde_rot(hsv)
        gx,gy,gs = self.finde_gruen(hsv)

        if rs > gs and rs > 0:
            return round(rx),round(ry),round(rs),"R"

        elif gs >= rs and gs > 0:
            return round(gx),round(gy),round(gs),"G"

        else:
            return 0,0,0,"N"


# ================= MAIN =================

if __name__ == "__main__":

    cam = CameraModules()
    cam.init("open")

    while True:

        hsv_full, hsv_main, bgr_main, hsv_line, bgr_line = cam.get_image()

        # Linien erkennen
        b_linie = cam.finde_blau(hsv_line)
        o_linie = cam.finde_orange(hsv_line)

        # Wände
        links, rechts, hellL, hellR = cam.waende(bgr_main)

        # Hindernisse
        x, y, s, farbe = cam.finde_hindernisse(hsv_main)

        # ===== Linien in main image einzeichnen =====
        if b_linie:
            cv2.line(bgr_main, (0, cam.line_height//2), (320, cam.line_height//2), (255,0,0), 2)
        if o_linie:
            cv2.line(bgr_main, (0, cam.line_height//2 + 2), (320, cam.line_height//2 + 2), (0,128,255), 2)

        # ===== Wände einzeichnen =====
        if links:
            cv2.line(bgr_main, (10,0), (10,bgr_main.shape[0]), (128,128,128), 2)
        if rechts:
            cv2.line(bgr_main, (310,0), (310,bgr_main.shape[0]), (128,128,128), 2)

        # ===== Hindernisse einzeichnen =====
        if farbe == "R":
            cv2.line(bgr_main, (x,0), (x,bgr_main.shape[0]), (0,0,255), 2)
        if farbe == "G":
            cv2.line(bgr_main, (x,0), (x,bgr_main.shape[0]), (0,255,0), 2)

        # ===== Anzeigen =====
        cv2.imshow("main image", bgr_main)

        # Maskenfenster optional
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
