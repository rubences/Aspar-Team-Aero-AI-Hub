#!/usr/bin/env python3
"""
poc_goiania_2026.py — Script ejecutable de la Prueba de Concepto.

Genera y muestra en consola el Informe Técnico de Ingeniería de Pista
para el Gran Premio de Brasil 2026 — Autódromo Internacional de Goiânia.

Uso:
    python scripts/poc_goiania_2026.py
    python scripts/poc_goiania_2026.py --output report_goiania_2026.json
    python scripts/poc_goiania_2026.py --section chassis
    python scripts/poc_goiania_2026.py --section debriefing
"""
from __future__ import annotations
import argparse
import json
import sys
import os
import time

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from race_engineering import TechnicalReportGenerator
from race_engineering.goiania_circuit import GoianiaCircuit
from race_engineering.chassis_dynamics import ChassisDynamicsCalculator, ChassisConfiguration
from race_engineering.tire_strategy import TireStrategyEngine, TireCompound, TirePosition
from race_engineering.run_plan import WeekendRunPlan
from race_engineering.pilot_debriefing import (
    PilotDebriefingProtocol, DebriefingSession, PilotResponse
)


# ── Utilidades de presentación ────────────────────────────────────────────────

SEPARATOR   = "═" * 80
SUBSEP      = "─" * 80
RED         = "\033[91m"
GREEN       = "\033[92m"
YELLOW      = "\033[93m"
BLUE        = "\033[94m"
MAGENTA     = "\033[95m"
CYAN        = "\033[96m"
BOLD        = "\033[1m"
RESET       = "\033[0m"


def header(text: str, color: str = CYAN) -> None:
    print(f"\n{color}{BOLD}{SEPARATOR}{RESET}")
    print(f"{color}{BOLD}  {text}{RESET}")
    print(f"{color}{BOLD}{SEPARATOR}{RESET}")


def section(text: str) -> None:
    print(f"\n{YELLOW}{BOLD}{SUBSEP}{RESET}")
    print(f"{YELLOW}{BOLD}  ▸ {text}{RESET}")
    print(f"{YELLOW}{BOLD}{SUBSEP}{RESET}")


def kv(key: str, value, unit: str = "") -> None:
    val_str = f"{value:.4f}" if isinstance(value, float) else str(value)
    print(f"  {BLUE}{key:<42}{RESET}{BOLD}{val_str}{RESET} {unit}")


def status(label: str, ok: bool, ok_text: str = "OK", fail_text: str = "REVISAR") -> None:
    color  = GREEN if ok else RED
    symbol = "✓" if ok else "✗"
    text   = ok_text if ok else fail_text
    print(f"  {color}{BOLD}[{symbol}] {label:<40} {text}{RESET}")


# ── Funciones de sección ──────────────────────────────────────────────────────

def run_circuit_analysis() -> None:
    header("ANÁLISIS DEL CIRCUITO — GOIÂNIA 2026", CYAN)
    circuit = GoianiaCircuit()

    section("Datos Generales del Trazado")
    kv("Circuito", circuit.name)
    kv("Longitud total", circuit.total_length_m, "m")
    kv("Número de curvas", circuit.num_corners)
    kv("Curvas a la derecha", circuit.right_corners)
    kv("Curvas a la izquierda", circuit.left_corners)
    kv("Índice de asimetría R/L", circuit.asymmetry_ratio)
    kv("Recta principal", circuit.main_straight_m, "m")
    kv("Distancia de carrera (24 vueltas)", circuit.race_distance_km, "km")
    kv("Tiempo de vuelta estimado", circuit.estimated_lap_time_s, "s")

    section("Condiciones Ambientales Proyectadas")
    env = circuit.environment
    kv("Temperatura ambiente", env.ambient_temp_c, "°C")
    kv("Temperatura asfalto (estimada)", env.asphalt_temp_c, "°C")
    kv("Humedad relativa", env.humidity_pct, "%")
    kv("Viento sostenido", env.wind_kmh, "km/h")
    kv("Estado del asfalto", env.track_condition)

    section("Severidad Térmica y Riesgo Asimétrico")
    tsi = circuit.thermal_severity_index
    color = RED if tsi >= 7 else YELLOW if tsi >= 4 else GREEN
    print(f"  Índice de Severidad Térmica: {color}{BOLD}{tsi}/10{RESET}")
    status("Riesgo de blistering hombro derecho", tsi >= 6,
           ok_text=f"ELEVADO (TSI={tsi})", fail_text=f"MODERADO (TSI={tsi})")

    section("Curvas Críticas — Resumen de Demandas")
    print(f"\n  {'#':>3}  {'Dir':>5}  {'Tipo':>7}  {'Entrada':>8}  {'Ápice':>6}  {'Lat-g':>6}  {'Flanco':>6}")
    print(f"  {'─'*3}  {'─'*5}  {'─'*7}  {'─'*8}  {'─'*6}  {'─'*6}  {'─'*6}")
    for c in circuit.corners:
        flag = f"{RED}◉{RESET}" if c.lateral_g >= 1.5 else "·"
        print(f"  {c.number:>3}  {c.direction.value:>5}  {c.corner_type.value:>7}  "
              f"{c.entry_speed_kmh:>7.0f}k  {c.apex_speed_kmh:>5.0f}k  "
              f"{c.lateral_g:>6.2f}g  {c.critical_tire_hombro.value[:1]:>6}  {flag}")


