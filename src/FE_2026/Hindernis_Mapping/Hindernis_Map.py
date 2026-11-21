"""Hindernis-Mapping ueber die Unterkante der Pfeiler.

Das Auto steht in der Ecke und schaut in die naechste Gerade. Jeder Pfeiler
steht auf einem von 6 Plaetzen (V/M/H x L/R, Kamerasicht). Der Platz wird aus
der Unterkante bestimmt (y = Abstand, x = Seite) - die Hoehe des Pfeilers
(gross/klein) spielt dadurch keine Rolle.

Erwartet wird das volle Frontkamerabild 320x240 (Cam.get_image(), ohne top_cut) -
so sind die Bilder in Bilder_hindernissposi aufgenommen.
"""
import cv2
import numpy as np

# Unterkante (x-Mitte, y) je Platz, gemessen aus FE_26/Bilder_hindernissposi.
# Neu kalibrieren, wenn Kamera/Halterung/Startposition geaendert wird.
PLAETZE = {
    "HL": (107, 62), "HR": (134, 62),
    "ML": (82, 66),  "MR": (121, 66),
    "VL": (14, 76),  "VR": (86, 77),
}
# Pixelhoehe eines normalen 100-mm-Pfeilers je Platz (gleiche Bilder).
# 50 mm misst ~0,55x, 150 mm ~1,5x davon -> Surprise-Rule-Pfeiler (Farbe vertauscht).
HOEHE_NORMAL = {"HL": 16, "HR": 15, "ML": 23, "MR": 23, "VL": 43, "VR": 45}
HOEHE_KLEIN, HOEHE_GROSS = 0.75, 1.25   # Verhaeltnis-Grenzen, Messwerte 0.51-0.57 / 1.44-1.53
BAND_Y = (50, 95)      # Crop: nur hier darf eine Unterkante liegen (darueber Hintergrund, darunter Linien)
MIN_FLAECHE = 20       # px^2, der kleine Pfeiler hinten hat ~50
Y_GEWICHT = 3          # H und M liegen nur 4 px auseinander -> y staerker gewichten
MAX_ABSTAND = 20       # weiter weg von jedem Platz -> kein Treffer
KANTE_ZEILEN = 5       # so viele Zeilen ueber der Unterkante bestimmen die x-Mitte

COLORFILTER = "/home/pi/FE_2026/Data/Colorfilter.dat"


def lade_farbfilter(pfad=COLORFILTER):
    """Rot/Gruen-Grenzen wie in CameraModules.get_colorfilter_data (Zeilen 7-12)."""
    f = {"R": [(10, 170), (80, 255), (80, 255)], "G": [(35, 85), (80, 255), (80, 255)]}
    try:
        with open(pfad) as fh:
            z = [l.strip() for l in fh if l.strip()]
        if len(z) >= 15:
            f["R"] = [tuple(map(int, z[i].split(","))) for i in (6, 7, 8)]
            f["G"] = [tuple(map(int, z[i].split(","))) for i in (9, 10, 11)]
    except OSError:
        pass  # Datei fehlt (z.B. am PC) -> Standardwerte
    return f


def _maske(hsv, farbe, f):
    (h0, h1), (s0, s1), (v0, v1) = f[farbe]
    if farbe == "G":
        return cv2.inRange(hsv, (h0, s0, v0), (h1, s1, v1))
    # Rot liegt an beiden Enden der Hue-Skala (wie finde_rot)
    return cv2.bitwise_or(cv2.inRange(hsv, (0, s0, v0), (h0, s1, v1)),
                          cv2.inRange(hsv, (h1, s0, v0), (179, s1, v1)))


def platz_von(x, y):
    """Naechster Platz zur Unterkante (x, y) oder None."""
    d = {p: np.hypot(x - px, (y - py) * Y_GEWICHT) for p, (px, py) in PLAETZE.items()}
    p = min(d, key=d.get)
    return p if d[p] <= MAX_ABSTAND else None


def finde_hindernisse(bgr, farbfilter=None):
    """Liefert Liste von Treffern {platz, farbe, x, y, hoehe, special} fuer ein Bild der Geraden.

    special = Pfeiler ist nicht 100 mm hoch -> Surprise Rule: nach der umgekehrten Farbe fahren.
    """
    f = farbfilter or lade_farbfilter()
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    treffer = []
    for farbe in "RG":
        m = cv2.medianBlur(_maske(hsv, farbe, f), 3)
        konturen, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for k in konturen:
            if cv2.contourArea(k) < MIN_FLAECHE:
                continue
            x, y, w, h = cv2.boundingRect(k)
            unten = y + h
            if not BAND_Y[0] <= unten <= BAND_Y[1]:
                continue
            # x nur aus den untersten Zeilen: oben kann der Pfeiler mit Hintergrund verschmelzen
            xs = np.nonzero(m[max(unten - KANTE_ZEILEN, y):unten, x:x + w])[1]
            xm = x + int(xs.mean())
            platz = platz_von(xm, unten)
            if platz:
                r = h / HOEHE_NORMAL[platz]
                hoehe = "K" if r < HOEHE_KLEIN else "G" if r > HOEHE_GROSS else "N"
                treffer.append({"platz": platz, "farbe": farbe, "x": xm, "y": unten,
                                "hoehe": hoehe, "special": hoehe != "N"})
    return treffer


class HindernisMap:
    """Karte aller 4 Geraden: gerade (0-3) -> {platz: farbe}."""

    def __init__(self):
        self.karte = [dict() for _ in range(4)]

    def eintragen(self, gerade, treffer):
        for t in treffer:
            self.karte[gerade % 4][t["platz"]] = t["farbe"]

    def farbe(self, gerade, platz):
        return self.karte[gerade % 4].get(platz, "-")

    def __str__(self):
        z = []
        for g in range(4):
            z.append(f"Gerade {g}:  L R")
            for reihe in "HMV":
                z.append(f"        {reihe}   {self.farbe(g, reihe + 'L')} {self.farbe(g, reihe + 'R')}")
        return "\n".join(z)


def zeichne(bgr, treffer):
    """Debug-Bild: Band, Referenzplaetze und Treffer."""
    img = bgr.copy()
    for y in BAND_Y:
        cv2.line(img, (0, y), (img.shape[1], y), (200, 200, 0), 1)
    for p, (px, py) in PLAETZE.items():
        cv2.circle(img, (px, py), 2, (255, 0, 0), -1)
    for t in treffer:
        c = (0, 0, 255) if t["farbe"] == "R" else (0, 160, 0)
        cv2.line(img, (t["x"] - 10, t["y"]), (t["x"] + 10, t["y"]), c, 2)
        cv2.putText(img, t["platz"] + t["farbe"], (t["x"] - 12, t["y"] + 18), 0, 0.5, c, 1)
    return img
