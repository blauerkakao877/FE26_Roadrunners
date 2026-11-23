# Testwerkzeuge und Fahrtauswertung

Hier beschreiben wir, wie wir neue Ideen offline testen und Fahrten auswerten.
Beim Schreiben einzelner Skripte haben wir Claude (KI-Assistent von Anthropic)
als Hilfswerkzeug genutzt, ähnlich wie eine Dokumentation oder ein Forum.
Ideen, Tests auf der Matte, Auswertung und Entscheidungen kommen von uns.

## 1. Testwerkzeuge und Analyse-Skripte

Eine unserer Regeln heißt **„Test new ideas early“**. Jede Testfahrt kostet
aber Zeit: Auto aufbauen, Hindernisse stellen, fahren, Logs holen. Deshalb
haben wir Werkzeuge gebaut, mit denen wir neue Ideen **offline gegen
Aufnahmen** testen können, statt jedes Mal neu zu fahren.

| Werkzeug | Was es macht |
|---|---|
| [`Hindernis_Mapping/Hindernis_Map.py`](src/FE_2026/Hindernis_Mapping/Hindernis_Map.py) | Ordnet jeden Pfeiler im Kamerabild einem von 6 Plätzen zu und erkennt über die Höhe im Bild 50 / 100 / 150 mm (Surprise Rule). |
| [`Hindernis_Mapping/test_mapping.py`](src/FE_2026/Hindernis_Mapping/test_mapping.py) | Prüft das Mapping an unseren Testfotos; muss „Alles OK.“ ausgeben. |
| [`Hindernis_Mapping/bild_pruefen.py`](src/FE_2026/Hindernis_Mapping/bild_pruefen.py) | Einzelne Bilder am PC prüfen: Farbe, Position, Platz. |
| [`Hindernis_Mapping/test_surprise_video.py`](src/FE_2026/Hindernis_Mapping/test_surprise_video.py) | Spielt echte Fahrvideos (`Videos/fahrt_*.avi`) durch dieselbe Erkennung wie auf dem Pi (`Work/Cam_moduls_contours.py`) und zählt falsche Farb-Flips. |

So sind wir vorgegangen:

- **Gleicher Code wie auf dem Auto.** `test_surprise_video.py` lädt das echte
  Kameramodul und ersetzt nur die Pi-Hardware (Kamera, LEDs) durch Platzhalter.
  Getestet wird also genau der Code, der später fährt.
- **Sonderfälle künstlich erzeugen.** Das Skript färbt grüne Pfeiler rot um und
  simuliert das Heranfahren durch Vergrößern des Bildes, bis die Spitze oben
  abgeschnitten ist. So prüfen wir Fälle, die auf der Matte selten vorkommen.
- **Klare Freigabe-Regel.** Die Surprise-Erkennung bleibt ausgeschaltet
  (`surprise_aktiv = False`), bis eine normale Fahrt mit der aktuellen Kamera
  „falsche Flips = 0“ zeigt. Geprüft haben wir das an 5163 Bildern.
- **Grenzen erkennen.** Beim Testen fiel auf, dass Videos von vor dem
  Kamera-Umbau (Horizont bei Zeile ~25 statt 53,5) nicht mehr aussagekräftig
  sind. Das steht jetzt direkt im Skript.

Details zum Ablauf: [`Hindernis_Mapping/README.md`](src/FE_2026/Hindernis_Mapping/README.md).

## 2. Fahrten auswerten

Bei jeder Fahrt entstehen drei Aufnahmen:

- das **Kamera-Video** (AVI) mit eingezeichneten Hindernissen und Linien,
- das **Pi-Log** mit genauem Zeitstempel in jeder Zeile,
- die **LiDAR-CSV** (10 Zeilen pro Sekunde, Start genau beim Startsignal).

Um einen Fahrfehler zu verstehen, muss man alle drei auf dieselbe Zeitachse
legen. Dafür nutzen wir **gemeinsame Zeitmarken**: Ereignisse,
die in allen drei Quellen sichtbar sind. Die beste Marke ist der **3-s-Stopp
nach drei Runden**:

- im Log steht „Runde Beendet“ mit Zeitstempel, die Stoppzeit ist im Code fest
  auf 3,0 s gesetzt,
- im LiDAR-CSV ändern sich die Abstände für diese Zeit nicht,
- im Video steht das Bild still.

**Erkenntnis:** Im Video dauert dieser Stopp nicht 3 s, sondern deutlich
kürzer. Die Pi-AVIs laufen also **nicht in Echtzeit**, sondern etwa um den
**Faktor 1,8–2** zu schnell. Der Grund: Der `VideoWriter` schreibt die Datei mit
festen 20 fps in den Header, der Pi liefert während der Fahrt aber weniger
Bilder pro Sekunde.

Was daraus folgt:

- Zeiten aus dem Video dürfen wir nicht direkt mit Log oder LiDAR vergleichen.
  Wir rechnen sie über die Zeitmarken um oder nehmen die Zeit aus dem Log.
- Reaktionszeiten und Geschwindigkeiten, die man „mit dem Auge“ aus dem Video
  schätzt, sind ohne Umrechnung falsch.
- Mit der Umrechnung lässt sich zu jedem Logeintrag das passende Videobild und
  die passende LiDAR-Zeile finden. So sehen wir, ob eine Strategie grundsätzlich
  nicht funktioniert oder nur feiner eingestellt werden muss (siehe
  *Reliability Tests* im [README](README.md#reliability-tests)).
