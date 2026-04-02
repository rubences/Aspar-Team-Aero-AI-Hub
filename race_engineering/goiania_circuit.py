"""
goiania_circuit.py — Modelo geométrico y operativo del
Autódromo Internacional de Goiânia - Ayrton Senna.

Gran Premio de Brasil 2026 · Categoría Moto3
Datos basados en la homologación FIM Grado A (reasfaltado 2025).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TurnDirection(str, Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class CornerType(str, Enum):
    SLOW = "SLOW"        # < 80 km/h
    MEDIUM = "MEDIUM"   # 80–140 km/h
    FAST = "FAST"       # > 140 km/h


@dataclass(frozen=True)
class Corner:
    number: int
    direction: TurnDirection
    corner_type: CornerType
    entry_speed_kmh: float      # Velocidad estimada de entrada
    apex_speed_kmh: float       # Velocidad en el ápice
    exit_speed_kmh: float       # Velocidad de salida
    banking_deg: float          # Peralte (grados)
    length_m: float             # Longitud aproximada del arco
    lateral_g: float            # Carga lateral estimada (g)
    critical_tire_hombro: TurnDirection  # Flanco más solicitado


@dataclass(frozen=True)
class TrackSector:
    sector_id: int
    name: str
    length_m: float
    corners: List[Corner]
    max_speed_kmh: float
    overtaking_zone: bool


@dataclass(frozen=True)
class TrackEnvironment:
    ambient_temp_c: float = 26.0
    humidity_pct: float = 57.0
    wind_kmh: float = 6.0
    wind_direction_deg: float = 270.0   # Viento en dirección de la recta principal
    asphalt_temp_c: float = 48.0        # Estimado con pista negra nueva + sol directo
    track_condition: str = "NEW_DRY"    # Asfalto reasfaltado, poca goma depositada


@dataclass
class GoianiaCircuit:
    """
    Modelo completo del Autódromo Internacional de Goiânia.
    """
    name: str = "Autódromo Internacional de Goiânia - Ayrton Senna"
    country: str = "Brasil"
    city: str = "Goiânia, Goiás"
    total_length_m: float = 3835.0
    num_corners: int = 14
    right_corners: int = 9
    left_corners: int = 5
    main_straight_m: float = 994.0
    fim_homologation: str = "Grado A"
    surface: str = "Asfalto de alta densidad 2025 (reasfaltado)"

    # Variables ambientales proyectadas
    environment: TrackEnvironment = field(default_factory=TrackEnvironment)

    # Definición de curvas (datos basados en análisis de telemetría extrapolada
    # desde Buriram 2025 + layout publicado de Goiânia)
    corners: List[Corner] = field(default_factory=list)

    # Sectores
    sectors: List[TrackSector] = field(default_factory=list)

    def __post_init__(self):
        self.corners = self._build_corners()
        self.sectors = self._build_sectors()

    def _build_corners(self) -> List[Corner]:
        return [
            # ── Sector 1: Frenada tras recta principal ────────────────────────
            Corner(1,  TurnDirection.RIGHT, CornerType.MEDIUM,
                   entry_speed_kmh=238, apex_speed_kmh=95,  exit_speed_kmh=112,
                   banking_deg=2.5, length_m=62,  lateral_g=1.28,
                   critical_tire_hombro=TurnDirection.RIGHT),

            Corner(2,  TurnDirection.LEFT,  CornerType.SLOW,
                   entry_speed_kmh=110, apex_speed_kmh=72,  exit_speed_kmh=95,
                   banking_deg=0.0, length_m=38,  lateral_g=1.05,
                   critical_tire_hombro=TurnDirection.LEFT),

            # ── Sector 2: Chicane técnica ─────────────────────────────────────
            Corner(3,  TurnDirection.RIGHT, CornerType.SLOW,
                   entry_speed_kmh=118, apex_speed_kmh=65,  exit_speed_kmh=88,
                   banking_deg=1.0, length_m=45,  lateral_g=1.18,
                   critical_tire_hombro=TurnDirection.RIGHT),

            Corner(4,  TurnDirection.LEFT,  CornerType.SLOW,
                   entry_speed_kmh=90,  apex_speed_kmh=68,  exit_speed_kmh=92,
                   banking_deg=0.5, length_m=42,  lateral_g=1.12,
                   critical_tire_hombro=TurnDirection.LEFT),

            Corner(5,  TurnDirection.RIGHT, CornerType.MEDIUM,
                   entry_speed_kmh=132, apex_speed_kmh=108, exit_speed_kmh=125,
                   banking_deg=3.0, length_m=72,  lateral_g=1.32,
                   critical_tire_hombro=TurnDirection.RIGHT),

            # ── Sector 3: Curvas de alta carga derecha ────────────────────────
            Corner(6,  TurnDirection.RIGHT, CornerType.FAST,
                   entry_speed_kmh=165, apex_speed_kmh=148, exit_speed_kmh=158,
                   banking_deg=4.5, length_m=95,  lateral_g=1.55,
                   critical_tire_hombro=TurnDirection.RIGHT),

            Corner(7,  TurnDirection.RIGHT, CornerType.FAST,
                   entry_speed_kmh=158, apex_speed_kmh=142, exit_speed_kmh=155,
                   banking_deg=3.5, length_m=88,  lateral_g=1.48,
                   critical_tire_hombro=TurnDirection.RIGHT),

            Corner(8,  TurnDirection.LEFT,  CornerType.MEDIUM,
                   entry_speed_kmh=148, apex_speed_kmh=118, exit_speed_kmh=132,
                   banking_deg=1.5, length_m=58,  lateral_g=1.22,
                   critical_tire_hombro=TurnDirection.LEFT),

            # ── Sector 4: Sector mixto ────────────────────────────────────────
            Corner(9,  TurnDirection.RIGHT, CornerType.MEDIUM,
                   entry_speed_kmh=145, apex_speed_kmh=115, exit_speed_kmh=128,
                   banking_deg=2.0, length_m=55,  lateral_g=1.28,
                   critical_tire_hombro=TurnDirection.RIGHT),

            Corner(10, TurnDirection.LEFT,  CornerType.SLOW,
                   entry_speed_kmh=115, apex_speed_kmh=78,  exit_speed_kmh=98,
                   banking_deg=0.0, length_m=35,  lateral_g=1.08,
                   critical_tire_hombro=TurnDirection.LEFT),

            Corner(11, TurnDirection.RIGHT, CornerType.MEDIUM,
                   entry_speed_kmh=122, apex_speed_kmh=92,  exit_speed_kmh=115,
                   banking_deg=1.5, length_m=48,  lateral_g=1.18,
                   critical_tire_hombro=TurnDirection.RIGHT),

            Corner(12, TurnDirection.RIGHT, CornerType.FAST,
                   entry_speed_kmh=178, apex_speed_kmh=155, exit_speed_kmh=168,
                   banking_deg=5.0, length_m=112, lateral_g=1.62,
                   critical_tire_hombro=TurnDirection.RIGHT),

            # ── Sector 5: Penúltima horquilla + entrada recta ─────────────────
            Corner(13, TurnDirection.RIGHT, CornerType.SLOW,
                   entry_speed_kmh=132, apex_speed_kmh=82,  exit_speed_kmh=105,
                   banking_deg=2.5, length_m=52,  lateral_g=1.15,
                   critical_tire_hombro=TurnDirection.RIGHT),

            Corner(14, TurnDirection.LEFT,  CornerType.MEDIUM,
                   entry_speed_kmh=128, apex_speed_kmh=108, exit_speed_kmh=138,
                   banking_deg=2.0, length_m=65,  lateral_g=1.25,
                   critical_tire_hombro=TurnDirection.LEFT),
        ]

    def _build_sectors(self) -> List[TrackSector]:
        return [
            TrackSector(
                sector_id=1, name="Frenada Principal - T1/T2",
                length_m=780,
                corners=[self.corners[0], self.corners[1]],
                max_speed_kmh=238, overtaking_zone=True,
            ),
            TrackSector(
                sector_id=2, name="Chicane Técnica - T3 a T5",
                length_m=695,
                corners=self.corners[2:5],
                max_speed_kmh=165, overtaking_zone=False,
            ),
            TrackSector(
                sector_id=3, name="Curvas Rápidas Derechas - T6 a T8",
                length_m=820,
                corners=self.corners[5:8],
                max_speed_kmh=178, overtaking_zone=False,
            ),
            TrackSector(
                sector_id=4, name="Sector Mixto - T9 a T12",
                length_m=745,
                corners=self.corners[8:12],
                max_speed_kmh=178, overtaking_zone=False,
            ),
            TrackSector(
                sector_id=5, name="Última Horquilla + Recta - T13/T14",
                length_m=795,
                corners=self.corners[12:],
                max_speed_kmh=238, overtaking_zone=True,
            ),
        ]

    # ── Métricas derivadas ────────────────────────────────────────────────────

    @property
    def asymmetry_ratio(self) -> float:
        """Cociente de asimetría direccional (R/L)."""
        return round(self.right_corners / self.left_corners, 2)

    @property
    def estimated_lap_time_s(self) -> float:
        """Estimación de tiempo de vuelta base (sin rebufo) en segundos."""
        # Extrapolación desde Buriram 2025: 1:39.5 en 4.554 km
        # Escala proporcional: 3.835 km / 4.554 km * 99.5 s ≈ 83.8 s
        return round((3835.0 / 4554.0) * 99.5, 1)

    @property
    def race_distance_km(self) -> float:
        """Distancia total de carrera (24 vueltas)."""
        return round(self.total_length_m * 24 / 1000, 2)

    @property
    def thermal_severity_index(self) -> float:
        """
        Índice de severidad térmica asimétrica [0-10].
        Pondera asimetría directional, temperatura ambiente y longitud de curvas rápidas.
        """
        asym_factor = (self.right_corners / self.num_corners) * 3.5
        temp_factor = (self.environment.asphalt_temp_c - 30) / 5.0
        fast_corners = sum(1 for c in self.corners if c.corner_type == CornerType.FAST)
        fast_factor = fast_corners / self.num_corners * 3.0
        return round(min(asym_factor + temp_factor + fast_factor, 10.0), 2)

    def summary(self) -> dict:
        return {
            "circuit": self.name,
            "length_m": self.total_length_m,
            "corners": {
                "total": self.num_corners,
                "right": self.right_corners,
                "left": self.left_corners,
                "asymmetry_ratio": self.asymmetry_ratio,
            },
            "main_straight_m": self.main_straight_m,
            "race_distance_km": self.race_distance_km,
            "estimated_lap_time_s": self.estimated_lap_time_s,
            "thermal_severity_index": self.thermal_severity_index,
            "environment": {
                "ambient_temp_c": self.environment.ambient_temp_c,
                "asphalt_temp_c": self.environment.asphalt_temp_c,
                "humidity_pct": self.environment.humidity_pct,
                "wind_kmh": self.environment.wind_kmh,
            },
        }
