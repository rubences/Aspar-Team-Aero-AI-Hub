"""
report_generator.py — Generador del Informe Técnico Maestro para el GP de Brasil 2026.

Agrega toda la información del módulo race_engineering y produce
el archivo maestro de la prueba de concepto en formato estructurado (dict / JSON).
"""
from __future__ import annotations
import json
from datetime import datetime
from typing import Any

from .goiania_circuit import GoianiaCircuit
from .chassis_dynamics import ChassisDynamicsCalculator, ChassisConfiguration
from .tire_strategy import TireStrategyEngine, TireAllocation, TireCompound, TirePosition
from .run_plan import WeekendRunPlan
from .pilot_debriefing import PilotDebriefingProtocol


class TechnicalReportGenerator:
    """
    Genera el informe técnico completo del GP de Brasil 2026 — Moto3.

    Este informe constituye el archivo maestro fundacional (Master Setup File)
    que guiará la operación del garaje desde la primera salida de FP1.
    """

    def __init__(self):
        # Circuito
        self.circuit = GoianiaCircuit()

        # Configuración base del chasis Moto3 2026
        self.base_config = ChassisConfiguration(
            rake_deg=23.5,
            fork_offset_mm=28.0,
            front_ride_height_mm=0.0,
            wheelbase_mm=1256,       # Configuración neutral (antes de propuesta)
            swingarm_length_mm=420,
            swingarm_pivot_height_mm=293,
            rear_axle_height_mm=298,
            cg_height_mm=465,
            front_sprocket_teeth=14,
            rear_sprocket_teeth=38,
            engine_sprocket_height_mm=298,
        )

        # Configuración propuesta para Goiânia
        self.goiania_config = ChassisConfiguration(
            rake_deg=23.5,
            fork_offset_mm=28.0,
            front_ride_height_mm=4.0,    # Tijas bajadas 4 mm → rake efectivo -0.48°
            wheelbase_mm=1268,            # +12 mm
            swingarm_length_mm=420,
            swingarm_pivot_height_mm=295, # +2 mm
            rear_axle_height_mm=298,
            cg_height_mm=465,
            front_sprocket_teeth=14,
            rear_sprocket_teeth=40,       # +2T corona → más fuerza / anti-squat pasivo
            engine_sprocket_height_mm=298,
        )

        self.base_calc    = ChassisDynamicsCalculator(self.base_config)
        self.goiania_calc = ChassisDynamicsCalculator(self.goiania_config)

        self.tire_engine  = TireStrategyEngine(TireAllocation())
        self.run_plan     = WeekendRunPlan()
        self.debriefing   = PilotDebriefingProtocol()

    # ─────────────────────────────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        """Genera el informe técnico completo como diccionario estructurado."""

        report = {
            "metadata": self._metadata(),
            "circuit_analysis": self._circuit_section(),
            "chassis_dynamics": self._chassis_section(),
            "tire_strategy": self._tire_section(),
            "run_plan": self._run_plan_section(),
            "debriefing_protocol": self._debriefing_section(),
            "poc_validation_criteria": self._validation_criteria(),
        }
        return report

    def to_json(self, indent: int = 2) -> str:
        """Serializa el informe a JSON."""
        return json.dumps(self.generate(), indent=indent, ensure_ascii=False, default=str)

    # ── Secciones del informe ─────────────────────────────────────────────────

    def _metadata(self) -> dict:
        return {
            "document_type":    "Informe Técnico de Ingeniería de Pista — Prueba de Concepto",
            "event":            "Gran Premio de Brasil 2026",
            "circuit":          "Autódromo Internacional de Goiânia - Ayrton Senna",
            "category":         "Moto3",
            "team":             "Aspar Team",
            "generated_at":     datetime.utcnow().isoformat() + "Z",
            "version":          "1.0.0-PoC",
            "classification":   "CONFIDENCIAL — Uso interno del equipo técnico",
            "status":           "ARCHIVO MAESTRO FUNDACIONAL — Sujeto a validación empírica en FP1",
            "authors":          ["Dpto. Ingeniería de Pista — Aspar Team Aero-AI-Hub"],
            "context": (
                "Primer evento en Goiânia tras más de dos décadas de ausencia. "
                "Asfalto reasfaltado 2025, homologación FIM Grado A. "
                "Sin telemetría histórica ni configuraciones base fiables. "
                "Toda la configuración inicial se establece mediante cálculo predictivo, "
                "cinemática avanzada y extrapolación desde Buriram 2025."
            ),
        }

    def _circuit_section(self) -> dict:
        summary = self.circuit.summary()
        return {
            "overview": summary,
            "critical_zones": [
                {
                    "zone": "Recta principal + frenada T1",
                    "length_m": self.circuit.main_straight_m,
                    "max_speed_kmh": 238,
                    "engineering_challenge": (
                        "Estabilidad longitudinal a alta velocidad + desaceleración de 1.42g. "
                        "Riesgo de snake/chatter y elevación trasera bajo frenada máxima."
                    ),
                    "dictated_parameters": ["Wheelbase", "Distribución de carga", "Gearing FDR"],
                },
                {
                    "zone": "Curvas rápidas derechas (T6, T7, T12)",
                    "corners": [6, 7, 12],
                    "max_lateral_g": 1.62,
                    "engineering_challenge": (
                        "Máxima carga sobre hombro derecho de neumáticos. "
                        "Riesgo de thermal blistering SC1 bajo anti-squat elevado."
                    ),
                    "dictated_parameters": ["Anti-squat %", "Compuesto trasero", "Presión neumático"],
                },
                {
                    "zone": "Chicane técnica T3–T4",
                    "engineering_challenge": (
                        "Transiciones rápidas que penalizan el wheelbase largo. "
                        "Compromiso agilidad/estabilidad en su máxima expresión."
                    ),
                    "dictated_parameters": ["Rake efectivo", "Trail", "Offset tijas"],
                },
            ],
            "thermal_severity": {
                "index": self.circuit.thermal_severity_index,
                "scale": "0 (fría) — 10 (extrema)",
                "asphalt_temp_est_c": self.circuit.environment.asphalt_temp_c,
                "asymmetry_ratio":    self.circuit.asymmetry_ratio,
                "impact": (
                    "EXTREMO: gradiente entre hombro derecho e izquierdo puede superar 40°C "
                    "hacia el final de la carrera. Gestión térmica es variable crítica."
                ),
            },
        }

    def _chassis_section(self) -> dict:
        # Comparativa base vs propuesta
        base_trail    = self.base_calc.trail_mm(rake_deg=23.5)
        goiania_trail = self.goiania_calc.trail_mm()
        base_as       = self.base_calc.anti_squat_pct()
        goiania_as    = self.goiania_calc.anti_squat_pct()

        return {
            "baseline_vs_proposed": {
                "parameter":           ["Wheelbase (mm)", "Rake efectivo (°)", "Trail (mm)", "Anti-squat (%)"],
                "baseline_value":      [
                    self.base_config.wheelbase_mm,
                    round(self.base_calc.effective_rake_deg(), 2),
                    base_trail,
                    base_as,
                ],
                "goiania_proposed":    [
                    self.goiania_config.wheelbase_mm,
                    round(self.goiania_calc.effective_rake_deg(), 2),
                    goiania_trail,
                    goiania_as,
                ],
                "delta":               [
                    self.goiania_config.wheelbase_mm - self.base_config.wheelbase_mm,
                    round(self.goiania_calc.effective_rake_deg() - self.base_calc.effective_rake_deg(), 2),
                    round(goiania_trail - base_trail, 2),
                    round(goiania_as - base_as, 2),
                ],
            },
            "wheelbase_analysis":    self.goiania_calc.wheelbase_modification_impact(delta_mm=12),
            "pitching_at_238kmh":    self.goiania_calc.pitching_moment_analysis(deceleration_g=1.42),
            "trail_sensitivity":     self.goiania_calc.trail_sensitivity_to_rake(delta_rake_deg=0.48),
            "anti_squat_analysis":   self.goiania_calc.anti_squat_with_pivot_adjustment(pivot_delta_mm=0),
            "gearing_interaction":  self.goiania_calc.chain_gearing_antisquat_interaction(14, 40),
            "proposed_configuration": self.goiania_calc.proposed_goiania_configuration(),
            "mechanical_summary": {
                "wheelbase_delta_mm":    12,
                "fork_drop_mm":          4.0,
                "rake_reduction_deg":    0.48,
                "swingarm_pivot_up_mm":  2,
                "front_sprocket_teeth":  14,
                "rear_sprocket_teeth":   40,
                "final_drive_ratio":     round(40 / 14, 4),
                "anti_squat_target_pct": "108% – 112%",
                "chain_links_added":     2,
            },
        }

    def _tire_section(self) -> dict:
        asphalt_temp = self.circuit.environment.asphalt_temp_c
        ambient_temp = self.circuit.environment.ambient_temp_c

        sessions_strategy = {}
        for session_key in ["FP1_RUN1", "FP1_RUN3", "PRACTICE_RUN1", "PRACTICE_RUN3",
                             "Q2_RUN1", "Q2_RUN2", "RACE"]:
            sessions_strategy[session_key] = self.tire_engine.session_compound_recommendation(
                session_key, asphalt_temp
            )

        return {
            "allocation": {
                "total_slicks":   19,
                "front_slicks":   9,
                "rear_slicks":    10,
                "breakdown": {
                    "front_sc1": 4, "front_sc2": 5,
                    "rear_sc1":  6, "rear_sc2":  4,
                },
                "extended_allocation_reason": (
                    "+2 unidades extra respecto al estándar (normalmente 17) por ser circuito "
                    "inédito: +10 min / sesión del viernes para recopilar datos básicos."
                ),
            },
            "compound_properties": {
                "SC1_description": (
                    "Blando. Ventana óptima 70–110°C en banda de rodadura. "
                    "Máximo coeficiente de fricción pero vulnerable a blistering "
                    "si supera 112°C en el hombro de apoyo."
                ),
                "SC2_description": (
                    "Medio. Ventana operativa 50–100°C. Mayor resistencia abrasiva "
                    "en asfalto nuevo. Carcasa más rígida = mejor soporte en frenada T1."
                ),
            },
            "thermal_risk_analysis": {
                "SC1_rear_at_48C_asphalt": self.tire_engine.asymmetric_thermal_risk(
                    TireCompound.SC1, asphalt_temp),
                "SC2_rear_at_48C_asphalt": self.tire_engine.asymmetric_thermal_risk(
                    TireCompound.SC2, asphalt_temp),
            },
            "cold_pressure_targets": {
                "front_SC2_practice": self.tire_engine.cold_pressure_target(
                    TireCompound.SC2, TirePosition.FRONT, ambient_temp, asphalt_temp),
                "rear_SC1_practice": self.tire_engine.cold_pressure_target(
                    TireCompound.SC1, TirePosition.REAR, ambient_temp, asphalt_temp),
                "front_SC2_race": self.tire_engine.cold_pressure_target(
                    TireCompound.SC2, TirePosition.FRONT, ambient_temp, asphalt_temp + 4),
                "rear_SC1_race": self.tire_engine.cold_pressure_target(
                    TireCompound.SC1, TirePosition.REAR, ambient_temp, asphalt_temp + 4),
            },
            "sessions_strategy": sessions_strategy,
            "race_strategy":     self.tire_engine.race_strategy(asphalt_temp),
        }

    def _run_plan_section(self) -> dict:
        summary = self.run_plan.weekend_summary()
        session_details = []
        for s in self.run_plan.sessions:
            session_details.append({
                "name":         s.name,
                "type":         s.session_type,
                "start_time":   s.start_time,
                "duration_min": s.duration_min,
                "conditions":   s.conditions,
                "objective":    s.primary_objetivo,
                "runs": [
                    {
                        "id":             r.run_id,
                        "laps":           r.laps,
                        "front":          f"{r.front_compound} / {r.front_state}",
                        "rear":           f"{r.rear_compound} / {r.rear_state}",
                        "pressures_cold": f"Del: {r.cold_pressure_front_bar} bar / Tras: {r.cold_pressure_rear_bar} bar",
                        "objective":      r.objective,
                        "telemetry":      r.telemetry_channels,
                        "notes":          r.engineer_notes,
                    }
                    for r in s.runs
                ],
            })
        return {
            "weekend_summary": summary,
            "sessions": session_details,
        }

    def _debriefing_section(self) -> dict:
        return {
            "protocol_description": (
                "Batería de 7 preguntas estructuradas en 3 fases para validar las hipótesis "
                "de configuración geométrica y termodinámica del archivo maestro. "
                "Cada pregunta incluye indicadores binarios de fallo y acciones correctivas directas."
            ),
            "phases": {
                "FASE_1": "Recta + Frenada T1: validación de Gearing, Wheelbase y Trail",
                "FASE_2": "Curvas asimétricas: validación de Agilidad y Térmica del neumático",
                "FASE_3": "Anti-Squat + Tracción + Electrónica: validación del pivote y mapas",
            },
            "questions": self.debriefing.format_for_engineer(),
            "usage_instructions": (
                "Ejecutar el debriefing de Fase 1–2 al finalizar FP1. "
                "Ejecutar Fase 3 al finalizar la Practice oficial. "
                "Correlacionar TODAS las respuestas con el canal de telemetría indicado "
                "antes de efectuar cualquier cambio mecánico."
            ),
        }

    def _validation_criteria(self) -> dict:
        """Criterios objetivos de validación de la prueba de concepto."""
        return {
            "success_criteria": [
                {
                    "id": "VC-01",
                    "metric": "Tiempo de vuelta FP1 vs estimación base",
                    "target": "Dentro de ±1.5s del tiempo estimado de 83.8s",
                    "data_source": "Transponder + GPS",
                },
                {
                    "id": "VC-02",
                    "metric": "Temperatura hombro derecho SC1 al final de tanda PRACTICE",
                    "target": "< 108°C (límite de blistering)",
                    "data_source": "Sensor IR en garaje al finalizar tanda",
                },
                {
                    "id": "VC-03",
                    "metric": "Recorrido amortiguador trasero bajo aceleración máxima",
                    "target": "< 18 mm de squat dinámico → confirma anti-squat 108%+",
                    "data_source": "Potenciómetro lineal suspensión trasera",
                },
                {
                    "id": "VC-04",
                    "metric": "Velocidad de entrada a T1 vs velocidad mínima en T1",
                    "target": "Ratio < 2.6 (estable bajo wheelbase largo)",
                    "data_source": "Speed sensor + GPS T1 sector",
                },
                {
                    "id": "VC-05",
                    "metric": "Puntuación de correlación debriefing piloto",
                    "target": "≥ 3.5 / 5.0 en la batería de 7 preguntas del protocolo",
                    "data_source": "DebriefingSession.correlation_score()",
                },
                {
                    "id": "VC-06",
                    "metric": "Presión neumático trasero EN PISTA (carrera)",
                    "target": "≥ 1.65 bar en todo momento (límite reglamentario DURO)",
                    "data_source": "Sensor de presión activado por TPMS / medición en box stop",
                },
            ],
            "poc_declaration": (
                "La prueba de concepto se considerará VALIDADA cuando los criterios VC-02, "
                "VC-03 y VC-05 sean superados simultáneamente al finalizar la Practice del viernes. "
                "VC-01, VC-04 y VC-06 son criterios de seguridad y deben mantenerse en todo momento."
            ),
        }
