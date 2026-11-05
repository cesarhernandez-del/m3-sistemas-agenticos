"""Reglas de negocio de las solicitudes de vacaciones (HU-10)."""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos import Vacaciones

DIAS_TOPE_ANUAL = 12

# Festivos oficiales (Ley Federal del Trabajo, art. 74) para los años soportados.
FESTIVOS: dict[int, set[date]] = {
    2026: {
        date(2026, 1, 1),
        date(2026, 2, 2),
        date(2026, 3, 16),
        date(2026, 5, 1),
        date(2026, 9, 16),
        date(2026, 11, 16),
        date(2026, 12, 25),
    },
    2027: {
        date(2027, 1, 1),
        date(2027, 2, 1),
        date(2027, 3, 15),
        date(2027, 5, 1),
        date(2027, 9, 16),
        date(2027, 11, 15),
        date(2027, 12, 25),
    },
}


def contar_dias_habiles(inicio: date, fin: date) -> int:
    """Cuenta los días que no son sábado, domingo ni festivo, incluyendo ambos extremos."""
    festivos = FESTIVOS.get(inicio.year, set())
    dias = 0
    actual = inicio
    while actual <= fin:
        if actual.weekday() < 5 and actual not in festivos:
            dias += 1
        actual += timedelta(days=1)
    return dias


def _fecha_mas_un_anio(fecha: date) -> date:
    """Suma un año a la fecha; el 29 de febrero cae en 1 de marzo si el año siguiente no es bisiesto."""
    try:
        return fecha.replace(year=fecha.year + 1)
    except ValueError:
        return date(fecha.year + 1, 3, 1)


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    """Indica si ya se cumplió al menos un año de antigüedad en la fecha de inicio solicitada."""
    return fecha_inicio >= _fecha_mas_un_anio(fecha_ingreso)


def obtener_solicitudes_anio(
    sesion: Session, empleado_id: int, anio: int
) -> list[Vacaciones]:
    """Solicitudes del empleado cuyo periodo cae en el año dado (los periodos no cruzan años)."""
    solicitudes = sesion.scalars(
        select(Vacaciones).where(Vacaciones.empleado_id == empleado_id)
    ).all()
    return [s for s in solicitudes if s.fecha_inicio.year == anio]
