"""Rutas de la API para solicitar y consultar vacaciones (HU-10)."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from basedatos import obtener_sesion
from esquemas import SaldoVacacionesSalida, VacacionesCrear, VacacionesSalida
from modelos import Empleado, Vacaciones
from vacaciones import (
    DIAS_TOPE_ANUAL,
    FESTIVOS,
    contar_dias_habiles,
    cumple_antiguedad,
    obtener_solicitudes_anio,
)

router = APIRouter(prefix="/api")


@router.post(
    "/empleados/{id}/vacaciones", response_model=VacacionesSalida, status_code=201
)
def solicitar_vacaciones(
    id: int, datos: VacacionesCrear, sesion: Session = Depends(obtener_sesion)
) -> dict:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )

    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )

    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = datos.fecha_inicio.year
    if anio not in FESTIVOS:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    if not cumple_antiguedad(empleado.fecha_ingreso, datos.fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    dias_habiles = contar_dias_habiles(datos.fecha_inicio, datos.fecha_fin)
    if dias_habiles == 0:
        raise HTTPException(
            status_code=400, detail="El periodo no incluye días hábiles"
        )

    dias_usados = sum(
        s.dias_habiles for s in obtener_solicitudes_anio(sesion, id, anio)
    )
    dias_disponibles = DIAS_TOPE_ANUAL - dias_usados

    if dias_habiles > dias_disponibles:
        raise HTTPException(
            status_code=400,
            detail=(
                "La solicitud excede los días disponibles: "
                f"quedan {dias_disponibles} días hábiles"
            ),
        )

    solicitud = Vacaciones(
        empleado_id=id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_habiles,
    )
    sesion.add(solicitud)
    sesion.commit()
    sesion.refresh(solicitud)

    return {
        "id": solicitud.id,
        "empleado_id": id,
        "fecha_inicio": solicitud.fecha_inicio,
        "fecha_fin": solicitud.fecha_fin,
        "dias_habiles": solicitud.dias_habiles,
        "dias_restantes": dias_disponibles - dias_habiles,
    }


@router.get("/empleados/{id}/vacaciones", response_model=SaldoVacacionesSalida)
def consultar_saldo_vacaciones(
    id: int, anio: int | None = None, sesion: Session = Depends(obtener_sesion)
) -> dict:
    empleado = sesion.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    anio_consulta = anio if anio is not None else date.today().year
    solicitudes = obtener_solicitudes_anio(sesion, id, anio_consulta)
    dias_usados = sum(s.dias_habiles for s in solicitudes)

    return {
        "empleado_id": id,
        "anio": anio_consulta,
        "dias_usados": dias_usados,
        "dias_disponibles": DIAS_TOPE_ANUAL - dias_usados,
        "solicitudes": solicitudes,
    }