def run_chassis_analysis() -> None:
    header("CONFIGURACIÓN DINÁMICA DEL CHASIS — GOIÂNIA 2026", MAGENTA)

    # Configuración base vs propuesta para Goiânia
    base_cfg = ChassisConfiguration(
        rake_deg=23.5, fork_offset_mm=28.0, front_ride_height_mm=0.0,
        wheelbase_mm=1256, swingarm_pivot_height_mm=293,
        front_sprocket_teeth=14, rear_sprocket_teeth=38,
    )
    goiania_cfg = ChassisConfiguration(
        rake_deg=23.5, fork_offset_mm=28.0, front_ride_height_mm=4.0,
        wheelbase_mm=1268, swingarm_pivot_height_mm=295,
        front_sprocket_teeth=14, rear_sprocket_teeth=40,
    )
    base    = ChassisDynamicsCalculator(base_cfg)
    goiania = ChassisDynamicsCalculator(goiania_cfg)

    section("Comparativa Base → Propuesta Goiânia")
    print(f"\n  {'Parámetro':<35} {'Base':>10}  {'Goiânia':>10}  {'Delta':>10}")
    print(f"  {'─'*35} {'─'*10}  {'─'*10}  {'─'*10}")

    params = [
        ("Wheelbase (mm)",          base_cfg.wheelbase_mm,                goiania_cfg.wheelbase_mm),
        ("Rake efectivo (°)",        base.effective_rake_deg(),            goiania.effective_rake_deg()),
        ("Trail (mm)",               base.trail_mm(rake_deg=23.5),        goiania.trail_mm()),
        ("Anti-squat (%)",           base.anti_squat_pct(),               goiania.anti_squat_pct()),
        ("Final Drive Ratio",        base_cfg.final_drive_ratio,          goiania_cfg.final_drive_ratio),
    ]
    for name, base_val, goiania_val in params:
        delta = goiania_val - base_val
        delta_str = f"{delta:+.2f}" if isinstance(delta, float) else f"{delta:+d}"
        color = GREEN if delta != 0 else RESET
        print(f"  {name:<35} {base_val:>10.2f}  "
              f"{color}{BOLD}{goiania_val:>10.2f}{RESET}  "
              f"{YELLOW}{delta_str:>10}{RESET}")

    section("Análisis de Cabeceo — Frenada T1 (238 → 0 km/h, 1.42g)")
    pitch = goiania.pitching_moment_analysis(deceleration_g=1.42)
    kv("Transferencia de carga (N)", pitch["load_transfer_N"], "N")
    kv("Carga dinámica delantera", pitch["fz_front_dynamic_N"], "N")
    kv("Carga dinámica trasera", pitch["fz_rear_dynamic_N"], "N")
    kv("Agarre trasero residual", pitch["rear_grip_pct"], "%")
    status("Riesgo de elevación trasera", not pitch["rear_lift_risk"],
           ok_text="RUEDA TRASERA EN CONTACTO", fail_text="ELEVACIÓN TRASERA — AJUSTAR WB")

    section("Análisis de Trail — Modificación de Tijas")
    trail_report = goiania.trail_sensitivity_to_rake(delta_rake_deg=0.48)
    kv("Rake base (°)", trail_report["base_rake_deg"])
    kv("Rake efectivo post-ajuste (°)", trail_report["modified_rake_deg"])
    kv("Trail base (mm)", trail_report["base_trail_mm"])
    kv("Trail modificado (mm)", trail_report["modified_trail_mm"])
    kv("Delta trail (mm)", trail_report["delta_trail_mm"])
    trail_ok = 75 <= trail_report["modified_trail_mm"] <= 100
    status("Trail en ventana operativa [75–100 mm]", trail_ok,
           ok_text=trail_report["assessment"], fail_text=trail_report["assessment"])

    section("Anti-Squat — Objetivo 108%–112%")
    as_report = goiania.anti_squat_with_pivot_adjustment(pivot_delta_mm=0)
    kv("Anti-squat real con configuración Goiânia (%)", goiania.anti_squat_pct())
    status("Anti-squat en ventana 108%–112%",
           108 <= goiania.anti_squat_pct() <= 112,
           ok_text="VENTANA ALCANZADA",
           fail_text="REQUIERE AJUSTE ADICIONAL DEL PIVOTE")

    section("Interacción Cadena ↔ Anti-Squat")
    gear_report = base.chain_gearing_antisquat_interaction(14, 40)
    kv("Gearing base", gear_report["original_gearing"])
    kv("Gearing propuesto Goiânia", gear_report["new_gearing"])
    kv("FDR base", gear_report["original_fdr"])
    kv("FDR propuesto", gear_report["new_fdr"])
    kv("Delta anti-squat por cambio de corona", gear_report["delta_as_pct"], "%")
    print(f"\n  {CYAN}ℹ {gear_report['notes']}{RESET}")


