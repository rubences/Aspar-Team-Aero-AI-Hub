# Engram Context — Memoria Persistente del Proyecto

Este directorio almacena decisiones de arquitectura, contexto técnico y conocimiento
acumulado del proyecto Aspar SmartOps Aero Hub.

## Estructura

- `decisions/` — ADRs (Architecture Decision Records)
- `specs/` — Especificaciones en Markdown para desarrollo guiado por IA
- `snapshots/` — Instantáneas del contexto del agente de desarrollo

## Decisiones Clave

### ADR-001: MCP como protocolo de integración universal
Todos los conectores de datos exponen una interfaz MCP estándar para garantizar
compatibilidad con cualquier agente de IA presente y futuro.

### ADR-002: PINN + GRU para predicción aerodinámica
Se combinan Physics-Informed Neural Networks (física del problema) con redes GRU
(patrones temporales) para maximizar precisión y explicabilidad.

### ADR-003: LangGraph para orquestación multi-agente
Se utiliza LangGraph en lugar de soluciones ad-hoc para el flujo de trabajo
multi-agente, permitiendo ciclos, ramificaciones y gestión de estado.

### ADR-004: Edge RAG Engine para recuperación ultrarrápida
Se implementa un motor RAG en memoria para consultas sub-milisegundo durante
decisiones críticas en pista.
