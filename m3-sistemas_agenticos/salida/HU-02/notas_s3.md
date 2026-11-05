# Notas · Sesión 3 · HU-02 Consultar directorio

## 1. Contenedores (`docker compose ps`)

<pega aquí la salida>

## 2. Pruebas (`python -m pytest tests -q`)

<pega aquí la salida: cuántas pasaron, cuántas fallaron y cuáles>

## 3. Intento fuera de rol (auditoría)

`buscar_denegados.py` no encontró intentos de escritura fuera de rol: los agentes
respetaron sus carpetas en esta ejecución.

Verifiqué que el resultado no fuera un falso negativo: la auditoría registró 20
escrituras (desarrollador 14, despliegue 3, automatizador 3) y el script reconoció
la ruta en las 20. También confirmé que el diccionario `PERMITIDO` del script
coincide con las listas `ESCRITURA` de `desarrollador.py`, `despliegue.py` y
`automatizador.py`.

Observación: `seguridad/hooks.py` abre `auditoria.jsonl` en modo `"a"`, así que el
archivo acumula todas las ejecuciones. Las 14 escrituras del desarrollador pueden
incluir la corrida de HU-01 del Lab 2. Para el reto hay que borrarlo antes de la
ejecución final.

## 4. Aprobación del plan de HU-02

El primer plan decía explícitamente que extendía el código de HU-01 sin romper el
POST, pero lo rechacé por dos huecos:

- Dejaba abierto «a decidir en implementación» cómo mostrar la lista vacía (mensaje
  `sin-resultados` o tabla vacía). La prueba E2E del automatizador busca un
  `data-testid` concreto, así que una decisión abierta podía romperla.
- Justificaba la búsqueda sin distinguir mayúsculas con «ambos ya se guardan en
  minúsculas o se normaliza con `func.lower()`». En HU-01 solo el correo se guarda en
  minúsculas; el nombre no. Además, `lower()` de SQLite solo convierte ASCII, así que
  no resuelve acentos.

Comentario de rechazo: <pega el texto exacto que escribiste>

¿El segundo plan lo incorporó?: <sí / no / parcialmente, y qué cambió>

## 5. Comparación con la tabla manual del Lab 2

<si hiciste la tabla de notas_s2.md: qué coincide y qué no.
Si no la hiciste: «No hice la revisión manual del 2C, así que no hay tabla con qué
comparar»>

## 6. Hallazgos sobre lo que propuso el modelo

- En el plan de HU-01, el modelo justificó usar regex «en lugar de `.endswith`, para
  evitar correos como `a@noempresa.com`». La razón es falsa:
  `"a@noempresa.com".endswith("@empresa.com")` ya devuelve `False`. La regex no está
  mal, pero el argumento suena técnico sin ser cierto. Hay que verificar las
  justificaciones del modelo, no solo su código.
- En HU-02, el plan decidió por su cuenta que un departamento inválido no es error y
  devuelve lista vacía, y que el directorio muestra también a los empleados dados de
  baja. Son decisiones que no venían en la instrucción.

## 7. Preguntas de cierre

- **¿Qué arquitectura tiene la fábrica después de flujo_s3?** Un workflow orquestado
  por código, es decir, un supervisor determinista: `construir_grafo()` fija el orden
  y ningún modelo decide quién sigue. Dentro de algunos nodos hay agentes (ReAct en
  los agentes 1 y 2, Claude Code en el 3, 4 y 5). `salida/HU-xx/` y el estado del
  grafo funcionan como pizarra.
- **¿Por qué despliegue y automatizador pueden ir en paralelo y el desarrollador no?**
  Porque el automatizador solo necesita `casos_prueba.json` y los `data-testid` de las
  convenciones para escribir las pruebas, no la app corriendo. Los dos dependen de lo
  que construye el desarrollador, por eso él va antes.
- **Con 15 agentes, ¿cambiaría de topología?** A una jerárquica, agrupando por equipos
  (análisis, desarrollo, calidad, despliegue), para que ningún supervisor tenga que
  elegir entre 15. A cambio se pierde detalle en cada resumen entre niveles y aumentan
  la latencia y el costo.