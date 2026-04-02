"""
race_engineering.py — Router FastAPI para el módulo de Ingeniería de Pista.

Expone los endpoints de la prueba de concepto del GP de Brasil 2026
como parte del gateway Aero-AI-Hub.
"""
from __future__ import annotations
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from backend_api.auth.core import get_current_user

# Importación lazy para evitar cargar los modelos en el import del gateway
# si las dependencias opcionales (torch, etc.) no están disponibles.
try:
    from race_engineering import (
        TechnicalReportGenerator,
        ChassisDynamicsCalculator,
        ChassisConfiguration,
        TireStrategyEngine,
        TireCompound,
        TirePosition,
        WeekendRunPlan,
        PilotDebriefingProtocol,
    )
    from race_engineering.pilot_debriefing import (
        DebriefingSession,
        PilotResponse,
        DebriefingPhase,
    )
    _RACE_ENG_AVAILABLE = True
except ImportError as _import_err:
    _RACE_ENG_AVAILABLE = False
    _IMPORT_ERROR = str(_import_err)


router = APIRouter(
    prefix="/race-engineering",
    tags=["Race Engineering — GP Brasil 2026"],
)


def _require_module():
    if not _RACE_ENG_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail=f"El módulo race_engineering no está disponible: {_IMPORT_ERROR}",
        )


# ── Modelos de request ────────────────────────────────────────────────────────

class TireAnalysisRequest(BaseModel):
    compound: str         = Field(..., example="SC1", description="SC1 o SC2")
    position: str         = Field(..., example="REAR", description="FRONT o REAR")
    ambient_temp_c: float = Field(26.0, ge=-10, le=60)
    asphalt_temp_c: float = Field(48.0, ge=0, le=80)


class ChassisAnalysisRequest(BaseModel):
    rake_deg: float               = Field(23.5, ge=18, le=32)
    fork_offset_mm: float         = Field(28.0, ge=10, le=50)
    fork_drop_mm: float           = Field(4.0, ge=-10, le=20)
    wheelbase_mm: float           = Field(1268.0, ge=1200, le=1400)
    swingarm_pivot_height_mm: float = Field(295.0, ge=270, le=330)
    cg_height_mm: float           = Field(465.0, ge=380, le=560)
    front_sprocket_teeth: int     = Field(14, ge=12, le=18)
    rear_sprocket_teeth: int      = Field(40, ge=30, le=55)


class PilotDebriefingRequest(BaseModel):
    session_name: str
    pilot_name: str
    responses: list[dict]  # [{question_id, scale_rating, verbatim_note}]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get(
    "/report",
    summary="Informe Técnico Maestro — GP Brasil 2026",
    description=(
        "Genera el Informe Técnico completo de la Prueba de Concepto para el "
        "Autódromo Internacional de Goiânia. Incluye análisis del circuito, "
        "configuración cinemática propuesta, estrategia de neumáticos, run plan "
        "y protocolo de debriefing al piloto."
    ),
)
async def get_master_report(current_user: str = Depends(get_current_user)):
    _require_module()
    t0 = time.perf_counter()
    generator = TechnicalReportGenerator()
    report    = generator.generate()
    elapsed   = round((time.perf_counter() - t0) * 1000, 1)
    return {
        "generated_by":     current_user,
        "generation_ms":    elapsed,
        "report":           report,
    }


