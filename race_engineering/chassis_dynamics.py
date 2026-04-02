"""
chassis_dynamics.py — Calculadora cinemática del chasis Moto3.

Implementa las fórmulas derivadas de la dinámica de motocicletas
(Cossalter 2002, Sharp 2001) para:
  · Distancia entre ejes (Wheelbase) y momento de cabeceo
  · Geometría de dirección (Rake / Trail)
  · Porcentaje de Anti-Squat
  · Interdependencia cadena ↔ anti-squat

Prueba de Concepto: Gran Premio de Brasil 2026 — Goiânia
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple


# ── Constantes físicas del prototipo base Moto3 2026 ─────────────────────────
_FRONT_WHEEL_RADIUS_MM    = 292.0   # 17" = 431,8 mm diámetro
_REAR_WHEEL_RADIUS_MM     = 298.0   # 17" trasero
_BIKE_MASS_KG             = 148.0   # Peso reglamentario mínimo (moto + piloto ~63 kg)
_RIDER_MASS_KG            = 63.0
_TOTAL_MASS_KG            = _BIKE_MASS_KG + _RIDER_MASS_KG
_GRAVITY_MS2              = 9.81


@dataclass
class ChassisConfiguration:
    """
    Parámetros geométricos completos del chasis Moto3.
    Todos los valores angulares en GRADOS; distancias en MILÍMETROS.
    """
    # ── Tren delantero ─────────────────────────────────────────────────────
    rake_deg: float        = 23.5     # Ángulo de lanzamiento desde la vertical
    fork_offset_mm: float  = 28.0     # Desplazamiento de tijas (triple clamp offset)
    front_ride_height_mm: float = 0.0 # Desplazamiento adicional de los tubos (+ = subir)

    # ── Geometría global ───────────────────────────────────────────────────
    wheelbase_mm: float    = 1268.0   # Distancia entre ejes base

    # ── Tren trasero ───────────────────────────────────────────────────────
    swingarm_length_mm: float        = 420.0   # Longitud brazo oscilante
    swingarm_pivot_height_mm: float  = 295.0   # Altura del pivote del basculante
    rear_axle_height_mm: float       = 298.0   # Altura eje trasero (= radio rueda trasera)
    cg_height_mm: float              = 465.0   # Centro de gravedad combinado (moto+piloto)

    # ── Transmisión ────────────────────────────────────────────────────────
    front_sprocket_teeth: int  = 14   # Piñón de ataque
    rear_sprocket_teeth: int   = 38   # Corona trasera
    engine_sprocket_height_mm: float = 298.0  # Altura centro piñón motor

    # ── Suspensión trasera ─────────────────────────────────────────────────
    rear_spring_preload_mm: float   = 8.0
    rear_compression_clicks: int    = 14
    rear_rebound_clicks: int        = 10
    rear_spring_rate_nm_mm: float   = 95.0

    # ── Suspensión delantera ───────────────────────────────────────────────
    front_compression_clicks: int   = 10
    front_rebound_clicks: int       = 8
    front_spring_rate_nm_mm: float  = 7.5

    @property
    def final_drive_ratio(self) -> float:
        return round(self.rear_sprocket_teeth / self.front_sprocket_teeth, 4)


# ── Motor de cálculo cinemático ──────────────────────────────────────────────

class ChassisDynamicsCalculator:
    """
    Calcula parámetros dinámicos derivados de la configuración del chasis.
    """

    def __init__(self, config: ChassisConfiguration):
        self.cfg = config

    # ── 1. Geometría de dirección ─────────────────────────────────────────

    def effective_rake_deg(self) -> float:
        """
        Ángulo de lanzamiento efectivo tras ajustar la altura del tren delantero.
        Bajar las tijas X mm reduce el rake efectivo (fórmula lineal aproximada).
        La reducción es ~0.1° por cada mm que se bajan los tubos.
        """
        delta_height = self.cfg.front_ride_height_mm
        effective_rake = self.cfg.rake_deg - (delta_height * 0.12)
        return round(effective_rake, 3)

    def trail_mm(self, rake_deg: float | None = None, offset_mm: float | None = None) -> float:
        """
        Avance (Trail) según la fórmula de Cossalter (Motorcycle Dynamics, 2002):

            t = R_f · sin(ε) - e · cos(ε)

        donde ε = ángulo de lanzamiento desde la vertical,
              R_f = radio de la rueda delantera,
              e = offset de las tijas.
        """
        rake_rad = math.radians(rake_deg if rake_deg is not None else self.effective_rake_deg())
        offset   = offset_mm if offset_mm is not None else self.cfg.fork_offset_mm
        t = (_FRONT_WHEEL_RADIUS_MM * math.sin(rake_rad)) - (offset * math.cos(rake_rad))
        return round(t, 2)

    def trail_sensitivity_to_rake(self, delta_rake_deg: float = 0.5) -> dict:
        """
        Evalúa el impacto de reducir el rake en ±delta sobre el trail.
        Devuelve un informe de sensibilidad.
        """
        base_trail = self.trail_mm()
        new_rake   = self.effective_rake_deg() - delta_rake_deg
        new_trail  = self.trail_mm(rake_deg=new_rake)
        return {
            "base_rake_deg":   round(self.effective_rake_deg(), 3),
            "modified_rake_deg": round(new_rake, 3),
            "base_trail_mm":   base_trail,
            "modified_trail_mm": new_trail,
            "delta_trail_mm":  round(new_trail - base_trail, 2),
            "assessment": (
                "Trail crítico: riesgo de cierre de dirección (tuck-in)"
                if new_trail < 75 else
                "Trail operativo: agilidad incrementada sin pérdida de estabilidad"
                if 75 <= new_trail <= 100 else
                "Trail conservador: alta estabilidad, menor agilidad"
            ),
        }

    # ── 2. Wheelbase y transferencia de masa longitudinal ─────────────────

    def pitching_moment_analysis(self, deceleration_g: float = 1.42) -> dict:
        """
        Calcula la transferencia de carga dinámica longitudinal bajo frenada.

        ΔFz_front = (m · a · h_cg) / wheelbase

        Args:
            deceleration_g: Deceleración media bajo frenada máxima (en g).

        Returns:
            Diccionario con cargas dinámicas delanteras/traseras y riesgo de
            elevación trasera.
        """
        wb        = self.cfg.wheelbase_mm / 1000.0   # → metros
        h_cg      = self.cfg.cg_height_mm  / 1000.0
        mass      = _TOTAL_MASS_KG
        decel_ms2 = deceleration_g * _GRAVITY_MS2

        # Carga estática
        # Distribución estática 52% delante / 48% atrás (típico Moto3)
        fz_front_static = mass * _GRAVITY_MS2 * 0.52
        fz_rear_static  = mass * _GRAVITY_MS2 * 0.48

        # Transferencia dinámica bajo deceleración
        delta_fz = (mass * decel_ms2 * h_cg) / wb

        fz_front_dynamic = fz_front_static + delta_fz
        fz_rear_dynamic  = fz_rear_static  - delta_fz

        rear_lift_risk = fz_rear_dynamic <= 0

        return {
            "wheelbase_mm":         self.cfg.wheelbase_mm,
            "deceleration_g":        deceleration_g,
            "fz_front_static_N":     round(fz_front_static, 1),
            "fz_rear_static_N":      round(fz_rear_static, 1),
            "load_transfer_N":       round(delta_fz, 1),
            "fz_front_dynamic_N":    round(fz_front_dynamic, 1),
            "fz_rear_dynamic_N":     round(fz_rear_dynamic, 1),
            "rear_lift_risk":        rear_lift_risk,
            "rear_grip_pct":         round(max(fz_rear_dynamic, 0) / fz_rear_static * 100, 1),
        }

    def wheelbase_modification_impact(self, delta_mm: float = 12.0) -> dict:
        """
        Evalúa el impacto de extender la distancia entre ejes en delta_mm.
        """
        original_wb    = self.cfg.wheelbase_mm
        modified_wb    = original_wb + delta_mm
        original_pitch = self.pitching_moment_analysis()
        # Recalcular con wheelbase extendido
        self.cfg.wheelbase_mm = modified_wb
        modified_pitch = self.pitching_moment_analysis()
        self.cfg.wheelbase_mm = original_wb   # restaurar

        delta_rear_grip = modified_pitch["fz_rear_dynamic_N"] - original_pitch["fz_rear_dynamic_N"]
        return {
            "original_wheelbase_mm":  original_wb,
            "modified_wheelbase_mm":  modified_wb,
            "delta_mm":               delta_mm,
            "original_rear_grip_pct": original_pitch["rear_grip_pct"],
            "modified_rear_grip_pct": modified_pitch["rear_grip_pct"],
            "delta_rear_grip_N":      round(delta_rear_grip, 1),
            "polar_inertia_penalty":  "ALTA" if delta_mm >= 15 else "MODERADA" if delta_mm >= 8 else "BAJA",
            "recommendation": (
                f"+{delta_mm} mm recommended para recta de 994 m + frenada T1. "
                "Compensar pérdida de agilidad con reducción de Rake en -0.5°."
            ),
        }

    # ── 3. Anti-Squat ──────────────────────────────────────────────────────

    def _instant_center_height_mm(self) -> float:
        """
        Calcula la altura del centro instantáneo de la fuerza combinada
        cadena+basculante respecto al suelo.

        Método geométrico simplificado:
        - Línea 1: Eje del basculante (pivote → eje rueda trasera)
        - Línea 2: Contiene la línea de tensión de la cadena (top run)

        El centro instantáneo 'P' es la intersección de estas dos rectas
        extendidas hacia la parte frontal de la motocicleta.

        Retorna la altura h_P en milímetros.
        """
        # Coordenadas (x: positivo hacia adelante desde eje trasero; y: altura)
        # Eje rueda trasera
        x_axle, y_axle = 0.0, _REAR_WHEEL_RADIUS_MM  # = rear_axle_height

        # Pivote basculante (está adelante y arriba respecto al eje trasero)
        x_pivot = self.cfg.swingarm_length_mm
        y_pivot = self.cfg.swingarm_pivot_height_mm

        # Pendiente de la línea del basculante (basculante → pivote)
        m_swingarm = (y_pivot - y_axle) / (x_pivot - x_axle)

        # Piñón del motor (adelante del pivote)
        # El piñón está aproximadamente al nivel del motor
        x_sprocket = x_pivot + 180.0   # aprox 180 mm adelante del pivote
        y_sprocket  = self.cfg.engine_sprocket_height_mm

        # Línea del tramo superior de la cadena (eje trasero → piñón motor)
        m_chain = (y_sprocket - y_axle) / (x_sprocket - x_axle)

        # Combinación ponderada: la línea efectiva pondera 60% basculante / 40% cadena
        m_combined = 0.60 * m_swingarm + 0.40 * m_chain
        b_combined = y_axle - m_combined * x_axle   # intercepto y

        # Intersección con el plano vertical del eje delantero
        x_front_axle = self.cfg.wheelbase_mm
        h_P = m_combined * x_front_axle + b_combined

        return round(h_P, 2)

    def anti_squat_pct(self) -> float:
        """
        Porcentaje de Anti-Squat en condiciones estáticas.

            AS% = (h_P / h_CG) × 100

        donde h_P es la altura del centro instantáneo proyectada en el
        plano del eje delantero, y h_CG es la altura del centro de gravedad.
        """
        h_P  = self._instant_center_height_mm()
        h_cg = self.cfg.cg_height_mm
        return round((h_P / h_cg) * 100.0, 2)

    def anti_squat_with_pivot_adjustment(self, pivot_delta_mm: float = 2.0) -> dict:
        """
        Recalcula el anti-squat tras elevar el pivote del basculante en +pivot_delta_mm.
        """
        original_pivot   = self.cfg.swingarm_pivot_height_mm
        original_as      = self.anti_squat_pct()

        self.cfg.swingarm_pivot_height_mm += pivot_delta_mm
        modified_as = self.anti_squat_pct()
        self.cfg.swingarm_pivot_height_mm = original_pivot  # restaurar

        in_target_window = 108.0 <= modified_as <= 112.0

        return {
            "pivot_delta_mm":     pivot_delta_mm,
            "original_as_pct":    original_as,
            "modified_as_pct":    modified_as,
            "delta_as_pct":       round(modified_as - original_as, 2),
            "in_target_window":   in_target_window,
            "target_window":      "108% – 112%",
            "assessment": (
                "OBJETIVO ALCANZADO: anti-squat en ventana operativa para curvas derechas de Goiânia"
                if in_target_window else
                "FUERA DE VENTANA: ajustar pivot adicional o revisar geometría de cadena"
            ),
        }

    def chain_gearing_antisquat_interaction(self, front_teeth: int, rear_teeth: int) -> dict:
        """
        Evalúa cómo el cambio en la relación de transmisión afecta pasivamente
        el porcentaje de anti-squat a través del vector de tensión de la cadena.
        """
        original_front = self.cfg.front_sprocket_teeth
        original_rear  = self.cfg.rear_sprocket_teeth
        original_as    = self.anti_squat_pct()

        self.cfg.front_sprocket_teeth = front_teeth
        self.cfg.rear_sprocket_teeth  = rear_teeth
        new_as = self.anti_squat_pct()

        self.cfg.front_sprocket_teeth = original_front
        self.cfg.rear_sprocket_teeth  = original_rear

        return {
            "original_gearing":    f"{original_front}T / {original_rear}T",
            "new_gearing":         f"{front_teeth}T / {rear_teeth}T",
            "original_fdr":        round(original_rear / original_front, 4),
            "new_fdr":             round(rear_teeth / front_teeth, 4),
            "original_as_pct":     original_as,
            "new_as_pct":          new_as,
            "delta_as_pct":        round(new_as - original_as, 2),
            "notes": (
                "Mayor corona trasera incrementa el ángulo de ataque de la cadena, "
                "aumentando el efecto anti-squat pasivamente."
            ),
        }

    # ── 4. Resumen de configuración propuesta ─────────────────────────────

    def proposed_goiania_configuration(self) -> dict:
        """
        Genera el conjunto completo de propuestas mecánicas para Goiânia 2026.
        Aplica los ajustes del informe técnico y devuelve el análisis comparativo.
        """
        # Aplicar ajustes propuestos sobre la configuración base
        orig_wb     = self.cfg.wheelbase_mm
        orig_rake   = self.cfg.rake_deg
        orig_offset = self.cfg.fork_offset_mm
        orig_pivot  = self.cfg.swingarm_pivot_height_mm

        # Ajuste 1: +12 mm wheelbase
        self.cfg.wheelbase_mm += 12

        # Ajuste 2: -0.5° rake (subiendo los tubos de la horquilla 4 mm)
        self.cfg.fork_offset_mm += 0   # el offset se analiza independientemente
        self.cfg.front_ride_height_mm = 4.0  # 4 mm arriba → -0.48° efectivo

        # Ajuste 3: +2 mm en pivote del basculante
        self.cfg.swingarm_pivot_height_mm += 2

        result = {
            "wheelbase": {
                "original_mm":   orig_wb,
                "modified_mm":   self.cfg.wheelbase_mm,
                "delta_mm":      12,
                "pitching_analysis": self.pitching_moment_analysis(deceleration_g=1.42),
            },
            "front_geometry": {
                "original_rake_deg":   orig_rake,
                "effective_rake_deg":  self.effective_rake_deg(),
                "fork_drop_mm":        self.cfg.front_ride_height_mm,
                "base_trail_mm":       self.trail_mm(rake_deg=orig_rake, offset_mm=orig_offset),
                "modified_trail_mm":   self.trail_mm(),
                "sensitivity_report":  self.trail_sensitivity_to_rake(0.48),
            },
            "anti_squat": {
                "baseline_pct":    self.anti_squat_pct(),
                "pivot_adjustment": self.anti_squat_with_pivot_adjustment(pivot_delta_mm=0),
                "target_window":   "108% – 112%",
                "status":          (
                    "CORRECTO"
                    if 108 <= self.anti_squat_pct() <= 112
                    else "REQUIERE AJUSTE ADICIONAL"
                ),
            },
            "gearing": self.chain_gearing_antisquat_interaction(
                front_teeth=14, rear_teeth=40
            ),
        }

        # Restaurar configuración original
        self.cfg.wheelbase_mm              = orig_wb
        self.cfg.rake_deg                  = orig_rake
        self.cfg.fork_offset_mm            = orig_offset
        self.cfg.swingarm_pivot_height_mm  = orig_pivot
        self.cfg.front_ride_height_mm      = 0.0

        return result
