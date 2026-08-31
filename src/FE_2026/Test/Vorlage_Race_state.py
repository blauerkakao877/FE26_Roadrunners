"""Race-State Verwaltung für Openrace/Roadrunner.

Dieses Modul stellt eine klassenorientierte Grundlage bereit, um den
aktuellen Zustand des Rennens zentral zu verwalten.

- Vordefinierte Variablen wie `current_direction`, `line_counter`, usw.
- Erweiterbar durch benutzerdefinierte Variablen zur Laufzeit
- Klare Methoden zum Setzen/Lesen/Zurücksetzen
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Direction(str, Enum):
    """Mögliche Fahrtrichtungen bezogen auf gefundene Linienfarbe."""

    UNKNOWN = "unknown"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class RaceState:
    """Enthält den aktuellen Rennzustand des Fahrzeugs.

    Die Felder sind bewusst generisch gehalten und können bei Bedarf
    erweitert werden. Für zusätzliche, frei definierbare Werte steht
    das Feld `extra` zur Verfügung.
    """

    race_running: bool = False
    current_direction: Direction = Direction.UNKNOWN
    current_line_color: Optional[str] = None

    line_counter: int = 0
    lap_counter: int = 0

    speed: float = 0.25
    gyro_angle: float = 0.0
    gyro_total: float = 0.0

    last_line_timestamp: float = 0.0
    line_cooldown_s: float = 1.0

    extra: Dict[str, Any] = field(default_factory=dict)

    def reset(self) -> None:
        """Setzt den State auf sinnvolle Standardwerte zurück."""
        self.race_running = False
        self.current_direction = Direction.UNKNOWN
        self.current_line_color = None

        self.line_counter = 0
        self.lap_counter = 0

        self.speed = 0.25
        self.gyro_angle = 0.0
        self.gyro_total = 0.0

        self.last_line_timestamp = 0.0
        self.line_cooldown_s = 1.0

        self.extra.clear()

    def set_custom(self, key: str, value: Any) -> None:
        """Setzt eine benutzerdefinierte Variable in `extra`."""
        self.extra[key] = value

    def get_custom(self, key: str, default: Any = None) -> Any:
        """Liest eine benutzerdefinierte Variable aus `extra`."""
        return self.extra.get(key, default)

    def update_from_line_color(self, color: str) -> None:
        """Aktualisiert Richtung + zuletzt erkannte Linienfarbe.

        Mapping (anpassbar):
        - blau   -> LEFT
        - orange -> RIGHT
        """
        normalized = color.strip().lower()
        self.current_line_color = normalized

        if normalized == "blau":
            self.current_direction = Direction.LEFT
        elif normalized == "orange":
            self.current_direction = Direction.RIGHT
        else:
            self.current_direction = Direction.UNKNOWN


class RaceStateController:
    """Controller, der den RaceState kapselt und Komfortmethoden anbietet."""

    def __init__(self) -> None:
        self.state = RaceState()

    def start_race(self) -> None:
        self.state.race_running = True

    def stop_race(self) -> None:
        self.state.race_running = False

    def set_direction(self, direction: Direction) -> None:
        self.state.current_direction = direction

    def increment_line_counter(self) -> int:
        self.state.line_counter += 1
        return self.state.line_counter

    def set_speed(self, speed: float) -> None:
        self.state.speed = max(0.0, min(1.0, speed))

    def set_gyro(self, angle: float, total: float) -> None:
        self.state.gyro_angle = angle
        self.state.gyro_total = total

    def add_variable(self, name: str, value: Any) -> None:
        """Öffentliche API: weitere Variablen bequem hinzufügen."""
        self.state.set_custom(name, value)

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Öffentliche API: variable Werte lesen."""
        return self.state.get_custom(name, default)

    def snapshot(self) -> Dict[str, Any]:
        """Liefert ein leicht logbares Abbild des aktuellen States."""
        return {
            "race_running": self.state.race_running,
            "current_direction": self.state.current_direction.value,
            "current_line_color": self.state.current_line_color,
            "line_counter": self.state.line_counter,
            "lap_counter": self.state.lap_counter,
            "speed": self.state.speed,
            "gyro_angle": self.state.gyro_angle,
            "gyro_total": self.state.gyro_total,
            "last_line_timestamp": self.state.last_line_timestamp,
            "line_cooldown_s": self.state.line_cooldown_s,
            "extra": dict(self.state.extra),
        }


if __name__ == "__main__":
    # Kurzes Beispiel für standalone Test / Demo
    race = RaceStateController()
    race.start_race()
    race.set_speed(0.35)
    race.state.update_from_line_color("blau")
    race.increment_line_counter()

    # Eigene Variablen ergänzen:
    race.add_variable("wall_distance_left_cm", 38.2)
    race.add_variable("wall_distance_right_cm", 41.5)
    race.add_variable("target_laps", 3)

    print("Aktueller Race-State:")
    print(race.snapshot())
