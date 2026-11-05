# Fábrica de software con agentes · Módulo 3

Una cadena de seis agentes que convierte una historia de usuario en una aplicación de gestión de empleados desplegada y probada:

| # | Agente | Entrada | Salida | Sesión |
| --- | --- | --- | --- | --- |
| 1 | Analista | Historia de usuario | `salida/HU-xx/criterios.feature` | 1 |
| 2 | Diseñador de pruebas | Criterios | `salida/HU-xx/casos_prueba.json` | 1 |
| 3 | Desarrollador (Claude Code) | Criterios y casos | `app/backend`, `app/frontend` | 2 |
| 4 | Despliegue (Claude Code) | Código | Contenedores con Docker Compose | 3 |
| 5 | Automatizador (Claude Code) | Casos de prueba | `app/tests` (pytest + Playwright) | 3 |
| 6 | Flujo E2E con triage | Pruebas y app desplegada | `salida/HU-xx/reporte.md` | 4 |

## Requisitos

Python 3.12, Node 20 o superior, Docker Desktop, Claude Code y una clave de API de Anthropic con créditos.

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
playwright install chromium
cp .env.example .env        # escribe ANTHROPIC_API_KEY y MODEL
```

## Uso

```bash
# Sesión 1: agentes por separado
python -m agentes.analista historias/HU-01-registrar-empleado.md
python -m agentes.disenador_pruebas salida/HU-01/criterios.feature

# Sesiones 2 a 4: la fábrica completa, cada vez con más agentes
python -m flujos.flujo_s2 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s3 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s4 historias/HU-01-registrar-empleado.md
```

Los patrones de cada sesión también tienen un ejemplo corto y ejecutable en [`ejemplos/`](ejemplos/README.md), por ejemplo `python -m ejemplos.s2_flujos.enrutamiento`.

La aplicación queda en http://localhost:8080 y la documentación de la API en http://localhost:8000/docs.

## Instalación por sistema operativo

### Mac (Apple Silicon, con Colima)

```bash
brew install uv node colima docker docker-compose
colima start --cpu 4 --memory 6        # Colima no arranca solo: brew services start colima
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env                    # ANTHROPIC_API_KEY y MODEL
```

### Linux

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
python -m playwright install --with-deps chromium
cp .env.example .env
docker info > /dev/null && echo "Docker listo"
```

### Windows (PowerShell)

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m playwright install chromium
Copy-Item .env.example .env
setx PYTHONUTF8 1                       # una vez; luego cierra y abre la terminal
```

Ejecuta todo desde la raíz del repositorio y con el entorno activado.

## Ejecutar una historia completa (ejemplo: el reto HU-10)

```bash
lsof -i :8000 -i :8080                  # deben estar libres o con el reenvío de Docker
python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md
```

El flujo se detiene dos veces para pedir tu decisión: si hay preguntas abiertas y para
aprobar el plan. Escribe `si` o tu comentario de rechazo. El resultado queda en
`salida/HU-10/reporte.md`.

Para agregar una historia nueva: copia la historia a `historias/` y anexa sus reglas y
convenciones al final de `contexto/reglas_negocio.md` y `contexto/convenciones_app.md`,
que son los archivos que reciben el desarrollador y el automatizador.

## Pruebas

```bash
cd app
docker compose up -d
python -m pytest tests -q -rs           # -rs muestra el motivo de cada prueba omitida
```

## Defensas

Los hooks de `seguridad/hooks.py` confinan la escritura, la lectura y los comandos de cada
agente, y registran cada intento en `auditoria.jsonl`. `DEFENSAS=0` apaga los de seguridad
y solo se usa para demostrar ataques en clase. El reporte está en `salida/seguridad.md`.

## Problemas frecuentes en esta instalación

| Síntoma | Causa | Qué hacer |
| --- | --- | --- |
| `failed to connect to the docker API ... colima` | Colima apagado | `colima start` |
| Pruebas que crean datos y no los encuentran | Un uvicorn local en `localhost:8000` | `lsof -i :8000` y cierra el proceso de Python |
| `RuntimeError: ... max_tokens` | Salida demasiado grande | Ya resuelto con streaming en `agentes/base.py` |
| `KeyError` al armar un prompt | Llaves sin escapar en un texto con `format` | Escribe `{{id}}` |

Los cambios a la fábrica están en `CHANGELOG.md`.