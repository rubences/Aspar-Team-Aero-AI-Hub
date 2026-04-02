"""
tire_strategy.py — Estrategia termodinámica de neumáticos Pirelli para Moto3.

Modela las ventanas operativas de los compuestos SC1/SC2, la asimetría térmica
del Autódromo de Goiânia y los algoritmos de selección de presiones en frío.

Gran Premio de Brasil 2026 — Goiânia
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class TireCompound(str, Enum):
    SC1 = "SC1"   # Blando
    SC2 = "SC2"   # Medio


class TirePosition(str, Enum):
    FRONT = "FRONT"
    REAR  = "REAR"


class TireState(str, Enum):
    NEW  = "NEW"
    USED = "USED"


# ── Propiedades físicas de los compuestos Pirelli Moto3 2026 ─────────────────

@dataclass(frozen=True)
class CompoundProfile:
    compound: TireCompound
    position: TirePosition
    # Ventana operativa de temperatura de la banda de rodadura (°C)
    temp_window_min_c: float
    temp_window_max_c: float
    # Temperatura de transición vítrea (below → pierde adherencia abruptamente)
    glass_transition_c: float
    # Temperatura de ampollas (thermal blistering onset)
    blistering_onset_c: float
    # Presión mínima reglamentaria (bares)
    pressure_min_bar: float
    # Rango de presión recomendado en caliente (bares)
    pressure_hot_min_bar: float
    pressure_hot_max_bar: float
    # Coeficiente de fricción máximo (normalizado 0–1)
    peak_grip_coefficient: float
    # Temperatura del calentador de neumáticos recomendada (°C)
    warmer_temp_c: float
    # Durabilidad relativa bajo asfalto abrasivo nuevo [0–10]
    abrasion_resistance: float


COMPOUND_PROFILES: Dict[Tuple[TireCompound, TirePosition], CompoundProfile] = {
    (TireCompound.SC1, TirePosition.FRONT): CompoundProfile(
        compound=TireCompound.SC1, position=TirePosition.FRONT,
        temp_window_min_c=70.0,  temp_window_max_c=105.0,
        glass_transition_c=55.0, blistering_onset_c=108.0,
        pressure_min_bar=1.65,
        pressure_hot_min_bar=1.80, pressure_hot_max_bar=2.10,
        peak_grip_coefficient=1.0,
        warmer_temp_c=90.0,
        abrasion_resistance=6.5,
    ),
    (TireCompound.SC2, TirePosition.FRONT): CompoundProfile(
        compound=TireCompound.SC2, position=TirePosition.FRONT,
        temp_window_min_c=50.0,  temp_window_max_c=98.0,
        glass_transition_c=38.0, blistering_onset_c=115.0,
        pressure_min_bar=1.65,
        pressure_hot_min_bar=1.80, pressure_hot_max_bar=2.10,
        peak_grip_coefficient=0.92,
        warmer_temp_c=90.0,
        abrasion_resistance=8.8,
    ),
    (TireCompound.SC1, TirePosition.REAR): CompoundProfile(
        compound=TireCompound.SC1, position=TirePosition.REAR,
        temp_window_min_c=75.0,  temp_window_max_c=110.0,
        glass_transition_c=58.0, blistering_onset_c=112.0,
        pressure_min_bar=1.65,
        pressure_hot_min_bar=1.50, pressure_hot_max_bar=1.75,
        peak_grip_coefficient=1.0,
        warmer_temp_c=90.0,
        abrasion_resistance=6.0,
    ),
    (TireCompound.SC2, TirePosition.REAR): CompoundProfile(
        compound=TireCompound.SC2, position=TirePosition.REAR,
        temp_window_min_c=55.0,  temp_window_max_c=100.0,
        glass_transition_c=42.0, blistering_onset_c=118.0,
        pressure_min_bar=1.65,
        pressure_hot_min_bar=1.50, pressure_hot_max_bar=1.75,
        peak_grip_coefficient=0.90,
        warmer_temp_c=90.0,
        abrasion_resistance=8.5,
    ),
}


# ── Asignación reglamentaria de neumáticos — GP Brasil 2026 ──────────────────

@dataclass
class TireAllocation:
    """
    Asignación ampliada de 19 neumáticos para el evento de Goiânia
    (10 minutos adicionales por la novedad del trazado).
    """
    total_slicks: int = 19
    front_slicks: int = 9
    rear_slicks: int  = 10

    # Desglose por compuesto (a confirmar con Pirelli antes del evento)
    front_sc1: int = 4
    front_sc2: int = 5
    rear_sc1:  int = 6
    rear_sc2:  int = 4

    def validate(self) -> bool:
        return (self.front_sc1 + self.front_sc2 == self.front_slicks and
                self.rear_sc1  + self.rear_sc2  == self.rear_slicks)


# ── Motor de estrategia termodinámica ─────────────────────────────────────────

class TireStrategyEngine:
    """
    Calcula presiones en frío óptimas, evalúa riesgos de degradación
    térmica asimétrica y genera recomendaciones de compuestos por sesión.
    """

    def __init__(self, allocation: TireAllocation | None = None):
        self.allocation = allocation or TireAllocation()
        self.profiles   = COMPOUND_PROFILES

    # ── Presión en frío ────────────────────────────────────────────────────

    def cold_pressure_target(
        self,
        compound: TireCompound,
        position: TirePosition,
        ambient_temp_c: float,
        asphalt_temp_c: float,
    ) -> dict:
        """
        Calcula la presión en frío (garage) necesaria para alcanzar la presión
        caliente objetivo en pista, usando un modelo termoquímico simplificado.

        ΔP ≈ P_cold × (ΔT / T_cold_K) × β_tire

        donde β_tire ≈ 0.85 (factor empírico de respuesta de presión de Pirelli slick).
        """
        profile = self.profiles[(compound, position)]

        # Temperatura realista del neumático al salir del box tras calentador.
        carcass_start_c = max(ambient_temp_c + 20, profile.warmer_temp_c - 10)
        T_cold_K = 273.15 + carcass_start_c

        # Incremento térmico adicional esperado ya en pista abierta.
        delta_T = max(asphalt_temp_c + 18 - carcass_start_c, 12)
        beta = 0.85

        # Objetivo nominal del fabricante y objetivo operativo compatible con reglamento.
        nominal_hot_target = (profile.pressure_hot_min_bar + profile.pressure_hot_max_bar) / 2.0
        operational_hot_target = (
            max(nominal_hot_target, profile.pressure_min_bar)
            if position == TirePosition.REAR
            else nominal_hot_target
        )

        theoretical_cold_pressure = operational_hot_target / (1 + beta * delta_T / T_cold_K)
        recommended_cold_pressure = theoretical_cold_pressure
        if position == TirePosition.REAR:
            recommended_cold_pressure = max(theoretical_cold_pressure, profile.pressure_min_bar - 0.10)

        return {
            "compound": compound,
            "position": position,
            "ambient_temp_c": ambient_temp_c,
            "asphalt_temp_c": asphalt_temp_c,
            "carcass_start_temp_c": round(carcass_start_c, 1),
            "theoretical_cold_pressure_bar": round(theoretical_cold_pressure, 2),
            "cold_pressure_bar": round(recommended_cold_pressure, 2),
            "nominal_hot_target_bar": round(nominal_hot_target, 2),
            "hot_target_bar": round(operational_hot_target, 2),
            "regulatory_min_bar": profile.pressure_min_bar,
            "compliant": operational_hot_target >= profile.pressure_min_bar,
        }

    # ── Riesgo de ampollas asimétrico ──────────────────────────────────────

    def asymmetric_thermal_risk(
        self,
        compound: TireCompound,
        asphalt_temp_c: float,
        right_corner_count: int = 9,
        total_corners: int = 14,
    ) -> dict:
        """
        Evalúa el riesgo de thermal blistering en el hombro derecho del neumático
        trasero dada la proporción de curvas a la derecha.

        Modelo: La temperatura del hombro derecho escala proporcionalmente a la
        fracción de curvas derechas × temperatura del asfalto × factor de carga lateral.
        """
        profile         = self.profiles[(compound, TirePosition.REAR)]
        right_fraction  = right_corner_count / total_corners
        lateral_g_mean  = 1.35           # Media de g laterales en curvas derechas de Goiânia
        heat_multiplier = 1.0 + (right_fraction - 0.5) * 0.8 * lateral_g_mean

        # Temperatura estimada hombro derecho
        right_shoulder_temp = asphalt_temp_c * heat_multiplier + 22  # +22°C por fricción base

        # Temperatura estimada hombro izquierdo (se enfría en recta larga)
        straight_cooling_factor = 0.72  # recta de 994 m → fuerte convección
        left_shoulder_temp = right_shoulder_temp * straight_cooling_factor

        blistering_risk_right = (right_shoulder_temp >= profile.blistering_onset_c)
        cold_snap_risk_left   = (left_shoulder_temp  <= profile.glass_transition_c + 5)

        return {
            "compound":                    compound,
            "right_shoulder_temp_est_c":   round(right_shoulder_temp, 1),
            "left_shoulder_temp_est_c":    round(left_shoulder_temp, 1),
            "blistering_onset_c":          profile.blistering_onset_c,
            "glass_transition_c":          profile.glass_transition_c,
            "right_blistering_risk":       blistering_risk_right,
            "left_cold_snap_risk":         cold_snap_risk_left,
            "severity": (
                "CRÍTICO: ampollas inminentes en hombro derecho"
                if blistering_risk_right else
                "MODERADO: hombro derecho cerca del límite superior"
                if right_shoulder_temp >= profile.blistering_onset_c - 5 else
                "NOMINAL"
            ),
            "management_action": (
                "Reducir presiones traseras en 0.05 bar y evaluar SC1 en rueda trasera"
                if blistering_risk_right else
                "Mantener presión objetivo. Monitorear IR en cada box stop."
            ),
        }

    # ── Selección de compuesto por sesión ──────────────────────────────────

    def session_compound_recommendation(
        self,
        session: str,
        asphalt_temp_c: float,
        tire_state: TireState = TireState.NEW,
    ) -> dict:
        """
        Genera la recomendación de compuesto delantero/trasero para una sesión.
        Lógica derivada del informe técnico Goiânia 2026.
        """
        rec = {
            "FP1_RUN1":    (TireCompound.SC2, TireCompound.SC2, "Shakedown en asfalto verde"),
            "FP1_RUN2":    (TireCompound.SC2, TireCompound.SC2, "Verificación de gearing"),
            "FP1_RUN3":    (TireCompound.SC2, TireCompound.SC2, "Evaluación anti-squat base"),
            "PRACTICE_RUN1": (TireCompound.SC2, TireCompound.SC1, "Evaluación térmica alta (SC1 trasero)"),
            "PRACTICE_RUN2": (TireCompound.SC2, TireCompound.SC1, "Termometría IR post-tanda"),
            "PRACTICE_RUN3": (TireCompound.SC1, TireCompound.SC1, "Time attack — ambos blandos"),
            "FP2_RUN1":    (TireCompound.SC2, TireCompound.SC1, "Simulación de carrera — peso máximo"),
            "FP2_RUN2":    (TireCompound.SC2, TireCompound.SC1, "Continuación larga tanda"),
            "Q2_RUN1":     (TireCompound.SC1, TireCompound.SC1, "Primer intento clasificación"),
            "Q2_RUN2":     (TireCompound.SC1, TireCompound.SC1, "Segundo intento (quick swap)"),
            "RACE":        (TireCompound.SC2, TireCompound.SC1, "SC2 delantero / SC1 trasero — 24 vueltas"),
        }.get(session, (TireCompound.SC2, TireCompound.SC2, "Sesión no especificada"))

        front_compound, rear_compound, rationale = rec

        # Ajuste de emergencia: si el asfalto supera 52°C, recomendar SC1 obligatorio detrás
        if asphalt_temp_c > 52 and rear_compound == TireCompound.SC2:
            rear_compound = TireCompound.SC1
            rationale += " [AJUSTE: asfalto >52°C → SC1 trasero obligatorio]"

        return {
            "session":         session,
            "front_compound":  front_compound,
            "rear_compound":   rear_compound,
            "rationale":       rationale,
            "front_pressure":  self.cold_pressure_target(front_compound, TirePosition.FRONT,
                                                          26.0, asphalt_temp_c),
            "rear_pressure":   self.cold_pressure_target(rear_compound,  TirePosition.REAR,
                                                          26.0, asphalt_temp_c),
            "thermal_risk":    self.asymmetric_thermal_risk(rear_compound, asphalt_temp_c),
        }

    # ── Estrategia de carrera ──────────────────────────────────────────────

    def race_strategy(self, asphalt_temp_c: float = 48.0) -> dict:
        """
        Estrategia definitiva de carrera con análisis de viabilidad termodinámica
        para los 24 giros y 92.04 km del GP de Brasil 2026.
        """
        front_profile  = self.profiles[(TireCompound.SC2, TirePosition.FRONT)]
        rear_profile   = self.profiles[(TireCompound.SC1, TirePosition.REAR)]

        # Estimación de vida térmica del neumático trasero SC1
        # Cada vuelta degrada el hombro derecho ~0.4°C neto sobre la ventana óptima
        # Límite crítico → ~20 vueltas antes de que el hombro alcance blistering
        rear_thermal_limit_laps = max(0, int((rear_profile.blistering_onset_c -
                                               (asphalt_temp_c * 1.42 + 22)) / 0.4))

        viable = rear_thermal_limit_laps >= 24

        return {
            "race_laps":           24,
            "race_distance_km":    92.04,
            "front_compound":      TireCompound.SC2,
            "rear_compound":       TireCompound.SC1,
            "front_pressure_grid_bar": 1.80,
            "rear_pressure_grid_bar":  1.65,
            "rear_thermal_limit_laps": rear_thermal_limit_laps,
            "race_viable":         viable,
            "anti_squat_requirement": (
                "108%–112% OBLIGATORIO para proteger hombro derecho SC1 "
                "bajo cargas de tracción en curvas rápidas derechas"
            ),
            "throttle_management": (
                "Modular apertura de gas <80% durante vueltas 1-10 para "
                "estabilizar histeresis térmica del flanco derecho"
                if not viable else
                "Ritmo libre desde vuelta 1. Monitorear IR cada parada en boxes."
            ),
            "risk_flags": [
                "SC1 trasero vulnerable a blistering >lap 20 si asfalto supera 52°C",
                "SC2 delantero: verificar carcasa tras T1 en cada vuelta (desaceleración 1.42g)",
                "Asimetría 9:5 R/L → gradiente térmico lateral >40°C posible al final de carrera",
            ] if not viable else [
                "SC1 trasero dentro de ventana operativa para 24 vueltas",
                "Mantener presión trasera ≥1.65 bar (límite reglamentario)",
            ],
        }