def run_tire_analysis() -> None:
    header("ESTRATEGIA TERMODINÁMICA DE NEUMÁTICOS PIRELLI", GREEN)
    engine   = TireStrategyEngine()
    asphalt  = 48.0
    ambient  = 26.0

    section("Riesgo de Degradación Asimétrica — Hombro Derecho")
    for compound in [TireCompound.SC1, TireCompound.SC2]:
        risk = engine.asymmetric_thermal_risk(compound, asphalt)
        is_critical = risk["right_blistering_risk"]
        color = RED if is_critical else YELLOW
        print(f"\n  Compuesto: {BOLD}{compound.value}{RESET}")
        kv("Temp. estimada hombro derecho", risk["right_shoulder_temp_est_c"], "°C")
        kv("Temp. estimada hombro izquierdo", risk["left_shoulder_temp_est_c"], "°C")
        kv("Umbral de ampollas", risk["blistering_onset_c"], "°C")
        print(f"  {color}{BOLD}  Severidad: {risk['severity']}{RESET}")
        print(f"  → {risk['management_action']}")

    section("Presiones en Frío — Condiciones Race Day (52°C asfalto)")
    for compound, pos, label in [
        (TireCompound.SC2, TirePosition.FRONT, "SC2 Delantero — Carrera"),
        (TireCompound.SC1, TirePosition.REAR,  "SC1 Trasero   — Carrera"),
    ]:
        cp = engine.cold_pressure_target(compound, pos, ambient, asphalt + 4)
        print(f"\n  {BOLD}{label}{RESET}")
        kv("Presión en frío objetivo (bar)", cp["cold_pressure_bar"])
        kv("Presión caliente objetivo (bar)", cp["hot_target_bar"])
        kv("Mínimo reglamentario (bar)", cp["regulatory_min_bar"])
        status("Presión reglamentariamente válida", cp["compliant"],
               ok_text="CUMPLE", fail_text="AJUSTAR PRESIÓN")

    section("Estrategia de Carrera — 24 Vueltas")
    race = engine.race_strategy(asphalt_temp_c=asphalt)
    kv("Compuesto delantero", race["front_compound"].value)
    kv("Compuesto trasero",   race["rear_compound"].value)
    kv("Presión parrilla delantera (bar)", race["front_pressure_grid_bar"])
    kv("Presión parrilla trasera (bar)",   race["rear_pressure_grid_bar"])
    kv("Vueltas antes de degradación crítica (estimado)", race["rear_thermal_limit_laps"])
    status("Neumático viable 24 vueltas", race["race_viable"],
           ok_text="VIABLE", fail_text="RIESGO TÉRMICO > 20 vueltas")
    print(f"\n  Gestión del acelerador: {CYAN}{race['throttle_management']}{RESET}")

    if race["risk_flags"]:
        print(f"\n  {RED}{BOLD}Flags de Riesgo:{RESET}")
        for flag in race["risk_flags"]:
            print(f"  {RED}⚠ {flag}{RESET}")


