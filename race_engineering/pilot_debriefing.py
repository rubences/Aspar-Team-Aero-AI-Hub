"""
pilot_debriefing.py — Protocolo estructurado de interrogación al piloto.

Implementa la batería de preguntas de debriefing post-sesión diseñada para
correlacionar la percepción del piloto con los datos de telemetría del
Autódromo de Goiânia. Específico para la validación del archivo maestro
de la prueba de concepto.

Las preguntas están estructuradas en 3 fases según el informe técnico GP Brasil 2026.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class DebriefingPhase(str, Enum):
    PHASE_1_STRAIGHT_BRAKING  = "FASE_1_RECTA_FRENADA"
    PHASE_2_CORNERING_THERMAL = "FASE_2_CURVA_TERMICA"
    PHASE_3_ANTISQUAT_TRACTION = "FASE_3_ANTISQUAT_TRACCION"


class ResponseScale(str, Enum):
    """Escala Likert adaptada para respuestas de ingeniería de pista."""
    MUY_NEGATIVO   = "1 — Comportamiento inaceptable / requiere cambio mayor"
    NEGATIVO       = "2 — Por debajo de lo esperado / ajuste necesario"
    NEUTRAL        = "3 — Aceptable pero mejorable"
    POSITIVO       = "4 — Por encima de lo esperado / validación positiva"
    MUY_POSITIVO   = "5 — Comportamiento óptimo / hipótesis confirmada"


@dataclass
class DebriefingQuestion:
    question_id: str
    phase: DebriefingPhase
    context_geographic: str        # Localización geográfica exacta en el circuito
    engineering_hypothesis: str    # La hipótesis que se valida con esta pregunta
    question_text: str             # Pregunta al piloto
    expected_positive_response: str # Respuesta que valida la hipótesis
    failure_indicator: str         # Respuesta que indica problema mecánico
    telemetry_crosscheck_channels: List[str]   # Canales de telemetría para correlacionar
    corrective_action_if_fail: str # Ajuste mecánico propuesto si la hipótesis falla


@dataclass
class PilotResponse:
    question_id: str
    scale_rating: int         # 1–5
    verbatim_note: str
    lap_reference: Optional[int] = None
    session: Optional[str]    = None


@dataclass
class DebriefingSession:
    session_name: str
    pilot_name: str
    responses: List[PilotResponse] = field(default_factory=list)

    def add_response(self, response: PilotResponse):
        self.responses.append(response)

    def correlation_score(self) -> float:
        """Puntuación media de correlación hipótesis–percepción (1–5)."""
        if not self.responses:
            return 0.0
        return round(sum(r.scale_rating for r in self.responses) / len(self.responses), 2)

    def failed_hypotheses(self, threshold: int = 2) -> List[str]:
        """Devuelve los IDs de preguntas cuya respuesta indica fallo mecánico."""
        return [r.question_id for r in self.responses if r.scale_rating <= threshold]


class PilotDebriefingProtocol:
    """
    Batería de interrogación protocolizada para el GP de Brasil 2026 — Goiânia.

    Estructura en 3 fases que cubren la validación de las hipótesis dinámicas
    del archivo maestro:
        · Fase 1: Recta + Frenada T1 (Wheelbase / Gearing / Trail)
        · Fase 2: Curvas asimétricas (Agilidad / Térmica del neumático)
        · Fase 3: Anti-Squat / Tracción / Electrónica
    """

    def __init__(self):
        self.questions = self._build_question_bank()

    def _build_question_bank(self) -> List[DebriefingQuestion]:
        return [

            # ════════════════════════════════════════════════════════════════
            # FASE 1 — RECTA PRINCIPAL + FRENADA T1
            # ════════════════════════════════════════════════════════════════

            DebriefingQuestion(
                question_id="F1-Q1",
                phase=DebriefingPhase.PHASE_1_STRAIGHT_BRAKING,
                context_geographic=(
                    "Recta principal de 994 m, zona de los 800 m marcados en la barrera, "
                    "curva T1 (frenada crítica)."
                ),
                engineering_hypothesis=(
                    "La relación final de transmisión (14T/40T) permite al motor alcanzar "
                    "la zona roja en 6ª marcha sin que el limitador corte la aceleración antes "
                    "del punto de frenada, y sin que la resistencia aerodinámica aplaste la curva de potencia."
                ),
                question_text=(
                    "Durante la progresión por la recta de 994 metros, cuando accionas la sexta marcha "
                    "más allá de la señal de los 800 metros, prestando atención al limitador de revoluciones: "
                    "¿Percibes que la entrega de potencia sufre un aplanamiento dramático al cruzar la barrera "
                    "del viento, impidiendo llegar a las RPM óptimas antes de buscar el freno, o sentimos un "
                    "corte violento contra el limitador que nos obliga a cortar gas anticipadamente?"
                ),
                expected_positive_response=(
                    "La sexta marcha satura suavemente el limitador exactamente en el punto de frenada. "
                    "No hay recorte abrupto ni aplanamiento de curva de potencia."
                ),
                failure_indicator=(
                    "El motor toca el limitador con más de 50 metros de margen ANTES del punto de frenada "
                    "(→ reducir corona trasera a 38T) o nunca llega a la zona roja "
                    "(→ aumentar la corona a 42T)."
                ),
                telemetry_crosscheck_channels=["engine_rpm", "gear_pos", "bike_speed",
                                               "throttle_pos", "gps_distance_from_T1"],
                corrective_action_if_fail=(
                    "Recalcular FDR. Si corta antes: corona 38T (FDR 2.714). "
                    "Si no llega: corona 42T (FDR 3.0). Recalcular anti-squat tras cambio."
                ),
            ),

            DebriefingQuestion(
                question_id="F1-Q2",
                phase=DebriefingPhase.PHASE_1_STRAIGHT_BRAKING,
                context_geographic=(
                    "Punto de frenada máxima hacia T1. "
                    "Máxima compresión de la horquilla delantera. "
                    "Velocidad de entrada estimada 238 km/h."
                ),
                engineering_hypothesis=(
                    "El incremento de +12 mm en la distancia entre ejes aumenta el brazo de palanca "
                    "resistivo al cabeceo (pitching), manteniendo la rueda trasera en contacto con "
                    "el asfalto durante la frenada máxima y evitando el snake o chatter."
                ),
                question_text=(
                    "Abordando la frenada hacia la Curva 1 desde máxima velocidad, asumiendo que hemos "
                    "alargado la distancia entre ejes en 12 milímetros: en el momento de la máxima "
                    "compresión de la horquilla delantera y la máxima presión en la maneta derecha, "
                    "¿sientes que el tren trasero se eleva y oscila lateralmente (snake o chatter), "
                    "o la motocicleta se mantiene relativamente aplomada, permitiendo que la retención "
                    "del freno motor estabilice la trayectoria de entrada?"
                ),
                expected_positive_response=(
                    "El tren trasero se mantiene asentado. La frenada es lineal y predecible. "
                    "No hay snake ni oscilación. La rueda trasera no se levanta."
                ),
                failure_indicator=(
                    "Tren trasero se eleva (wheelie inverso) antes del punto de frenada ideal, "
                    "y/o se detecta chatter o snake en la fase de frenada máxima."
                ),
                telemetry_crosscheck_channels=["rear_suspension_pot", "front_brake_pressure",
                                               "rear_wheel_speed", "wheelie_sensor",
                                               "gyro_pitch_rate"],
                corrective_action_if_fail=(
                    "Si snake o chatter: incrementar wheelbase a +16 mm. "
                    "Si elevación trasera: reducir altérate del freno motor (Engine Brake Map). "
                    "Si la elevación persiste: revisar distribución estática de peso."
                ),
            ),

            DebriefingQuestion(
                question_id="F1-Q3",
                phase=DebriefingPhase.PHASE_1_STRAIGHT_BRAKING,
                context_geographic=(
                    "Entrada a T1: trail braking desde 120 m hasta el ápice. "
                    "Ángulo de inclinación progresivo hasta ~52°."
                ),
                engineering_hypothesis=(
                    "La reducción del ángulo de lanzamiento en -0.5° (bajando las tijas 4 mm) "
                    "aumenta la agilidad de entrada manteniendo el Trail en la ventana operativa "
                    "(82–95 mm) para evitar el cierre de dirección bajo trail braking."
                ),
                question_text=(
                    "Una vez iniciada la inclinación en T1, mientras liberas gradualmente la presión "
                    "del freno delantero (trail braking) entrando en el ápice, hemos bajado las tijas "
                    "de la horquilla reduciendo el avance (Trail) estático: ¿Notas un subviraje "
                    "contumaz que te empuja ancho, o percibes pesadez o una tendencia agresiva en "
                    "la dirección a 'caer' cerrándose (tuck-in) de forma impredecible?"
                ),
                expected_positive_response=(
                    "La dirección cae natural y predeciblemente hacia el ápice. "
                    "Sin subviraje. Sin tuck-in. El Trail proporciona feedback táctil sólido."
                ),
                failure_indicator=(
                    "La rueda delantera tiende a cerrarse de golpe bajo trail braking "
                    "(Trail demasiado corto → subir tijas 2 mm) o la moto empuja "
                    "al exterior de forma sistemática (Trail excesivo → bajar tijas 2 mm más)."
                ),
                telemetry_crosscheck_channels=["steering_angle", "front_brake_pressure",
                                               "lean_angle", "front_suspension_pot",
                                               "lat_accel_front"],
                corrective_action_if_fail=(
                    "Tuck-in: subir tijas 2 mm (aumentar Trail). "
                    "Subviraje: bajar tijas 2 mm adicionales (reducir Trail 3–4 mm más). "
                    "Correlacionar siempre con el offset de las tijas antes de decidir."
                ),
            ),

            # ════════════════════════════════════════════════════════════════
            # FASE 2 — CURVAS ASIMÉTRICAS / AGILIDAD / THERMAL
            # ════════════════════════════════════════════════════════════════

            DebriefingQuestion(
                question_id="F2-Q1",
                phase=DebriefingPhase.PHASE_2_CORNERING_THERMAL,
                context_geographic=(
                    "Chicane técnica T3–T4 y sector mixto T9–T11. "
                    "Transiciones cambio de dirección a media velocidad."
                ),
                engineering_hypothesis=(
                    "A pesar del alargamiento del wheelbase (+12 mm), la reducción del Rake "
                    "y la distribución de peso ligeramente delantera mantienen la agilidad "
                    "de giro en un nivel aceptable para las transiciones de media velocidad."
                ),
                question_text=(
                    "A la hora de enlazar cambios de dirección a media velocidad (mid-speed "
                    "transitions), dado que el chasis se ha alargado para tolerar la recta: "
                    "¿percibes una resistencia viscosa que te obliga a ejercer una fuerza de "
                    "contra-manillar extenuante, o la distribución de pesos delantera logra "
                    "que la moto caiga fluida hacia el interior del viraje opuesto?"
                ),
                expected_positive_response=(
                    "La motocicleta cae fluidamente al siguiente viraje con un esfuerzo "
                    "de contra-manillar moderado. La adaptación al wheelbase largo es tolerable."
                ),
                failure_indicator=(
                    "Contra-manillar extremo en cada transición OR la moto no quiere caer "
                    "al viraje contrario y el piloto llega tarde al ápice opuesto."
                ),
                telemetry_crosscheck_channels=["steering_torque_sensor", "lean_angle_rate",
                                               "lateral_accel_transitions"],
                corrective_action_if_fail=(
                    "Reducir wheelbase a +8 mm (compromiso menor). "
                    "Alternativamente, reducir el Rake adicional -0.3° más (bajar tijas +2 mm). "
                    "Revisar distribución de peso: mover la batería/masa hacia el frontal 5 mm."
                ),
            ),

            DebriefingQuestion(
                question_id="F2-Q2",
                phase=DebriefingPhase.PHASE_2_CORNERING_THERMAL,
                context_geographic=(
                    "T6 y T7 (curvas rápidas derechas de alta carga): tras 10 vueltas en Practice. "
                    "Máximo ángulo de inclinación estimado 55–58° sobre hombro derecho."
                ),
                engineering_hypothesis=(
                    "El neumático trasero SC1 bajo asimetría 9:5 R/L y temperatura de asfalto "
                    "45–50°C no sufre degradación catastrófica en el hombro derecho antes de "
                    "completar una tanda de clasificación (6 vueltas intense)."
                ),
                question_text=(
                    "Dadas las nueve curvas hacia la derecha que estresan térmicamente ese flanco, "
                    "después de acumular diez vueltas seguidas en la Práctica: al llegar al máximo "
                    "ángulo de inclinación sobre el costado derecho, ¿se materializa una caída "
                    "abrupta y esponjosa del agarre (indicio de abrasión o ampollas en el compuesto "
                    "blando SC1), o la merma del neumático es un descenso predecible que te permite "
                    "sobrellevar la trazada?"
                ),
                expected_positive_response=(
                    "La degradación del hombro derecho es gradual y predecible. "
                    "El piloto siente el grip retroceder de forma lineal, no en un colapso abrupto."
                ),
                failure_indicator=(
                    "Colapso abrupto del agarre en el hombro derecho en curvas rápidas derechas "
                    "(→ blistering confirmado: cambiar a SC2 trasero o reducir el anti-squat a 104%)."
                ),
                telemetry_crosscheck_channels=["tire_temp_IR_rear_right", "rear_slip_ratio",
                                               "lean_angle_T6_T7", "rear_suspension_pot"],
                corrective_action_if_fail=(
                    "Emergencia SC1: cambiar a SC2 trasero para todas las sesiones restantes. "
                    "Reducir presiones traseras a 1.70 bar caliente para minimizar deformación. "
                    "Revisar si el anti-squat 108% genera excess heat por sobre-tracción."
                ),
            ),

            # ════════════════════════════════════════════════════════════════
            # FASE 3 — ANTI-SQUAT / TRACCIÓN / INTERACCIÓN ELECTRÓNICA
            # ════════════════════════════════════════════════════════════════

            DebriefingQuestion(
                question_id="F3-Q1",
                phase=DebriefingPhase.PHASE_3_ANTISQUAT_TRACTION,
                context_geographic=(
                    "Ápice de T5, T6 y T12 (curvas rápidas peraltadas a la derecha). "
                    "Primer toque de aceleración con ~45° de inclinación."
                ),
                engineering_hypothesis=(
                    "El anti-squat al 108%–112% (pivote +2 mm) mantiene la suspensión "
                    "trasera suficientemente extendida bajo la primera apertura de gas, "
                    "evitando el squat excesivo que destruye el radio de giro y "
                    "provoca subviraje de salida."
                ),
                question_text=(
                    "A la salida de las largas curvas peraltadas, en la fracción exacta de segundo "
                    "en que reanudas el primer toque de aceleración (initial throttle) estando "
                    "inclinado sobre el borde del neumático: ¿la parte posterior de la moto se hunde "
                    "lánguidamente (squat), forzando el morro hacia afuera e impidiendo cerrar el "
                    "radio de giro, o por el contrario notas que la zaga se mantiene erguida bajo "
                    "tensión, proporcionando empuje hacia adelante?"
                ),
                expected_positive_response=(
                    "La zaga se mantiene firme. La moto gira sobre sí misma sin empujar al exterior. "
                    "El empuje es inmediato y lineal hacia la recta principal."
                ),
                failure_indicator=(
                    "El trasero se hunde bajo el primer acelerador (squat excesivo → bajar anti-squat). "
                    "O bien la moto se levanta violentamente del interior (jacking extremo → bajar pivote)."
                ),
                telemetry_crosscheck_channels=["rear_suspension_pot", "throttle_pos",
                                               "lean_angle", "rear_axle_lift",
                                               "chassis_roll_rate"],
                corrective_action_if_fail=(
                    "Squat excesivo: subir pivote +1 mm adicional (→113–115%). "
                    "Jacking extremo: bajar pivote 1 mm (→106%). "
                    "En ambos casos recalcular la interacción con la nueva relación de cadena."
                ),
            ),

            DebriefingQuestion(
                question_id="F3-Q2",
                phase=DebriefingPhase.PHASE_3_ANTISQUAT_TRACTION,
                context_geographic=(
                    "Fase de pick-up tras T12 y T13: enderezamiento del chasis "
                    "hacia la recta principal. Aceleración al máximo."
                ),
                engineering_hypothesis=(
                    "Si el neumático trasero SC1 entra en la región de deslizamiento "
                    "(wheelspin controlado), el anti-squat elevado convierte ese slip "
                    "en un vector de impulso limpio sin retroalimentación oscilatoria (pogo)."
                ),
                question_text=(
                    "En el momento de aplicar la plena aceleración mientras vas enderezando el chasis "
                    "(pick-up phase), si el parche de contacto de la rueda trasera SC1 entra en la "
                    "región del deslizamiento (wheelspin): ¿ese deslizamiento se transforma en un "
                    "impulso que te catapulta con presteza en dirección a la recta principal, o por "
                    "el contrario desencadena un efecto de rebote elástico oscilatorio (efecto pogo) "
                    "que contamina todo el chasis e impide engranar las marchas con suavidad?"
                ),
                expected_positive_response=(
                    "El wheelspin se siente controlado y se convierte en tracción neta. "
                    "La aceleración es rectilínea. No hay pogo ni vibración de alta frecuencia."
                ),
                failure_indicator=(
                    "Pogo o chatter de alta frecuencia durante el pick-up "
                    "(→ reducir spring rate trasero o revisar amortiguación de rebote)."
                ),
                telemetry_crosscheck_channels=["rear_wheel_speed", "front_wheel_speed",
                                               "rear_slip_ratio", "chassis_vibration_sensor",
                                               "engine_rpm", "gear_changes"],
                corrective_action_if_fail=(
                    "Pogo estructural: reducir rebote trasero 2 clicks. "
                    "Pogo de alta frecuencia: revisar fijaciones del basculante y rodamientos del pivote. "
                    "Wheelspin incontrolado: ajustar traction control map (ATC); reducir umbral 1 step."
                ),
            ),

            DebriefingQuestion(
                question_id="F3-Q3",
                phase=DebriefingPhase.PHASE_3_ANTISQUAT_TRACTION,
                context_geographic=(
                    "Reducciones de marcha en T1 y T3 con la moto vertical. "
                    "Frenada combinada freno/freno motor."
                ),
                engineering_hypothesis=(
                    "La interacción entre el mapa de freno motor y el embrague antirrebote "
                    "es correcta: no genera ni exceso de retardo (que fuerza al piloto a usar "
                    "más freno manual) ni rebote del tren trasero."
                ),
                question_text=(
                    "Por último, evaluando la interacción entre la mecánica y los mapas electrónicos: "
                    "en las reducciones que abordamos en seco, ¿sientes la intervención del freno "
                    "motor del propulsor en sintonía con la limitación de deslizamiento del embrague, "
                    "o el efecto de la compresión acentúa excesivamente el retardo forzándote a "
                    "aplicar más esfuerzo manual sobre los frenos?"
                ),
                expected_positive_response=(
                    "El freno motor complementa la frenada manual de forma natural. "
                    "El rebote del tren trasero está controlado por el embrague antirrebote."
                ),
                failure_indicator=(
                    "El motor frena demasiado (→ reducir EB 1 step en el mapa). "
                    "El tren trasero bota en las reducciones (→ ajustar presión del slipper clutch)."
                ),
                telemetry_crosscheck_channels=["engine_brake_torque", "rear_wheel_speed",
                                               "rear_suspension_pot_rebound",
                                               "front_brake_pressure", "clutch_slip_sensor"],
                corrective_action_if_fail=(
                    "Exceso EB: reducir Engine Brake Map 1–2 steps. "
                    "Rebote trasero en reducción: incrementar la presión del slipper clutch 0.5 bar. "
                    "Verificar siempre la correlación entre el nivel de EB y el anti-squat establecido."
                ),
            ),
        ]

    # ── Métodos de servicio ────────────────────────────────────────────────────

    def get_phase_questions(self, phase: DebriefingPhase) -> List[DebriefingQuestion]:
        return [q for q in self.questions if q.phase == phase]

    def format_for_engineer(self) -> List[dict]:
        """Exporta la batería en formato estructurado para el ingeniero de pista."""
        result = []
        for q in self.questions:
            result.append({
                "id":              q.question_id,
                "phase":           q.phase,
                "ubicacion":       q.context_geographic,
                "hipotesis":       q.engineering_hypothesis,
                "pregunta_piloto": q.question_text,
                "respuesta_ok":    q.expected_positive_response,
                "indicador_fallo": q.failure_indicator,
                "telemetria":      q.telemetry_crosscheck_channels,
                "accion_correctiva": q.corrective_action_if_fail,
            })
        return result

    def evaluate_session(
        self,
        debriefing_session: DebriefingSession,
    ) -> dict:
        """
        Correlaciona las respuestas del piloto con las hipótesis de ingeniería
        y genera las acciones correctivas priorizadas.
        """
        failed = debriefing_session.failed_hypotheses(threshold=2)
        score  = debriefing_session.correlation_score()

        actions = []
        for qid in failed:
            q = next((x for x in self.questions if x.question_id == qid), None)
            if q:
                actions.append({
                    "question_id":    qid,
                    "phase":          q.phase,
                    "action":         q.corrective_action_if_fail,
                    "telemetry":      q.telemetry_crosscheck_channels,
                })

        return {
            "session":            debriefing_session.session_name,
            "pilot":              debriefing_session.pilot_name,
            "correlation_score":  score,
            "hypothesis_status":  "VALIDADA" if score >= 3.5 else "PARCIAL" if score >= 2.5 else "REQUIERE REVISIÓN MAYOR",
            "failed_hypotheses":  failed,
            "corrective_actions": actions,
            "poc_status": (
                "ARCHIVO MAESTRO VALIDADO — Continuar con configuración propuesta"
                if not failed else
                f"AJUSTES REQUERIDOS EN {len(failed)} HIPÓTESIS — Ver acciones correctivas"
            ),
        }