@router.get(
    "/report/executive",
    summary="Resumen Ejecutivo — GP Brasil 2026",
    description=(
        "Devuelve una versión condensada del informe técnico para briefing rápido "
        "de dirección técnica, piloto y jefes de mecánicos."
    ),
)
async def get_executive_report(current_user: str = Depends(get_current_user)):
    _require_module()
    generator = TechnicalReportGenerator()
    report = generator.generate()

    overview = report.get("circuit_analysis", {}).get("overview", {})
    mech = report.get("chassis_dynamics", {}).get("mechanical_summary", {})
    race = report.get("tire_strategy", {}).get("race_strategy", {})
    criteria = report.get("poc_validation_criteria", {}).get("success_criteria", [])

    return {
        "generated_by": current_user,
        "event": report.get("metadata", {}).get("event"),
        "circuit": report.get("metadata", {}).get("circuit"),
        "key_metrics": {
            "lap_time_est_s": overview.get("estimated_lap_time_s"),
            "thermal_severity_index": overview.get("thermal_severity_index"),
            "asymmetry_ratio": overview.get("corners", {}).get("asymmetry_ratio"),
        },
        "chassis_setup": {
            "wheelbase_delta_mm": mech.get("wheelbase_delta_mm"),
            "rake_reduction_deg": mech.get("rake_reduction_deg"),
            "swingarm_pivot_up_mm": mech.get("swingarm_pivot_up_mm"),
            "anti_squat_target_pct": mech.get("anti_squat_target_pct"),
            "final_drive_ratio": mech.get("final_drive_ratio"),
        },
        "race_strategy": {
            "front_compound": race.get("front_compound"),
            "rear_compound": race.get("rear_compound"),
            "grid_pressure_front_bar": race.get("front_pressure_grid_bar"),
            "grid_pressure_rear_bar": race.get("rear_pressure_grid_bar"),
            "race_viable": race.get("race_viable"),
        },
        "validation_criteria": [
            {
                "id": c.get("id"),
                "metric": c.get("metric"),
                "target": c.get("target"),
            }
            for c in criteria
        ],
    }


@router.get(
    "/circuit",
    summary="Análisis del Circuito de Goiânia",
)
async def get_circuit_analysis(current_user: str = Depends(get_current_user)):
    _require_module()
    from race_engineering import GoianiaCircuit
    circuit = GoianiaCircuit()
    return {
        "summary": circuit.summary(),
        "corners": [
            {
                "number":       c.number,
                "direction":    c.direction,
                "type":         c.corner_type,
                "entry_kmh":    c.entry_speed_kmh,
                "apex_kmh":     c.apex_speed_kmh,
                "exit_kmh":     c.exit_speed_kmh,
                "banking_deg":  c.banking_deg,
                "lateral_g":    c.lateral_g,
                "critical_shoulder": c.critical_tire_hombro,
            }
            for c in circuit.corners
        ],
        "sectors": [
            {
                "id":           s.sector_id,
                "name":         s.name,
                "length_m":     s.length_m,
                "max_kmh":      s.max_speed_kmh,
                "overtaking":   s.overtaking_zone,
            }
            for s in circuit.sectors
        ],
    }


@router.post(
    "/chassis/analyze",
    summary="Análisis Dinámico del Chasis",
    description=(
        "Calcula Trail, Anti-Squat%, transferencia de carga e impacto del wheelbase "
        "para la configuración de chasis enviada. Útil para evaluar ajustes en tiempo real."
    ),
)
async def analyze_chassis(
    request: ChassisAnalysisRequest,
    current_user: str = Depends(get_current_user),
):
    _require_module()
    config = ChassisConfiguration(
        rake_deg=request.rake_deg,
        fork_offset_mm=request.fork_offset_mm,
        front_ride_height_mm=request.fork_drop_mm,
        wheelbase_mm=request.wheelbase_mm,
        swingarm_pivot_height_mm=request.swingarm_pivot_height_mm,
        cg_height_mm=request.cg_height_mm,
        front_sprocket_teeth=request.front_sprocket_teeth,
        rear_sprocket_teeth=request.rear_sprocket_teeth,
    )
    calc = ChassisDynamicsCalculator(config)
    return {
        "input_config":        request.model_dump(),
        "effective_rake_deg":  calc.effective_rake_deg(),
        "trail_mm":            calc.trail_mm(),
        "anti_squat_pct":      calc.anti_squat_pct(),
        "pitching_analysis":   calc.pitching_moment_analysis(deceleration_g=1.42),
        "trail_sensitivity":   calc.trail_sensitivity_to_rake(),
        "pivot_adjustment":    calc.anti_squat_with_pivot_adjustment(pivot_delta_mm=2.0),
        "final_drive_ratio":   config.final_drive_ratio,
    }


