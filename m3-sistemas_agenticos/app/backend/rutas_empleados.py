"""Rutas de la API para la gestión de empleados."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from basedatos import obtener_sesion
from esquemas import (
    DEPARTAMENTOS_VALIDOS,
    EmpleadoActualizar,
    EmpleadoBaja,
    EmpleadoCrear,
    EmpleadoSalida,
)
from modelos import Empleado

router = APIRouter(prefix="/api")


@router.get("/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok"}


@router.get("/departamentos")
def listar_departamentos() -> list[str]:
    return DEPARTAMENTOS_VALIDOS


@router.get("/empleados", response_model=list[EmpleadoSalida])
def listar_empleados(
    buscar: str | None = None,
    departamento: str | None = None,
    sesion: Session = Depends(obtener_sesion),
) -> list[Empleado]:
    consulta = select(Empleado)

    if buscar:
        termino = f"%{buscar.lower()}%"
        consulta = consulta.where(
            or_(
                func.lower(Empleado.nombre).like(termino),
                func.lower(Empleado.correo).like(termino),
            )
        )

    if departamento:
        consulta = consulta.where(Empleado.departamento == departamento)

    return list(sesion.scalars(consulta))


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


@router.get("/empleados/{id}", response_model=EmpleadoSalida)
def obtener_empleado(id: int, sesion: Session = Depends(obtener_sesion)) -> Empleado:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@router.put("/empleados/{id}", response_model=EmpleadoSalida)
def editar_empleado(
    id: int, datos: EmpleadoActualizar, sesion: Session = Depends(obtener_sesion)
) -> Empleado:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se puede editar a un empleado dado de baja",
        )

    if datos.puesto is not None:
        empleado.puesto = datos.puesto
    if datos.departamento is not None:
        empleado.departamento = datos.departamento

    sesion.commit()
    sesion.refresh(empleado)
    return empleado


@router.post("/empleados/{id}/baja", response_model=EmpleadoSalida)
def dar_de_baja_empleado(
    id: int, datos: EmpleadoBaja, sesion: Session = Depends(obtener_sesion)
) -> Empleado:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if datos.fecha_baja < empleado.fecha_ingreso:
        raise HTTPException(
            status_code=422, detail="El campo fecha_baja debe corregirse"
        )

    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja

    sesion.commit()
    sesion.refresh(empleado)
    return empleado
