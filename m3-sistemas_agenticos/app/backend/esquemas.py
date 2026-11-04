"""Esquemas Pydantic de entrada y salida para empleados."""

import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

DEPARTAMENTOS_VALIDOS = [
    "Tecnología",
    "Ventas",
    "Finanzas",
    "Recursos Humanos",
    "Operaciones",
]

PATRON_CORREO_CORPORATIVO = re.compile(r"^[^@\s]+@empresa\.com$")


class EmpleadoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: str
    puesto: str = Field(min_length=2, max_length=60)
    departamento: str
    fecha_ingreso: date

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        correo_normalizado = valor.strip().lower()
        if not PATRON_CORREO_CORPORATIVO.match(correo_normalizado):
            raise ValueError("Usa el correo corporativo @empresa.com")
        return correo_normalizado

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        if valor not in DEPARTAMENTOS_VALIDOS:
            raise ValueError("departamento no es válido")
        return valor


class EmpleadoActualizar(BaseModel):
    puesto: str | None = Field(default=None, min_length=2, max_length=60)
    departamento: str | None = None

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str | None) -> str | None:
        if valor is not None and valor not in DEPARTAMENTOS_VALIDOS:
            raise ValueError("departamento no es válido")
        return valor


class EmpleadoBaja(BaseModel):
    fecha_baja: date


class EmpleadoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: date | None
    creado_en: datetime


class VacacionesCrear(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class SolicitudVacacionesResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int


class VacacionesSalida(BaseModel):
    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int
    dias_restantes: int


class SaldoVacacionesSalida(BaseModel):
    empleado_id: int
    anio: int
    dias_usados: int
    dias_disponibles: int
    solicitudes: list[SolicitudVacacionesResumen]
