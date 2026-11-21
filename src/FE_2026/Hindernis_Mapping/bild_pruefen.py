"""Ein Bild rein -> Farbe und Position der Hindernisse raus.

Starten:  python bild_pruefen.py bild1.jpg [bild2.jpg ...]
Ohne Argument (z.B. Doppelklick): fragt nach dem Pfad, Bild einfach ins Fenster ziehen.
"""
import os, sys
import cv2
import Hindernis_Map as HM

FARBE = {"R": "Rot", "G": "Grün"}
REIHE = {"V": "vorne", "M": "mitte", "H": "hinten"}
SEITE = {"L": "links", "R": "rechts"}


def pruefe(pfad):
    pfad = pfad.strip().strip('"').strip("'")  # Drag & Drop setzt oft Anführungszeichen
    bgr = cv2.imread(pfad)
    if bgr is None:
        print(f"  Kann Bild nicht lesen: {pfad}")
        return
    treffer = HM.finde_hindernisse(bgr)
    print(os.path.basename(pfad) + ":")
    if not treffer:
        print("  kein Hindernis erkannt")
    for t in treffer:
        p = t["platz"]
        print(f"  {FARBE[t['farbe']]:5} {REIHE[p[0]]} {SEITE[p[1]]}")


if len(sys.argv) > 1:
    for p in sys.argv[1:]:
        pruefe(p)
else:
    while True:
        p = input("\nBild hier reinziehen oder Pfad eingeben (Enter = Ende): ")
        if not p.strip():
            break
        pruefe(p)
