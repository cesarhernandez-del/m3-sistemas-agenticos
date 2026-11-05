# Decisiones · HU-10 Solicitar vacaciones

Corrida final: 4 de noviembre de 2026, `flujos/flujo_s4`, con defensas. Estado LISTA,
0 ciclos de triage, 1.72 USD, 42 pruebas pasan y 2 se omiten (ver punto 2).

## 1. ¿Qué es workflow y qué es agente?

Es **workflow** todo lo que decide el código: el orden de las etapas en `construir_grafo()`,
las compuertas (`despues_de_filtrar`, `despues_de_verificar`, `despues_de_e2e`), los
reintentos con `MAX_INTENTOS = 2` y `MAX_CICLOS = 2`, `verificar_app` y pytest. El filtro
de historia también es workflow, aunque use un modelo: llena un `Veredicto` en un paso
fijo y no decide qué sigue. Son **agentes** el analista y el diseñador (deciden qué leer y
cuándo escribir dentro de su bucle) y los tres de Claude Code (el desarrollador construyó
en 32 turnos que él mismo eligió). El triage es el único punto donde un modelo decide el
siguiente paso del grafo; en esta corrida no hizo falta.

## 2. ¿Cómo se validó cada salida y qué atrapó algún validador?

- Criterios: `validar_gherkin` más un chequeo que agregué a la fábrica, que exige los 8
  mensajes exactos de `convenciones_vacaciones.md`. El validador original solo pedía dos
  escenarios. El analista lo cumplió en el intento 1, así que en esta corrida no atrapó nada.
- Casos: contrato Pydantic dentro de `guardar_casos` y `validar_plan`; pasó en el intento 1.
- Código: `verificar_app` (arranca y compila) y después pytest como árbitro.
- **Lo que sí se atrapó:** en la primera corrida, el diseñador se quedó sin tokens a media
  llamada a `guardar_casos`. La protección de `base.py` lanzó `RuntimeError` por
  `max_tokens` en lugar de seguir con un archivo vacío.
- Las 2 omisiones son pruebas E2E del 404 y del 409: la pantalla no muestra el botón para
  esos empleados. Revisé que las dos reglas sí estén probadas en `tests/api/test_hu_10.py`
  con código y mensaje exactos. El diseñador les asignó nivel `e2e` cuando eran de `api`.

## 3. ¿Dónde intervine y qué vi para decidir?

Rechacé el primer plan. Tenía bien el orden de validación, pero no decía los códigos
400/409, el conteo inclusivo de días, «días hábiles» en plural con N = 1, el mensaje de
éxito exacto ni el año por defecto del GET. Además proponía «cerrar los otros
formularios», el mismo cambio que en HU-03 ocultó el alta. El segundo plan incorporó los
seis puntos y lo aprobé. Al final revisé el motivo de las omisiones (`pytest -rs`) y
comprobé la app con curl: 404 y 409 exactos, fin de semana rechazado y del 14 al 18 de
septiembre de 2026 = 4 días hábiles.

## 4. ¿Qué arquitectura usa la fábrica y por qué no otra?

Un supervisor determinista con flujo definido (encadenamiento, enrutamiento,
paralelización y evaluador-optimizador), con `salida/HU-xx/` como pizarra. Los pasos se
conocen de antemano, así que un supervisor con LLM en cada paso añadiría costo y
variación sin ganar nada. Red y traspasos dejarían el orden a los modelos y serían
difíciles de auditar. Jerárquica no se justifica con seis agentes.

## 5. ¿Qué corregí en los agentes y por qué no en su resultado?

- **Contexto:** el desarrollador y el automatizador solo leen `reglas_negocio.md` y
  `convenciones_app.md`; anexé ahí las reglas de HU-10 para que les llegaran.
- **Analista:** el chequeo de mensajes exactos del punto 2.
- **Bucle:** streaming con `max_tokens = 32000` tras el corte del diseñador.
- **Automatizador** (antes del reto): crear datos solo por la API. Lo volví a correr sobre
  HU-02 y las pruebas pasaron de 22/24 a 24/24.
- **Desarrollador:** no dejar servidores en 8000 u 8080. La auditoría mostró que los dejó
  en HU-01 y HU-03; como es solo una instrucción, el control real es revisar los puertos.

Corregir el resultado a mano lo arreglaría una vez; corregir al agente hace que la
siguiente historia salga bien, y `auditoria.jsonl` demuestra que nada en `app/` ni en
`salida/` lo editó una persona.