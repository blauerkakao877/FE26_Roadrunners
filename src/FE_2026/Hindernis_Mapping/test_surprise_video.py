"""Prueft die Surprise-Rule-Erkennung aus Work/Cam_moduls_contours.py am PC.

Aufruf:
  python test_surprise_video.py                     -> nur Fotos + Sonderfaelle
  python test_surprise_video.py fahrt_XYZ.avi ...   -> zusaetzlich Fahrvideos abspielen

Fahrvideos: Videos vom Roboter (Videos/fahrt_*.avi) einer normalen Obstacle-Fahrt
MIT DER AKTUELLEN KAMERA. Dort gibt es nur 100-mm-Pfeiler -> Flips muessen 0 sein.
Erst dann in Cam_moduls_contours.py  surprise_aktiv = True  setzen.
(Videos vor dem Kamera-Umbau im Nov 2026 zaehlen nicht: Horizont lag dort ~25 statt 53.5.)
"""
import builtins, glob, os, sys, types, importlib.util
import cv2
import numpy as np

hier = os.path.dirname(os.path.abspath(__file__))
code = os.path.join(hier, "..")

for name in ("picamera2", "Cam", "Led", "libcamera"):   # Pi-Module am PC ersetzen
    m = types.ModuleType(name); m.Picamera2 = object; sys.modules[name] = m
sys.path.insert(0, os.path.join(code, "Work"))

spec = importlib.util.spec_from_file_location("cmc", os.path.join(code, "Work", "Cam_moduls_contours.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
lokal = os.path.join(code, "Data", "Colorfilter.dat")   # statt /home/pi/...
mod.open = lambda p, *a, **k: builtins.open(lokal if "Colorfilter" in p else p, *a, **k)
cam = mod.CameraModules(None)
cam.get_colorfilter_data()
cam.surprise_aktiv = True
fehler = 0


def check(ok, text):
    global fehler
    fehler += not ok
    print(("OK     " if ok else "FEHLER ") + text)


def erkenne(bgr):
    return cam.finde_hindernisse(cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[cam.top_cut:])


def frisch():
    cam.hoehe_latch = {"R": "N", "G": "N"}


def umfaerben(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    g = cv2.inRange(hsv, (35, 80, 80), (85, 255, 255)) > 0
    hsv[..., 0][g] = 176
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def naeher(bgr, z, x0):
    """Heranfahren simulieren: um den Horizontpunkt (x0, 53.5) vergroessern -> Spitze wandert oben raus."""
    M = np.float32([[z, 0, x0 * (1 - z)], [0, z, 53.5 * (1 - z)]])
    return cv2.warpAffine(bgr, M, (320, 240), borderValue=(255, 255, 255))


print("--- Fotos ---")
bilder = {os.path.basename(f)[:-4]: cv2.imread(f) for f in sorted(glob.glob(os.path.join(code, "..", "Bilder_hindernissposi", "HG*.jpg")))}
assert bilder, "keine Testfotos"
for name, bgr in bilder.items():
    for rot in (False, True):
        frisch()
        f = umfaerben if rot else (lambda b: b)
        if name == "HGVRG":
            # Spitze liegt im Fahrbild (top_cut) genau am Rand -> wie beim Heranfahren erst weiter weg sehen
            erkenne(f(naeher(bgr, 0.8, 86)))
        r = erkenne(f(bgr))
        sichtbar = "R" if rot else "G"
        hoehe = name[4:] or "N"
        if r[3] == "N":
            check(hoehe != "N" or name[2] in "HM", f"{name}{'_rot' if rot else ''} nicht gesehen (min_area) {r}")
            continue
        soll = sichtbar if hoehe == "N" else ("G" if sichtbar == "R" else "R")
        check(r[3] == soll and cam.special == (hoehe != "N"), f"{name}{'_rot' if rot else ''} {hoehe} -> {r} soll {soll}")

print("--- Sonderfaelle ---")
for z in (1.3, 1.6):
    frisch(); erkenne(bilder["HGVLG"])
    r = erkenne(naeher(bilder["HGVLG"], z, 14))
    check(r[3] == "R" and cam.special, f"150 mm naeher (x{z}), Spitze abgeschnitten -> bleibt umgedreht {r}")
frisch(); erkenne(bilder["HGVR"])
r = erkenne(naeher(bilder["HGVR"], 1.6, 86))
check(r[3] == "G" and not cam.special, f"100 mm, Spitze abgeschnitten -> bleibt normal {r}")
frisch(); erkenne(bilder["HGVLG"]); erkenne(np.full_like(bilder["HGVLG"], 255))
check(cam.hoehe_latch["G"] == "N", "Pfeiler weg -> Merker zurueckgesetzt")
for oben in (2, 25):
    b = bilder["HGVR"].copy()
    hsv = cv2.cvtColor(b, cv2.COLOR_BGR2HSV)
    b[oben:40, 78:96] = b[(hsv[..., 0] >= 35) & (hsv[..., 0] <= 85) & (hsv[..., 1] > 80)][0]
    frisch(); r = erkenne(b)
    check(r[3] == "G" and not cam.special, f"gruener Hintergrund ab y={oben} ueber 100 mm -> kein Flip {r}")

if len(sys.argv) > 1:
    print("--- Fahrvideos (nur 100-mm-Pfeiler erwartet) ---")
for f in sys.argv[1:]:
    cap = cv2.VideoCapture(f)
    ok, fr = cap.read()
    if not ok:
        check(False, f"{f}: nicht lesbar"); continue
    top = cam.top_cut
    cam.top_cut = 240 - fr.shape[0]           # Video = bgr_main mit damaligem top_cut
    frisch(); frames = gesehen = flips = 0
    while ok:
        # eingezeichnete senkrechte Hindernislinien (rot/gruen, volle Hoehe) entfernen
        hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        farbig = (hsv[..., 1] > 150) & ((hsv[..., 0] < 10) | (hsv[..., 0] > 170) | ((hsv[..., 0] > 50) & (hsv[..., 0] < 70)))
        for s in np.nonzero(farbig.mean(axis=0) > 0.8)[0]:
            fr[:, max(s - 3, 0):s + 4] = (128, 128, 128)
        r = cam.finde_hindernisse(cv2.cvtColor(fr, cv2.COLOR_BGR2HSV))
        frames += 1; gesehen += r[3] != "N"; flips += cam.special
        ok, fr = cap.read()
    cam.top_cut = top
    check(flips == 0, f"{os.path.basename(f)}: frames={frames} mit Pfeiler={gesehen} falsche Flips={flips}")

print("\nFEHLER: %d" % fehler if fehler else "\nAlles OK.")
sys.exit(1 if fehler else 0)
