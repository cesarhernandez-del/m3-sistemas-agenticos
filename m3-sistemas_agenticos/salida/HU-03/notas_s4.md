# Notas · Sesión 4 · HU-03 Editar y dar de baja

## 4A · Fábrica completa con HU-03

**Estado final:** ESCALAR A UNA PERSONA · 2 ciclos de corrección · 3.54 USD

### Aprobación del plan

El primer plan proponía migrar los `data-testid` y las rutas de `id` a
`numero_empleado`, tocando código de HU-01 y HU-02 («lo trato como corrección»).
Lo verifiqué contra `contexto/convenciones_app.md`: todos los testid usan `{id}` y
las pruebas de HU-02 usan `empleado['id']`. HU-02 cumplía la convención; el error
venía de `casos_prueba.json`, donde el diseñador leyó `{id}` como `EMP-0007`
(fallo en cascada, ASI08).

Comentario de rechazo:
> No migres los data-testid ni las rutas a numero_empleado. Según
> convenciones_app.md, {id} es el campo id numérico del recurso, el mismo que ya
> usan HU-02 y sus pruebas. Las rutas nuevas son GET /api/empleados/{id},
> PUT /api/empleados/{id} y POST /api/empleados/{id}/baja, y los testid nuevos son
> editar-empleado-{id} y baja-empleado-{id} con el id numérico. No modifiques el
> alta ni el directorio de HU-01 y HU-02.

El segundo plan lo incorporó: rutas con `{id}`, testid con `empleado.id`, sin
tocar la tabla, la búsqueda ni el alta. Lo aprobé. Dos observaciones que no
ameritaban otro rechazo:
- El mensaje del 422 de fecha de baja lo redactó el modelo; el criterio solo dice
  que la pantalla indique el campo `fecha_baja`.
- Dar de baja a quien ya está de baja no está cubierto ni en los criterios ni en el
  plan (el primer plan respondía 409).

Corrección en la fábrica: agregué a `contexto/convenciones_app.md` que `{id}` en
rutas y data-testid es siempre el id numérico, nunca `numero_empleado`, para que
la ambigüedad no se repita en HU-10 (commit aparte).

### Lo que decidió el triage

| Ciclo | Resultado de pruebas | Triage eligió | Causa que dio |
| --- | --- | --- | --- |
| 1 | 7 fallas, 17 pasan | desarrollador | Al dar de baja, el empleado desaparece del directorio |
| 2 | 10 fallas, 14 pasan | automatizador | Las filas `fila-empleado-88…100` nunca aparecen; las pruebas no esperan bien |
| — | 10 fallas, 14 pasan | — | Escala a una persona al agotar MAX_CICLOS |

En el ciclo 1, la corrección del desarrollador costó 65 turnos y 1.70 USD,
aumentó las fallas de 7 a 10 y cambió `App.jsx` para ocultar el formulario de
alta mientras se edita (no lo pidió nadie).

### Diagnóstico de causa raíz (lo hice yo, no el triage)

1. Las pruebas de HU-02 no habían cambiado desde el Lab 3
   (`git diff --stat -- app/tests` vacío) y ahora fallaban: el problema no estaba
   en ellas.
2. Las pruebas buscaban los ids 163 y 164, pero la API del 8080 tenía como máximo
   el 149: los datos se estaban creando en otra base.
3. `lsof -i :8000` mostró dos procesos: `ssh` (reenvío de Colima al contenedor) y
   un `python` en `localhost:8000`, un uvicorn que quedó vivo tras `verificar`.
   Las pruebas (`URL_API = http://localhost:8000`) le pegaban a ese backend local.
   Al cerrarlo: **de 10 fallas a 2**, con todas las de HU-03 pasando.
4. Las 2 restantes (`test_cp11` y `test_cp12`, «baja sigue en directorio», de
   HU-02) usan `_insertar_empleado_baja`, que escribe directo en SQLite porque en
   HU-02 no había endpoint de baja. Descarté con evidencia: otro archivo (es el
   mismo `empleados.db`), filtro por estado (no existe), búsqueda (funciona),
   Unicode (ambos NFC).
5. Experimento: insertar desde la Mac y consultar la API cada segundo dio
   0 resultados durante 7.2 s. Tras `docker compose restart backend`, el registro
   apareció. La base vive en la Mac y el contenedor la lee por la carpeta
   compartida de Colima; el backend no ve a tiempo lo que escribe la Mac.

| Fallas | Causa real | Responsable correcto | Qué dijo el triage |
| --- | --- | --- | --- |
| 8 | uvicorn local en `localhost:8000` interceptando las llamadas de las pruebas | La fábrica: `verificar` no apaga su servidor | Ciclo 2: automatizador ✗ |
| 2 | La prueba escribe directo en SQLite y el contenedor no lo ve a tiempo | Automatizador: la prueba depende del entorno en lugar de usar la API | Ciclo 1: desarrollador ✗ |

**Conclusión:** ninguna de las 10 fallas era un defecto de la app. El triage no
acertó en ninguno de los dos ciclos porque las causas estaban en el entorno y en
el diseño de las pruebas, y él solo ve fallos y criterios: no ve puertos,
volúmenes ni procesos. Su catálogo (desarrollador, automatizador, despliegue) no
tiene la opción «entorno».

### Cambios pendientes en la fábrica antes del reto

- Automatizador: crear y modificar datos solo por la API, nunca directo en la base.
- `verificar`: apagar el servidor que levanta, o usar un puerto distinto al 8000.
- Antes de cada corrida: `lsof -i :8000 -i :8080` debe mostrar solo `ssh`.

## 4B · Atacar y defender con HU-99

<pendiente: conteo del paso 1 (ingenuo vs. endurecido), dos corridas del paso 2,
bloqueo del paso 3 y evidencia del paso 4>

## Preguntas de cierre

- **¿Estás de acuerdo con el agente que eligió el triage?** No, en ninguno de los
  dos ciclos (ver diagnóstico).
- **¿Qué componente del agente de la sesión 1 pone realmente el límite?** Las
  herramientas y su lista de rutas permitidas, no el prompt ni el modelo.
- **¿Dónde pondrías a una persona para una historia sospechosa?** Después de
  `filtrar_historia`, con un `interrupt` que muestre el motivo, en lugar de
  terminar el flujo directo.
- **¿Qué capa detuvo HU-99?** 4B: el conteo del paso 1, el resultado de las dos 
  corridas del paso 2 y el bloqueo del paso 3.
  Pregunta «¿qué capa detuvo HU-99?»: el filtro (filtrar_historia) bloqueó la historia completa. 
  Además, la ruta permitida del analista (base.py) le habría impedido leer el señuelo aunque el filtro fallara. 
  Son dos capas.