def run_run_plan() -> None:
    header("PLAN DE EJECUCIÓN — FIN DE SEMANA GP BRASIL 2026", BLUE)
    plan    = WeekendRunPlan()
    summary = plan.weekend_summary()

    section("Resumen de Asignación de Neumáticos")
    alloc = summary["tire_usage"]
    kv("Neumáticos delanteros asignados", alloc["allocation_fronts"])
    kv("Neumáticos traseros asignados",   alloc["allocation_rears"])
    kv("Delanteros nuevos planificados",  alloc["new_fronts_planned"])
    kv("Traseros nuevos planificados",    alloc["new_rears_planned"])
    kv("Delanteros sobrantes (reserva)",  alloc["fronts_remaining"])
    kv("Traseros sobrantes (reserva)",    alloc["rears_remaining"])

    section("Sesiones del Fin de Semana")
    for s_data in summary["sessions"]:
        print(f"\n  {BOLD}{s_data['name']}{RESET}")
        print(f"    Inicio:    {s_data['start_time']}")
        print(f"    Duración:  {s_data['duration_min']} min")
        print(f"    Tandas:    {s_data['runs']}  |  Vueltas totales: {s_data['total_laps']}")

    section("Detalle de Tandas — Sesiones Viernes")
    for session_obj in plan.sessions[:2]:
        print(f"\n  ▸ {BOLD}{session_obj.name}{RESET}")
        print(f"    Condiciones: {session_obj.conditions}")
        for r in session_obj.runs:
            print(f"\n    {CYAN}[{r.run_id}]{RESET} {r.laps} vueltas")
            print(f"      Del: {r.front_compound}/{r.front_state}  |  Tras: {r.rear_compound}/{r.rear_state}")
            print(f"      Presiones frío: {r.cold_pressure_front_bar} / {r.cold_pressure_rear_bar} bar")
            print(f"      Objetivo: {r.objective}")


