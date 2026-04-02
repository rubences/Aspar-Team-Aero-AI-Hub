"""
run_plan.py — Plan de ejecución (Run Plan) del fin de semana del GP de Brasil 2026.

Estructura las tandas, asignación de neumáticos, objetivos técnicos
y protocolos de ingeniería para cada sesión del Autódromo de Goiânia.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class SessionType(str, Enum):
    FP1          = "FP1"
    PRACTICE     = "PRACTICE"
    FP2          = "FP2"
    Q1           = "Q1"
    Q2           = "Q2"
    WARM_UP      = "WARM_UP"
    RACE         = "RACE"


@dataclass(frozen=True)
class Tanda:
    """Una salida individual del garaje."""
    run_id: str
    laps: int
    front_compound: str      # SC1 / SC2
    rear_compound: str
    front_state: str         # NEW / USED
    rear_state: str
    cold_pressure_front_bar: float
    cold_pressure_rear_bar: float
    objective: str
    telemetry_channels: List[str]
    engineer_notes: str


@dataclass
class Session:
    session_type: SessionType
    name: str
    start_time: str
    duration_min: int
    conditions: str
    primary_objetivo: str
    runs: List[Tanda] = field(default_factory=list)

    def total_laps(self) -> int:
        return sum(r.laps for r in self.runs)

    def tires_consumed(self) -> dict:
        fronts = sum(1 for r in self.runs if r.front_state == "NEW")
        rears  = sum(1 for r in self.runs if r.rear_state  == "NEW")
        return {"new_fronts": fronts, "new_rears": rears}


@dataclass
class WeekendRunPlan:
    """
    Plan completo del fin de semana del GP de Brasil 2026 — Goiânia.
    """
    event: str = "Gran Premio de Brasil 2026"
    circuit: str = "Autódromo Internacional de Goiânia - Ayrton Senna"
    category: str = "Moto3"
    dates: str = "20–22 de Marzo, 2026"
    tire_allocation: dict = field(default_factory=lambda: {
        "total": 19, "fronts": 9, "rears": 10,
        "front_sc1": 4, "front_sc2": 5, "rear_sc1": 6, "rear_sc2": 4,
    })
    sessions: List[Session] = field(default_factory=list)

    def __post_init__(self):
        self.sessions = self._build_sessions()

    def _build_sessions(self) -> List[Session]:
        return [
            self._build_fp1(),
            self._build_practice(),
            self._build_fp2(),
            self._build_q2(),
            self._build_warmup(),
            self._build_race(),
        ]

    # ─────────────────────────────────────────────────────────────────────────
    def _build_fp1(self) -> Session:
        return Session(
            session_type=SessionType.FP1,
            name="Free Practice 1 (FP1)",
            start_time="Viernes 20/03 — 09:00",
            duration_min=55,
            conditions=(
                "Asfalto verde (sin goma depositada), suciedad roja arcillosa, "
                "baja adherencia, temperatura 22–26°C ambiente."
            ),
            primary_objetivo=(
                "Shakedown, barrido de pista, verificación de gearing y "
                "primera evaluación de la cinemática propuesta."
            ),
            runs=[
                Tanda(
                    run_id="FP1-R1", laps=5,
                    front_compound="SC2", rear_compound="SC2",
                    front_state="NEW",   rear_state="NEW",
                    cold_pressure_front_bar=1.60, cold_pressure_rear_bar=1.35,
                    objective="Shakedown inicial. Verificación de frenos, sensores de recorrido y temperaturas.",
                    telemetry_channels=["front_suspension_pot", "rear_suspension_pot",
                                        "brake_pressure_front", "tire_temp_IR"],
                    engineer_notes=(
                        "SC2 en ambos ejes para prevenir cold-tear en asfalto abrasivo virgen. "
                        "Piloto debe barrer la línea óptima de contaminación roja."
                    ),
                ),
                Tanda(
                    run_id="FP1-R2", laps=6,
                    front_compound="SC2", rear_compound="SC2",
                    front_state="USED",  rear_state="USED",
                    cold_pressure_front_bar=1.62, cold_pressure_rear_bar=1.38,
                    objective="Gearing check: confirmar que 6ª marcha llega al limitador a ~900 m de recta.",
                    telemetry_channels=["engine_rpm", "gear_pos", "bike_speed", "throttle_pos"],
                    engineer_notes=(
                        "Evaluar si el limitador electronico corta antes del punto de frenada T1. "
                        "Análisis empírico del alargamiento de 12 mm de wheelbase bajo frenada."
                    ),
                ),
                Tanda(
                    run_id="FP1-R3", laps=7,
                    front_compound="SC2", rear_compound="SC2",
                    front_state="USED",  rear_state="USED",
                    cold_pressure_front_bar=1.63, cold_pressure_rear_bar=1.40,
                    objective="Primera evaluación del anti-squat: recorrido del amortiguador trasero bajo 108% propuesto.",
                    telemetry_channels=["rear_suspension_pot", "rear_axle_accel",
                                        "wheelie_sensor", "lat_accel"],
                    engineer_notes=(
                        "Foco en la fase pick-up (0–30° de ángulo de inclinación). "
                        "Detectar squat excesivo: si hundimiento > 18 mm bajo aceleración media, "
                        "subir pivote del basculante +1 mm adicional."
                    ),
                ),
            ],
        )

    # ─────────────────────────────────────────────────────────────────────────
    def _build_practice(self) -> Session:
        return Session(
            session_type=SessionType.PRACTICE,
            name="Practice (Práctica Oficial)",
            start_time="Viernes 20/03 — 13:15",
            duration_min=55,
            conditions=(
                "Pista con primeros depósitos de goma. Temperatura asfalto 45–50°C. "
                "Humedad relativa 57%. Condición de máximo estrés térmico diurno."
            ),
            primary_objetivo=(
                "Sesión crítica: tiempos combinados para directa Q2. "
                "Evaluación termodinámica del SC1 bajo temperaturas extremas."
            ),
            runs=[
                Tanda(
                    run_id="PRAC-R1", laps=6,
                    front_compound="SC2", rear_compound="SC1",
                    front_state="NEW",   rear_state="NEW",
                    cold_pressure_front_bar=1.60, cold_pressure_rear_bar=1.30,
                    objective=(
                        "Evaluación SC1 trasero a alta temperatura. Verificar que anti-squat 108% "
                        "no sobrecalienta la banda de rodadura blanda en salidas de curvas derechas."
                    ),
                    telemetry_channels=["tire_temp_IR_rear_right", "tire_temp_IR_rear_left",
                                        "rear_suspension_pot", "throttle_pos", "lat_accel"],
                    engineer_notes=(
                        "Al regreso de pista: lectura inmediata IR en hombro derecho SC1. "
                        "Si T > 108°C → risk de ampollas confirmado → revisar mapa freno motor."
                    ),
                ),
                Tanda(
                    run_id="PRAC-R2", laps=6,
                    front_compound="SC2", rear_compound="SC1",
                    front_state="USED",  rear_state="USED",
                    cold_pressure_front_bar=1.62, cold_pressure_rear_bar=1.33,
                    objective="Termometría infrarroja de validación. Simulacro corto con goma usada.",
                    telemetry_channels=["tire_temp_IR_all", "engine_brake_map",
                                        "clutch_slip_sensor"],
                    engineer_notes=(
                        "Si la temperatura del borde derecho del SC1 excede la ventana operativa, "
                        "evaluar reducción del anti-squat a 104% y revisión del mapa de entrega de potencia."
                    ),
                ),
                Tanda(
                    run_id="PRAC-R3", laps=6,
                    front_compound="SC1", rear_compound="SC1",
                    front_state="NEW",   rear_state="NEW",
                    cold_pressure_front_bar=1.65, cold_pressure_rear_bar=1.35,
                    objective=(
                        "Time Attack oficial. SC1 delante y detrás para máximo agarre. "
                        "Combustible mínimo. Búsqueda del tiempo de corte Q2."
                    ),
                    telemetry_channels=["lap_time", "sector_times", "max_lean_angle",
                                        "max_brake_pressure", "gps_position"],
                    engineer_notes=(
                        "Instrucción al piloto: buscar rebufo (slipstream) activo en la recta de 994 m. "
                        "Ganancia estimada en Moto3: 0.3–0.5 s/vuelta bajo rebufo total."
                    ),
                ),
            ],
        )

    # ─────────────────────────────────────────────────────────────────────────
    def _build_fp2(self) -> Session:
        return Session(
            session_type=SessionType.FP2,
            name="Free Practice 2 (FP2)",
            start_time="Sábado 21/03 — 08:40",
            duration_min=30,
            conditions=(
                "Pista limpia y engomada. Temperatura mañana fresca 18–20°C ambiente. "
                "Asfalto <25°C. Menor degradación química."
            ),
            primary_objetivo=(
                "Consistencia del ritmo de carrera. Simulación con depósito lleno "
                "y evaluación del comportamiento bajo peso máximo."
            ),
            runs=[
                Tanda(
                    run_id="FP2-R1", laps=9,
                    front_compound="SC2", rear_compound="SC1",
                    front_state="USED",  rear_state="USED",
                    cold_pressure_front_bar=1.72, cold_pressure_rear_bar=1.42,
                    objective=(
                        "Simulación de carrera (endurance). Vehículo a peso reglamentario máximo. "
                        "Estudio de drop-off con alta carga y evaluación del Trail delantero bajo peso."
                    ),
                    telemetry_channels=["front_suspension_pot", "rear_suspension_pot",
                                        "fuel_level_sensor", "engine_rpm", "lap_time"],
                    engineer_notes=(
                        "NOTA: Re-calentar neumáticos usados del final de Práctica. "
                        "Todos los neumáticos NUEVOS no usados del viernes → RESERVADOS para Q2 y carrera."
                    ),
                ),
                Tanda(
                    run_id="FP2-R2", laps=8,
                    front_compound="SC2", rear_compound="SC1",
                    front_state="USED",  rear_state="USED",
                    cold_pressure_front_bar=1.72, cold_pressure_rear_bar=1.42,
                    objective=(
                        "Continuación de la tanda larga. Calibración final del mapa "
                        "electrónico de freno motor (Engine Brake) y consumo de combustible."
                    ),
                    telemetry_channels=["fuel_consumption_rate", "engine_brake_level",
                                        "clutch_slip", "rear_wheel_speed", "front_wheel_speed"],
                    engineer_notes=(
                        "Calcular consumo por vuelta para confirmar que 24 vueltas de carrera "
                        "se cubren con margen de seguridad de ≥1.5 litros."
                    ),
                ),
            ],
        )

    # ─────────────────────────────────────────────────────────────────────────
    def _build_q2(self) -> Session:
        return Session(
            session_type=SessionType.Q2,
            name="Qualifying 2 (Q2)",
            start_time="Sábado 21/03 — 13:10",
            duration_min=15,
            conditions=(
                "Pico de adherencia máximo. Altas temperaturas. "
                "Goma depositada en óptimas condiciones de capa."
            ),
            primary_objetivo=(
                "Máximo rendimiento en una única vuelta limpia. "
                "Estrategia de rebufo en recta de 994 m."
            ),
            runs=[
                Tanda(
                    run_id="Q2-R1", laps=3,
                    front_compound="SC1", rear_compound="SC1",
                    front_state="NEW",   rear_state="NEW",
                    cold_pressure_front_bar=1.68, cold_pressure_rear_bar=1.38,
                    objective=(
                        "Primer intento de tiempo. Búsqueda exhaustiva de rebufo en recta principal. "
                        "Vuelta de preparación + vuelta rápida + vuelta de enfriamiento."
                    ),
                    telemetry_channels=["lap_time", "sector_times", "speed_trap_main_straight",
                                        "max_lean_angle_T1", "trail_braking_depth_T1"],
                    engineer_notes=(
                        "Calentadores: front 90°C / rear 90°C. "
                        "Coordinar con equipo radio la posición de grupos de Moto3 para rebufo."
                    ),
                ),
                Tanda(
                    run_id="Q2-R2", laps=3,
                    front_compound="SC1", rear_compound="SC1",
                    front_state="NEW",   rear_state="NEW",
                    cold_pressure_front_bar=1.68, cold_pressure_rear_bar=1.38,
                    objective=(
                        "Segundo intento: quick swap de caucho nuevo. "
                        "Combustible escrupulosamente tasado (3 vueltas + retorno)."
                    ),
                    telemetry_channels=["lap_time", "sector_times", "max_speed",
                                        "throttle_position_T14_exit"],
                    engineer_notes=(
                        "Si el tiempo del primer intento ya asegura la pole o fila delantera, "
                        "evaluar conservar este juego SC1 para el Warm Up de reconocimiento."
                    ),
                ),
            ],
        )

    # ─────────────────────────────────────────────────────────────────────────
    def _build_warmup(self) -> Session:
        return Session(
            session_type=SessionType.WARM_UP,
            name="Warm Up",
            start_time="Domingo 22/03 — 10:40",
            duration_min=10,
            conditions="Temperatura mañana. Pista con goma de clasificación.",
            primary_objetivo=(
                "Fregar pastillas de freno nuevas. Verificar sistemas. "
                "Practice start y prueba del mordiente del embrague."
            ),
            runs=[
                Tanda(
                    run_id="WU-R1", laps=4,
                    front_compound="SC2", rear_compound="SC1",
                    front_state="USED",  rear_state="USED",
                    cold_pressure_front_bar=1.75, cold_pressure_rear_bar=1.48,
                    objective=(
                        "Fregar pastillas de freno. Practice start. "
                        "Confirmar que no hay fugas hidráulicas tras los ajustes del sábado."
                    ),
                    telemetry_channels=["brake_temp_front", "brake_temp_rear",
                                        "clutch_temp", "engine_temp"],
                    engineer_notes=(
                        "RESERVAR las unidades nuevas SC2/SC1 de carrera en calentadores. "
                        "No usar neumáticos de carrera en esta sesión bajo ningún concepto."
                    ),
                ),
            ],
        )

    # ─────────────────────────────────────────────────────────────────────────
    def _build_race(self) -> Session:
        return Session(
            session_type=SessionType.RACE,
            name="Carrera — GP de Brasil 2026",
            start_time="Domingo 22/03 — 12:00",
            duration_min=84,
            conditions=(
                "Pista seca. Temperatura ambiente proyectada 28–30°C. "
                "Asfalto 48–52°C. Peor escenario térmico del fin de semana."
            ),
            primary_objetivo=(
                "Consistencia perimetral de velocidad (24 vueltas / 92.04 km). "
                "Supervivencia térmica del hombro derecho SC1. Táctica en grupo largo."
            ),
            runs=[
                Tanda(
                    run_id="RACE", laps=24,
                    front_compound="SC2", rear_compound="SC1",
                    front_state="NEW",   rear_state="NEW",
                    cold_pressure_front_bar=1.80, cold_pressure_rear_bar=1.65,
                    objective=(
                        "24 vueltas de distancia de carrera. SC2 delantero para resistir "
                        "24 frenadas violentas en T1. SC1 trasero para tracción máxima, "
                        "supervisado por el ajuste de anti-squat 108%."
                    ),
                    telemetry_channels=[
                        "tire_temp_IR_all", "rear_suspension_pot", "front_suspension_pot",
                        "throttle_position", "lean_angle", "lat_accel", "engine_rpm",
                        "fuel_remaining", "lap_time", "sector_times",
                    ],
                    engineer_notes=(
                        "PROTOCOLO DE CARRERA — Modulación de gas: "
                        "Vueltas 1-10: apertura máxima limitada a 80% en salidas de curvas derechas. "
                        "Vueltas 11-18: apertura libre. Monitorear temperatura IR cada vuelta via telemetría. "
                        "Vueltas 19-24: si hombro derecho > 108°C, activar mapa de entrega suavizada (Mapa 3). "
                        "Presión trasera ≥1.65 bar es límite reglamentario hard — no negociable."
                    ),
                ),
            ],
        )

    # ── Resumen del fin de semana ─────────────────────────────────────────────

    def weekend_summary(self) -> dict:
        total_laps   = sum(s.total_laps() for s in self.sessions)
        total_front_new = sum(s.tires_consumed()["new_fronts"] for s in self.sessions)
        total_rear_new  = sum(s.tires_consumed()["new_rears"]  for s in self.sessions)

        return {
            "event":             self.event,
            "circuit":           self.circuit,
            "total_track_laps":  total_laps,
            "tire_usage": {
                "new_fronts_planned":  total_front_new,
                "new_rears_planned":   total_rear_new,
                "allocation_fronts":   self.tire_allocation["fronts"],
                "allocation_rears":    self.tire_allocation["rears"],
                "fronts_remaining":    self.tire_allocation["fronts"] - total_front_new,
                "rears_remaining":     self.tire_allocation["rears"]  - total_rear_new,
            },
            "sessions": [
                {
                    "name":        s.name,
                    "start_time":  s.start_time,
                    "duration_min": s.duration_min,
                    "runs":        len(s.runs),
                    "total_laps":  s.total_laps(),
                }
                for s in self.sessions
            ],
        }
