"""Rutas de la API para la gestión de empleados."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from basedatos import obtener_sesion
from esquemas import DEPARTAMENTOS_VALIDOS, EmpleadoCrear, EmpleadoSalida
from modelos import Empleado

router = APIRouter(prefix="/api")


@router.get("/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok"}


@router.get("/departamentos")
def listar_departamentos() -> list[str]:
    return DEPARTAMENTOS_VALIDOS


@router.post("/empleados", response_model=EmpleadoSalida, status_code=201)
def crear_empleado(
    datos: EmpleadoCrear, sesion: Session = Depends(obtener_sesion)
) -> Empleado:
    if datos.fecha_ingreso > date.today():
        raise HTTPException(
            status_code=422, detail="La fecha de ingreso no puede ser futura"
        )

    existente = sesion.scalar(select(Empleado).where(Empleado.correo == datos.correo))
    if existente is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    total_empleados = sesion.scalar(select(func.count()).select_from(Empleado))
    numero_empleado = f"EMP-{total_empleados + 1:04d}"

    empleado = Empleado(
        numero_empleado=numero_empleado,
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
    )
    sesion.add(empleado)
    sesion.commit()
    sesion.refresh(empleado)
    return empleado
