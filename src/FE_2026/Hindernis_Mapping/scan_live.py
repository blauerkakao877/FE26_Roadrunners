"""Live-Test auf dem Roboter: Frontkamera -> Hindernis-Mapping mit Hoehe/Special.

Starten (auf dem Pi, mit Bildschirm/VNC):  python scan_live.py
Taste s = Bild speichern (fuer neue Testbilder), x = Ende.

Nimmt das volle Kamerabild 320x240 (ohne top_cut) - so wurden die Referenzbilder
in Bilder_hindernissposi aufgenommen. Mit beschnittenem Bild stimmen die Plaetze nicht.
"""
import os, sys, time
import cv2

sys.path.insert(0, "/home/pi/FE_2026/Work")   # Cam.py liegt dort
from Cam import Cam
import Hindernis_Map as HM

ORDNER = "/home/pi/FE_2026/Bilder"

farbfilter = HM.lade_farbfilter()
cam = Cam(1)   # 1 = Frontkamera (wie Cam_Write_Images.py)
cam.start()
os.makedirs(ORDNER, exist_ok=True)
letzte = None
try:
    while True:
        bgr = cam.get_image()
        treffer = HM.finde_hindernisse(bgr, farbfilter)
        text = sorted(f"{t['platz']}{t['farbe']}{'*' if t['special'] else ''}" for t in treffer)
        if text != letzte:   # nur bei Aenderung ausgeben, * = Special (Surprise Rule)
            print(text)
            letzte = text
        cv2.imshow("Scan", cv2.resize(HM.zeichne(bgr, treffer), (640, 480), interpolation=cv2.INTER_NEAREST))
        key = cv2.waitKey(1) & 0xFF
        if key == ord("x"):
            break
        if key == ord("s"):
            name = os.path.join(ORDNER, time.strftime("scan_%Y-%m-%d_%H-%M-%S.jpg"))
            cv2.imwrite(name, bgr)
            print("gespeichert:", name)
finally:
    cam.stop()
    cv2.destroyAllWindows()
