"""Test: alle Bilder aus Bilder_hindernissposi durch das Mapping schicken.

Aufruf:  python test_mapping.py [Bilderordner]
Dateiname HG<Reihe><Seite>[G|K].jpg gibt die erwartete Position vor.
Debug-Bilder landen in ./debug/.
"""
import glob, os, sys
import cv2
import numpy as np
import Hindernis_Map as HM

hier = os.path.dirname(os.path.abspath(__file__))
ordner = sys.argv[1] if len(sys.argv) > 1 else os.path.join(hier, "..", "..", "Bilder_hindernissposi")
os.makedirs(os.path.join(hier, "debug"), exist_ok=True)
fehler = 0


def pruefe(name, bgr, soll):
    global fehler
    t = HM.finde_hindernisse(bgr)
    ist = sorted(x["platz"] + x["farbe"] for x in t)
    ok = ist == sorted(soll)
    if ok and len(name) <= 5:   # Einzelbild: Hoehe aus Dateiname (G/K/ohne)
        ok = [x["hoehe"] for x in t] == [name[4:] or "N"]
    fehler += not ok
    print(f"{'OK    ' if ok else 'FEHLER'} {name:22} soll={sorted(soll)} ist={ist} "
          f"kanten={[(x['x'], x['y']) for x in t]} hoehe={[x['hoehe'] for x in t]}")
    cv2.imwrite(os.path.join(hier, "debug", name + ".jpg"), HM.zeichne(bgr, t))
    return t


bilder = {os.path.basename(f)[:-4]: cv2.imread(f) for f in sorted(glob.glob(os.path.join(ordner, "HG*.jpg")))}
assert bilder, "keine HG*.jpg in " + ordner

print("--- Einzelbilder ---")
for name, bgr in bilder.items():
    pruefe(name, bgr, [name[2:4] + "G"])


def umfaerben(bgr):
    """Gruen -> Rot (Hue drehen), um die Rot-Erkennung ohne rote Testbilder zu pruefen."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    g = cv2.inRange(hsv, (35, 80, 80), (85, 255, 255)) > 0
    hsv[..., 0][g] = 176
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def kombi(a, b):
    """Pfeiler aus Bild b in Bild a kopieren (zwei Hindernisse in einer Geraden)."""
    hsv = cv2.cvtColor(b, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (0, 80, 80), (179, 255, 255))
    m[:HM.BAND_Y[0] - 45] = 0; m[HM.BAND_Y[1]:] = 0   # nur Pfeilerbereich, nicht orange Linie
    m = cv2.dilate(m, np.ones((3, 3), np.uint8)) > 0
    out = a.copy(); out[m] = b[m]
    return out


print("--- Rot (umgefaerbt) ---")
for name in ("HGVL", "HGMRK", "HGHLG"):
    pruefe(name + "_rot", umfaerben(bilder[name]), [name[2:4] + "R"])

print("--- Zwei Hindernisse (zusammenkopiert) ---")
pruefe("VL_G+HR_G", kombi(bilder["HGHR"], bilder["HGVL"]), ["VLG", "HRG"])
pruefe("VR_R+HL_G", kombi(bilder["HGHLK"], umfaerben(bilder["HGVRG"])), ["VRR", "HLG"])
pruefe("ML_G+HR_R", kombi(umfaerben(bilder["HGHR"]), bilder["HGML"]), ["MLG", "HRR"])

print("--- Karte ueber 4 Geraden ---")
karte = HM.HindernisMap()
for g, name in enumerate(("HGVL", "HGMR", "HGHLK", "HGVRG")):
    karte.eintragen(g, HM.finde_hindernisse(bilder[name]))
karte.eintragen(1, HM.finde_hindernisse(umfaerben(bilder["HGHL"])))
print(karte)
assert karte.karte == [{"VL": "G"}, {"MR": "G", "HL": "R"}, {"HL": "G"}, {"VR": "G"}], karte.karte

print("\nFEHLER:" if fehler else "\nAlles OK.", fehler or "")
sys.exit(1 if fehler else 0)