@router.post(
    "/tires/analyze",
    summary="Análisis de Estrategia de Neumático",
    description=(
        "Calcula la presión en frío óptima y el riesgo de degradación asimétrica "
        "para un compuesto y condiciones ambientales dados."
    ),
)
async def analyze_tire(
    request: TireAnalysisRequest,
    current_user: str = Depends(get_current_user),
):
    _require_module()
    try:
        compound = TireCompound(request.compound.upper())
        position = TirePosition(request.position.upper())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Compuesto/posición no válido: {e}")

    engine = TireStrategyEngine()
    return {
        "cold_pressure":     engine.cold_pressure_target(
            compound, position,
            request.ambient_temp_c, request.asphalt_temp_c,
        ),
        "asymmetric_risk": (
            engine.asymmetric_thermal_risk(compound, request.asphalt_temp_c)
            if position == TirePosition.REAR else None
        ),
    }


@router.get(
    "/run-plan",
    summary="Plan de Ejecución del Fin de Semana",
    description="Devuelve el run plan completo con todas las sesiones y tandas del GP Brasil 2026.",
)
async def get_run_plan(
    session: Optional[str] = Query(None, description="Filtrar por tipo de sesión: FP1, PRACTICE, FP2, Q2, WARM_UP, RACE"),
    current_user: str = Depends(get_current_user),
):
    _require_module()
    plan    = WeekendRunPlan()
    summary = plan.weekend_summary()

    if session:
        sessions = [
            s for s in plan.sessions
            if s.session_type.value == session.upper()
        ]
        if not sessions:
            raise HTTPException(
                status_code=404,
                detail=f"Sesión '{session}' no encontrada. Opciones: FP1, PRACTICE, FP2, Q2, WARM_UP, RACE",
            )
        return {
            "weekend_summary": summary,
            "sessions": [
                {
                    "name":       s.name,
                    "type":       s.session_type,
                    "start":      s.start_time,
                    "conditions": s.conditions,
                    "objective":  s.primary_objetivo,
                    "runs": [r.__dict__ for r in s.runs],
                }
                for s in sessions
            ],
        }

    return summary


@router.get(
    "/debriefing/questions",
    summary="Batería de Preguntas de Debriefing al Piloto",
    description=(
        "Devuelve el protocolo completo de interrogación post-sesión para "
        "validar las hipótesis de configuración del GP Brasil 2026."
    ),
)
async def get_debriefing_questions(
    phase: Optional[str] = Query(None, description="Filtrar por fase: FASE_1, FASE_2, FASE_3"),
    current_user: str = Depends(get_current_user),
):
    _require_module()
    protocol = PilotDebriefingProtocol()
    questions = protocol.format_for_engineer()

    if phase:
        phase_map = {
            "FASE_1": DebriefingPhase.PHASE_1_STRAIGHT_BRAKING,
            "FASE_2": DebriefingPhase.PHASE_2_CORNERING_THERMAL,
            "FASE_3": DebriefingPhase.PHASE_3_ANTISQUAT_TRACTION,
        }
        if phase.upper() not in phase_map:
            raise HTTPException(status_code=422, detail="Fase inválida. Use FASE_1, FASE_2 o FASE_3.")
        target_phase = phase_map[phase.upper()]
        questions = [q for q in questions if q["phase"] == target_phase]

    return {
        "total_questions": len(questions),
        "phases": {
            "FASE_1": "Recta + Frenada T1",
            "FASE_2": "Curvas asimétricas — Thermal",
            "FASE_3": "Anti-Squat + Tracción + Electrónica",
        },
        "questions": questions,
    }


@router.post(
    "/debriefing/evaluate",
    summary="Evaluación del Debriefing al Piloto",
    description=(
        "Recibe las respuestas del piloto en escala 1–5, valida las hipótesis de "
        "configuración y genera las acciones correctivas priorizadas."
    ),
)
async def evaluate_debriefing(
    request: PilotDebriefingRequest,
    current_user: str = Depends(get_current_user),
):
    _require_module()
    protocol = PilotDebriefingProtocol()

    session = DebriefingSession(
        session_name=request.session_name,
        pilot_name=request.pilot_name,
    )
    for r in request.responses:
        try:
            session.add_response(PilotResponse(
                question_id=r["question_id"],
                scale_rating=int(r["scale_rating"]),
                verbatim_note=r.get("verbatim_note", ""),
                session=request.session_name,
            ))
        except (KeyError, TypeError) as e:
            raise HTTPException(
                status_code=422,
                detail=f"Formato de respuesta inválido en '{r}': {e}",
            )

    return protocol.evaluate_session(session)
