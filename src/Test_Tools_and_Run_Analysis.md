# Test Tools and Run Analysis

We used Claude (AI assistant by Anthropic) only as a supporting tool: for tests and simulation, and to check our code for errors. Ideas, field tests and decisions are our own.

## Offline test tools

One of our rules is "Test new ideas early". But every test drive takes time: set up the car, place the obstacles, drive, collect the logs. So we built tools that test new ideas **offline against recordings** instead of driving again each time.

| Tool | Purpose |
|---|---|
| [`Hindernis_Map.py`](FE_2026/Hindernis_Mapping/Hindernis_Map.py) | Assigns each pillar in the camera image to one of 6 positions and detects its height (50 / 100 / 150 mm) for the Surprise Rule. |
| [`test_mapping.py`](FE_2026/Hindernis_Mapping/test_mapping.py) | Checks the mapping against our test photos; must print "Alles OK.". |
| [`test_surprise_video.py`](FE_2026/Hindernis_Mapping/test_surprise_video.py) | Runs real drive videos through the same detection code as the car and counts wrong color flips. |

- **Same code as on the car.** The video test loads the real camera module and only replaces the Pi hardware with stubs.
- **Simulated edge cases.** Green pillars are recolored red, and approaching a pillar is simulated by zooming in until its top is cut off.
- **Clear release rule.** The Surprise Rule stays disabled until a normal run with the current camera shows 0 wrong flips (checked on 5163 frames).

Details: [Hindernis_Mapping README](FE_2026/Hindernis_Mapping/README.md).

## Aligning recordings

Each run produces three recordings: the camera video (AVI with detected obstacles drawn in), the Pi log (precise timestamp in every line) and the LiDAR CSV (10 lines per second, starting at the start signal).

To understand a driving error, we put all three on one time axis using shared time marks, i.e. events visible in all sources. The best mark is the **3 s stop after three rounds**: the log shows "Runde Beendet", the LiDAR distances stay constant, and the video image stands still.

**Finding:** In the video this stop lasts clearly less than 3 s. The Pi AVIs do not play in real time but about **1.8–2x too fast**: the file is written with a fixed 20 fps, while the Pi delivers fewer frames per second while driving.

So video times must be converted using the time marks before comparing them with the log or LiDAR data. Speeds or reaction times estimated by eye from the video are wrong otherwise.
