class RaceEngineerAgent:
    """
    Specialist in race procedures, strategy, and operational diagnostics.
    """
    def __init__(self, diagnostics_engine, mongo_client):
        self.diagnostics = diagnostics_engine
        self.mongo = mongo_client

    def provide_strategy(self, query: str):
        # 1. Check diagnostics
        # 2. Consult setups/regulations in RAG
        return "Operational Procedure: Perform Box-and-Go for tire temperature normalization."

if __name__ == "__main__":
    print("Race Engineer Agent initialized")
    """
    Race Engineer Agent — integrado con el módulo race_engineering (PoC GP Brasil 2026).
    """
    from __future__ import annotations
    import re
    from typing import Any

    try:
        from race_engineering import (
            TechnicalReportGenerator,
            ChassisDynamicsCalculator,
            ChassisConfiguration,
            TireStrategyEngine,
            TireCompound,
            TirePosition,
        )
        from race_engineering.goiania_circuit import GoianiaCircuit
        _RACE_ENGINEERING_AVAILABLE = True
    except ImportError:
        _RACE_ENGINEERING_AVAILABLE = False


    class RaceEngineerAgent:
        """
        Specialist in race procedures, strategy, and operational diagnostics.
        Enhanced with the Goiânia 2026 PoC race engineering module.
        """

        # Keywords → routing to race_engineering module
        _KEYWORDS_ANTISQUAT  = ["anti-squat", "antisquat", "squat", "hundimiento", "pivote"]
        _KEYWORDS_TIRE       = ["neumático", "presión", "compuesto", "sc1", "sc2", "thermal", "blistering"]
        _KEYWORDS_CHASSIS    = ["wheelbase", "rake", "trail", "chasis", "tijas", "basculante"]
        _KEYWORDS_RUNPLAN    = ["tanda", "run plan", "sesión", "fp1", "fp2", "practice", "q2", "carrera"]
        _KEYWORDS_REPORT     = ["informe", "report", "poc", "prueba de concepto", "goiânia", "goiania"]

        def __init__(self, diagnostics_engine, mongo_client):
            self.diagnostics  = diagnostics_engine
            self.mongo        = mongo_client
            self._circuit     = GoianiaCircuit()         if _RACE_ENGINEERING_AVAILABLE else None
            self._tire_engine = TireStrategyEngine()     if _RACE_ENGINEERING_AVAILABLE else None
            self._report_gen  = TechnicalReportGenerator() if _RACE_ENGINEERING_AVAILABLE else None

        # ── Dispatcher ────────────────────────────────────────────────────────────

        def provide_strategy(self, query: str) -> str:
            """
            Routes the query to the appropriate specialist sub-function.
            Falls back to the legacy generic response if the module is unavailable.
            """
            if not _RACE_ENGINEERING_AVAILABLE:
                return "Operational Procedure: Perform Box-and-Go for tire temperature normalization."

            q = query.lower()

            if any(kw in q for kw in self._KEYWORDS_REPORT):
                return self._strategy_full_report()
            if any(kw in q for kw in self._KEYWORDS_ANTISQUAT):
                return self._strategy_antisquat(query)
            if any(kw in q for kw in self._KEYWORDS_TIRE):
                return self._strategy_tire(query)
            if any(kw in q for kw in self._KEYWORDS_CHASSIS):
                return self._strategy_chassis(query)
            if any(kw in q for kw in self._KEYWORDS_RUNPLAN):
                return self._strategy_runplan()

            # Generic fallback
            return (
                "Race Engineering Agent (Goiânia 2026): consulta no específica. "
                "Especifica: informe, anti-squat, neumático, chasis o run plan."
            )

        # ── Sub-estrategias ───────────────────────────────────────────────────────

        def _strategy_full_report(self) -> str:
            report = self._report_gen.generate()
            meta   = report["metadata"]
            chassis = report["chassis_dynamics"]["mechanical_summary"]
            race    = report["tire_strategy"]["race_strategy"]
            return (
                f"[INFORME MAESTRO — {meta['event']}]\n"
                f"Circuito: {meta['circuit']}\n"
                f"Wheelbase: +{chassis['wheelbase_delta_mm']} mm | "
                f"Rake: -{chassis['rake_reduction_deg']}° | "
                f"Anti-squat objetivo: {chassis['anti_squat_target_pct']}\n"
                f"Carrera: {race['front_compound'].value} delantero / "
                f"{race['rear_compound'].value} trasero | "
                f"Presión parrilla: Del {race['front_pressure_grid_bar']} / "
                f"Tras {race['rear_pressure_grid_bar']} bar\n"
                f"PoC viable: {'SÍ' if race['race_viable'] else 'REVISAR ESTRATEGIA TÉRMICA'}"
            )

        def _strategy_antisquat(self, query: str) -> str:
            cfg  = ChassisConfiguration(
                wheelbase_mm=1268, swingarm_pivot_height_mm=295,
                front_sprocket_teeth=14, rear_sprocket_teeth=40,
                front_ride_height_mm=4.0,
            )
            calc = ChassisDynamicsCalculator(cfg)
            as_pct = calc.anti_squat_pct()
            in_window = 108 <= as_pct <= 112
            return (
                f"Anti-Squat Goiânia (pivote +2 mm, corona 40T): {as_pct:.1f}%\n"
                f"Ventana objetivo: 108%–112%\n"
                f"Estado: {'✓ VENTANA ALCANZADA' if in_window else '⚠ REQUIERE AJUSTE ADICIONAL'}\n"
                f"Justificación: las 9 curvas derechas exigen suspensión firme bajo aceleración "
                f"para evitar squat excesivo y thermal blistering del hombro SC1."
            )

        def _strategy_tire(self, query: str) -> str:
            q = query.lower()
            # Detectar si el usuario pregunta por condiciones extremas (>50°C)
            asphalt_temp = 52.0 if "52" in q or "calor extremo" in q else 48.0
            risk_sc1  = self._tire_engine.asymmetric_thermal_risk(TireCompound.SC1, asphalt_temp)
            risk_sc2  = self._tire_engine.asymmetric_thermal_risk(TireCompound.SC2, asphalt_temp)
            race_strat = self._tire_engine.race_strategy(asphalt_temp_c=asphalt_temp)
            return (
                f"Estrategia de neumáticos GP Brasil 2026 (asfalto {asphalt_temp}°C):\n"
                f"SC1 trasero — hombro derecho estimado: {risk_sc1['right_shoulder_temp_est_c']}°C "
                f"[límite: {risk_sc1['blistering_onset_c']}°C] — {risk_sc1['severity']}\n"
                f"SC2 trasero — hombro derecho estimado: {risk_sc2['right_shoulder_temp_est_c']}°C "
                f"[límite: {risk_sc2['blistering_onset_c']}°C] — {risk_sc2['severity']}\n"
                f"Recomendación carrera: {race_strat['front_compound'].value} del / "
                f"{race_strat['rear_compound'].value} tras | "
                f"Viable 24 vueltas: {'SÍ' if race_strat['race_viable'] else 'RIESGO'}"
            )

        def _strategy_chassis(self, query: str) -> str:
            cfg  = ChassisConfiguration(
                rake_deg=23.5, fork_offset_mm=28.0, front_ride_height_mm=4.0,
                wheelbase_mm=1268, swingarm_pivot_height_mm=295,
            )
            calc = ChassisDynamicsCalculator(cfg)
            return (
                f"Configuración chasis Goiânia 2026:\n"
                f"  Wheelbase: {cfg.wheelbase_mm} mm (+12 vs base)\n"
                f"  Rake efectivo: {calc.effective_rake_deg():.2f}° (-0.48° vía tijas bajas 4 mm)\n"
                f"  Trail: {calc.trail_mm():.1f} mm (ventana 75–100 mm)\n"
                f"  Anti-squat: {calc.anti_squat_pct():.1f}% (objetivo 108%–112%)\n"
                f"  Análisis cabeceo T1 (1.42g): "
                f"{calc.pitching_moment_analysis(1.42)['rear_grip_pct']:.1f}% agarre trasero residual"
            )

        def _strategy_runplan(self) -> str:
            from race_engineering.run_plan import WeekendRunPlan
            plan    = WeekendRunPlan()
            summary = plan.weekend_summary()
            sessions = "\n".join(
                f"  {s['name']:35} {s['start_time']:25} {s['total_laps']} vueltas"
                for s in summary["sessions"]
            )
            alloc = summary["tire_usage"]
            return (
                f"Run Plan GP Brasil 2026 — Goiânia:\n"
                f"{sessions}\n\n"
                f"Asignación neumáticos: {alloc['allocation_fronts']} del / {alloc['allocation_rears']} tras "
                f"(19 total — asignación ampliada por circuito inédito)\n"
                f"Reservados para carrera: {alloc['fronts_remaining']} del / {alloc['rears_remaining']} tras"
            )


    if __name__ == "__main__":
        print("Race Engineer Agent initialized")
        if _RACE_ENGINEERING_AVAILABLE:
            agent = RaceEngineerAgent(None, None)
            print(agent.provide_strategy("Dame el informe maestro de Goiânia"))
