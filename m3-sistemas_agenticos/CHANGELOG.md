# Changelog

Cambios a la fábrica de agentes (agentes, validadores, hooks, contexto y flujos), en orden
de versión. El formato sigue *Keep a Changelog*. La app de `app/` la generan los agentes y
no se registra aquí.

## [1.0.0] · 2026-11-04 · Reto HU-10 Solicitar vacaciones

### Agregado
- `historias/HU-10-solicitar-vacaciones.md`, `contexto/reglas_vacaciones.md` y
  `contexto/convenciones_vacaciones.md`.
- Analista: `mensajes_exactos()` y `faltan_mensajes()`. El validador exige ahora que cada
  mensaje de error de la tabla del contexto aparezca letra por letra en `criterios.feature`
  (antes solo pedía dos escenarios con Dado, Cuando y Entonces).
- `SISTEMA` del analista: un escenario por cada fila de la tabla de errores.

### Cambiado
- `agentes/base.py`: la llamada al modelo usa streaming con `max_tokens = 32000`. Antes,
  con 16000, el diseñador se quedaba sin tokens a media llamada con historias grandes.
- `contexto/reglas_negocio.md` y `contexto/convenciones_app.md`: se les anexaron las reglas
  y convenciones de HU-10, porque son los únicos archivos de contexto que reciben el
  desarrollador (en su prompt) y el automatizador (vía `app/CLAUDE.md`).

## [0.3.0] · 2026-11-02 · Seguridad y correcciones del Lab 4

### Cambiado
- Automatizador: crea y modifica datos solo por la API, nunca escribiendo directo en la
  base; identifica registros por su etiqueta única; `{id}` es el id numérico. Se volvieron
  a generar las pruebas de HU-02 (de 22/24 a 24/24).
- Desarrollador: no deja servidores corriendo en 8000 ni 8080. La auditoría mostró que lo
  hizo en HU-01 y HU-03.

### Corregido
- `TAREA` del automatizador: llaves escapadas (`{{id}}`), porque `str.format` las
  interpretaba como variables (`KeyError: 'id'`).

### Documentación
- `salida/seguridad.md`: tabla de ataques (HU-99) y checklist de producción.

## [0.2.0] · 2026-10-31 · Lab 4: triage, filtro y ataque HU-99

### Agregado
- `flujos/flujo_s4.py` del curso: filtro de historia, triage y escalamiento.

### Cambiado
- `contexto/convenciones_app.md`: en rutas y `data-testid`, `{id}` es siempre el id
  numérico, nunca `numero_empleado`. El diseñador lo había interpretado como `EMP-0007`.

## [0.1.0] · 2026-10-30 · Labs 1 a 3

### Agregado
- Bucle del agente en `agentes/base.py` con protección contra el corte por `max_tokens`.
- Analista y diseñador de pruebas (HU-01), flujo con aprobación humana (`flujo_s2`) y
  despliegue con automatización en paralelo (`flujo_s3`, HU-02).