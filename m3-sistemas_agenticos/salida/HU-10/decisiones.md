# Decisiones · HU-10 Solicitar vacaciones
Corrida final: 4 de noviembre de 2026, `flujos/flujo_s4`, con defensas. Estado LISTA,
0 ciclos de triage, 1.72 USD, 42 pruebas pasan y 2 se omiten.

## 1. ¿Qué es workflow y qué es agente?

Es **workflow** lo que decide el código: el orden de `construir_grafo()`, las compuertas,
los reintentos (`MAX_INTENTOS = 2`, `MAX_CICLOS = 2`), `verificar_app` y pytest. El filtro
también lo es aunque use un modelo: llena un `Veredicto` en un paso fijo. Son **agentes**
el analista y el diseñador, que deciden qué leer y cuándo escribir, y los tres de Claude
Code (el desarrollador eligió sus 32 turnos). El triage es el único punto donde un modelo
decide el siguiente paso; en esta corrida no hizo falta.

## 2. ¿Cómo se validó cada salida y qué atrapó algún validador?

- Criterios: `validar_gherkin` más un chequeo que agregué, que exige los 8 mensajes
  exactos del contexto (el original solo pedía dos escenarios). Pasó en el intento 1.
- Casos: contrato Pydantic en `guardar_casos` y `validar_plan`; pasó en el intento 1.
- Código: `verificar_app` y luego pytest como árbitro.
- **Lo que se atrapó:** en la primera corrida el diseñador se quedó sin tokens a media
  llamada, y `base.py` lanzó `RuntimeError` en lugar de seguir con un archivo vacío.
- Las 2 omisiones son E2E del 404 y el 409: la pantalla no ofrece botón para esos
  empleados. Ambas reglas están probadas en la API con código y mensaje exactos.

## 3. ¿Dónde intervine y qué vi para decidir?

Rechacé el primer plan: no decía los códigos 400/409, el conteo inclusivo, «días hábiles»
con N = 1, el mensaje de éxito exacto ni el año por defecto del GET, y proponía cerrar
formularios como el cambio que en HU-03 ocultó el alta. El segundo incorporó los seis
puntos y lo aprobé. Después revisé las omisiones (`pytest -rs`) y probé con curl: 404 y
409 exactos, fin de semana rechazado y del 14 al 18 de septiembre = 4 días hábiles.

## 4. ¿Qué arquitectura usa la fábrica y por qué no otra?

Supervisor determinista con flujo definido (encadenamiento, enrutamiento, paralelización
y evaluador-optimizador) y `salida/HU-xx/` como pizarra. Los pasos se conocen de
antemano: un supervisor con LLM añadiría costo y variación. Red y traspasos dejarían el
orden a los modelos y serían difíciles de auditar; jerárquica no se justifica con 6
agentes.

## 5. ¿Qué corregí en los agentes y por qué no en su resultado?

- **Contexto:** anexé las reglas de HU-10 a los dos archivos que reciben el desarrollador
  y el automatizador.
- **Analista:** el chequeo de mensajes exactos.
- **Bucle:** streaming con `max_tokens = 32000` tras el corte del diseñador.
- **Automatizador:** datos solo por la API; HU-02 pasó de 22/24 a 24/24.
- **Desarrollador:** no dejar servidores en 8000 u 8080, como mostró la auditoría.

Corregir el resultado lo arregla una vez; corregir al agente arregla la siguiente
historia, y `auditoria.jsonl` demuestra que nada en `app/` ni `salida/` lo editó una
persona.