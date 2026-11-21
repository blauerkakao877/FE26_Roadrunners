# Hindernis-Mapping (Scan-Runde + Surprise Rule)

Stand 2026-11-17. Noch **nicht** in `Roadrunner2.py` eingebaut.

Das Auto steht in der Ecke und schaut in die nächste Gerade. Jeder Pfeiler wird
über seine **Unterkante** einem von 6 Plätzen zugeordnet (V/M/H × L/R). Über seine
**Höhe** im Bild wird erkannt, ob er 50 / 100 / 150 mm hoch ist; nicht 100 mm
= `special` (Surprise Rule: nach der umgekehrten Farbe vorbeifahren).

## Dateien

| Datei | Wo | Zweck |
|---|---|---|
| `Hindernis_Map.py` | PC + Pi | Kern: `finde_hindernisse(bgr)` → `[{platz, farbe, x, y, hoehe, special}]`, `HindernisMap` (Karte der 4 Geraden), `zeichne()` |
| `scan_live.py` | Pi | Live-Kamerabild mit Treffern; `s` speichert Bild, `x` beendet |
| `bild_pruefen.py` | PC | Einzelne Bilder reinziehen → Farbe/Position |
| `test_mapping.py` | PC | Test mit `FE_26/Bilder_hindernissposi` (muss „Alles OK." ausgeben) |

Abhängigkeiten: `opencv`, `numpy`; auf dem Pi zusätzlich `Work/Cam.py` und
`Data/Colorfilter.dat` (am PC werden Standard-Farbgrenzen benutzt).

## Auf den Roboter

Ordner nach `/home/pi/FE_2026/Hindernis_Mapping/` kopieren, dort
`python scan_live.py` starten.

## Surprise Rule beim Fahren (eingebaut, Schalter AUS)

`Work/Cam_moduls_contours.py` erkennt die Höhe auch beim Fahren und dreht
dann die Farbe um (`surprise_aktiv`, Standard **False** = alles wie vorher,
an 5163 Bildern geprüft). Ist die Spitze abgeschnitten, gilt die zuletzt
sicher gemessene Höhe. Alte Fahrvideos (vor dem Kamera-Umbau) sind dafür
**nicht** aussagekräftig.

Freischalten:
1. Normale Obstacle-Fahrt mit aktueller Kamera fahren (Video landet in
   `Videos/fahrt_*.avi`), ideal je einmal links und rechts.
2. `python test_surprise_video.py <video.avi> ...` → muss „falsche Flips=0“
   und „Alles OK.“ zeigen.
3. Fahrt mit echtem 50- und 150-mm-Pfeiler: im Log muss
   „Surprise-Pfeiler“ stehen und das Auto richtig vorbeifahren.
4. Erst dann `self.surprise_aktiv = True` setzen (vor der Check Time!).

Sicherung des Stands davor: `Code/Work_save_vor_surprise/`.

**Kamera-Check (30 s):** `scan_live.py` starten, 50-mm-Pfeiler vor das Auto
stellen. Seine Oberkante muss etwa auf Zeile 53 liegen (Horizont der
Testfotos). Liegt sie deutlich anders, ist die Kamera anders geneigt als
beim Fotografieren → Plätze und Höhen neu messen.

## Wichtig

- Bild = **volles** Frontkamerabild 320×240 (`Cam.get_image()`), **kein**
  `top_cut`. Mit dem beschnittenen `bgr_main` aus `Cam_moduls_contours`
  (`top_cut=8`) verschieben sich alle Plätze.
- Plätze (`PLAETZE`) und Normalhöhen (`HOEHE_NORMAL`) neu messen, wenn
  Kamera, Halterung oder Scan-Position geändert wird. Neue Bilder als
  `HG<Reihe><Seite>[G|K].jpg` speichern und `test_mapping.py` laufen lassen.
- Nur die Blickrichtung aus den Testbildern ist gemessen; Gegenrichtung und
  echte rote Pfeiler fehlen noch.