def run_debriefing_demo() -> None:
    header("PROTOCOLO DE DEBRIEFING — VALIDACIÓN DE HIPÓTESIS", YELLOW)
    protocol = PilotDebriefingProtocol()

    section("Batería de Preguntas Protocolizadas (7 preguntas / 3 fases)")
    for phase_name, phase_label in [
        ("FASE_1_RECTA_FRENADA",     "FASE 1 — Recta + Frenada T1"),
        ("FASE_2_CURVA_TERMICA",     "FASE 2 — Curvas Asimétricas / Térmica"),
        ("FASE_3_ANTISQUAT_TRACCION","FASE 3 — Anti-Squat + Tracción + Electrónica"),
    ]:
        questions = [q for q in protocol.format_for_engineer() if q["phase"] == phase_name]
        print(f"\n  {MAGENTA}{BOLD}{phase_label}{RESET}")
        for q in questions:
            print(f"\n    {BOLD}[{q['id']}]{RESET} {q['pregunta_piloto'][:80]}...")
            print(f"    → Hipótesis: {q['hipotesis'][:70]}...")
            print(f"    → Canales telemetría: {', '.join(q['telemetria'][:3])}")

    section("Simulación de Evaluación Post-FP1")
    # Simular respuestas del piloto (escenario optimista con un fallo detectado)
    mock_session = DebriefingSession(
        session_name="FP1 — Goiânia 2026",
        pilot_name="Piloto Demo",
    )
    responses_sim = [
        ("F1-Q1", 4, "El motor llega al limitador exactamente en el punto de frenada. Perfecto."),
        ("F1-Q2", 3, "El tren trasero se mantiene pero siento un pequeño micro-chatter en la desaceleración máxima."),
        ("F1-Q3", 4, "La dirección cae bien al ápice. Sin tuck-in."),
        ("F2-Q1", 3, "Algo de resistencia en los cambios de dirección, tolerable pero notar el wheelbase largo."),
        ("F2-Q2", 2, "Siento que el hombro derecho está muy al límite después de 8 vueltas. Predecible pero cerca."),
        ("F3-Q1", 4, "El trasero se mantiene firme bajo aceleración. Muy bien en las derechas rápidas."),
        ("F3-Q2", 4, "El wheelspin se convierte en tracción limpia. Sin pogo."),
        ("F3-Q3", 3, "El freno motor colabora bien, aunque podría bajar 1 step el EB para más fluidez."),
    ]
    for qid, rating, note in responses_sim:
        mock_session.add_response(PilotResponse(
            question_id=qid, scale_rating=rating, verbatim_note=note
        ))

    result = protocol.evaluate_session(mock_session)

    print(f"\n  Puntuación de correlación global: {BOLD}{result['correlation_score']}/5.0{RESET}")
    print(f"  Estado de las hipótesis:          {BOLD}{result['hypothesis_status']}{RESET}")
    print(f"\n  Estado PoC: {GREEN if not result['failed_hypotheses'] else YELLOW}"
          f"{BOLD}{result['poc_status']}{RESET}")

    if result["corrective_actions"]:
        print(f"\n  {RED}{BOLD}Acciones Correctivas Requeridas:{RESET}")
        for action in result["corrective_actions"]:
            print(f"  {RED}⚠ [{action['question_id']}] {action['action']}{RESET}")


def run_validation_criteria() -> None:
    header("CRITERIOS DE VALIDACIÓN DE LA PRUEBA DE CONCEPTO", GREEN)
    generator = TechnicalReportGenerator()
    report    = generator.generate()
    criteria  = report["poc_validation_criteria"]

    section("Criterios de Éxito Objetivos")
    for vc in criteria["success_criteria"]:
        print(f"\n  {BOLD}[{vc['id']}]{RESET} {vc['metric']}")
        print(f"    Objetivo:    {GREEN}{vc['target']}{RESET}")
        print(f"    Fuente data: {vc['data_source']}")

    print(f"\n  {CYAN}{BOLD}Declaración de Validación:{RESET}")
    print(f"  {criteria['poc_declaration']}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PoC — Informe Técnico Ingeniería de Pista GP Brasil 2026"
    )
    parser.add_argument(
        "--section",
        choices=["all", "circuit", "chassis", "tires", "runplan", "debriefing", "validation"],
        default="all",
        help="Sección del informe a generar (default: all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Guardar el informe completo en un archivo JSON",
    )
    args = parser.parse_args()

    print(f"\n{BOLD}{CYAN}{'═' * 80}")
    print("  ASPAR TEAM — AERO-AI-HUB")
    print("  Prueba de Concepto: Informe Técnico de Ingeniería de Pista")
    print("  Gran Premio de Brasil 2026 — Autódromo Internacional de Goiânia")
    print(f"{'═' * 80}{RESET}")

    t0 = time.perf_counter()

    section_map = {
        "circuit":    run_circuit_analysis,
        "chassis":    run_chassis_analysis,
        "tires":      run_tire_analysis,
        "runplan":    run_run_plan,
        "debriefing": run_debriefing_demo,
        "validation": run_validation_criteria,
    }

    if args.section == "all":
        for fn in section_map.values():
            fn()
    elif args.section in section_map:
        section_map[args.section]()

    elapsed = time.perf_counter() - t0
    print(f"\n{GREEN}{BOLD}{'═' * 80}")
    print(f"  PoC generada en {elapsed:.2f} s")
    print(f"{'═' * 80}{RESET}\n")

    if args.output:
        generator = TechnicalReportGenerator()
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(generator.to_json())
        print(f"{GREEN}Informe completo guardado en: {args.output}{RESET}\n")


if __name__ == "__main__":
    main()
