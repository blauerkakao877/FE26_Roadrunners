# Test Tools and Run Analysis

We used Claude (AI assistant by Anthropic) as a helper tool while writing some scripts. Ideas, field tests and decisions are our own.

## Offline test tools

Following our rule "Test new ideas early", we test new ideas against recordings instead of driving again each time.
[`test_surprise_video.py`](src/FE_2026/Hindernis_Mapping/test_surprise_video.py) runs real drive videos through the same detection code as the car and counts wrong color flips. The Surprise Rule stays disabled until a run shows 0 wrong flips.
The obstacle mapping is checked with [`test_mapping.py`](src/FE_2026/Hindernis_Mapping/test_mapping.py), see the [Hindernis_Mapping README](src/FE_2026/Hindernis_Mapping/README.md).

## Aligning recordings

We align camera video, Pi log and LiDAR CSV using shared time marks, e.g. the 3 s stop after three rounds.
This showed that the Pi AVIs do not play in real time but about 1.8–2x too fast: the file is written at a fixed 20 fps while the Pi delivers fewer frames. Video times must therefore be converted using the time marks before comparing them with the log.
