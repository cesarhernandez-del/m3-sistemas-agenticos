"""Punto de entrada de la API de gestión de empleados."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from basedatos import Base, motor
from rutas_empleados import router
from rutas_vacaciones import router as router_vacaciones

Base.metadata.create_all(bind=motor)

app = FastAPI(title="Gestión de empleados")
app.include_router(router)
app.include_router(router_vacaciones)


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, excepcion: RequestValidationError
) -> JSONResponse:
    """Traduce los errores de validación de Pydantic a {"detail": mensaje en español}."""
    primer_error = excepcion.errors()[0]
    campo = primer_error["loc"][-1]
    mensaje = primer_error.get("msg", "").removeprefix("Value error, ")

    if campo == "correo" and mensaje:
        detalle = mensaje
    else:
        detalle = f"El campo {campo} debe corregirse"

    return JSONResponse(status_code=422, content={"detail": detalle})
