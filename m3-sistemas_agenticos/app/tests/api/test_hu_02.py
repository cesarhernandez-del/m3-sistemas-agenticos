"""Pruebas de API para HU-02: directorio de empleados.

Cada caso crea sus propios empleados con un identificador único (uuid)
incrustado en el nombre o el correo, y usa ese identificador como término
de búsqueda para aislar sus resultados del resto de los datos que ya
existan en la base (en lugar de asumir que la base está vacía).
"""

import sqlite3
import uuid
from datetime import date, datetime
from pathlib import Path

import httpx
import pytest

RUTA_BASE_DATOS = Path(__file__).resolve().parents[2] / "backend" / "datos" / "empleados.db"


def _crear_empleado(
    url_api: str,
    nombre: str,
    puesto: str = "Analista",
    departamento: str = "Tecnología",
    correo: str | None = None,
) -> dict:
    """Crea un empleado vía la API y regresa el objeto creado."""
    payload = {
        "nombre": nombre,
        "correo": correo or f"empleado.{uuid.uuid4().hex[:10]}@empresa.com",
        "puesto": puesto,
        "departamento": departamento,
        "fecha_ingreso": "2024-01-15",
    }
    respuesta = httpx.post(f"{url_api}/api/empleados", json=payload)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _insertar_empleado_baja(nombre: str, correo: str, puesto: str, departamento: str) -> dict:
    """Inserta directamente en la base un empleado con estado 'baja'.

    HU-02 solo expone lectura del directorio: la API no tiene (todavía) un
    endpoint para dar de baja a un empleado. Para preparar esta precondición
    se inserta el registro directo en la base SQLite que usa el backend.
    Si la base no es accesible desde donde corren las pruebas (por ejemplo,
    el backend corre en un contenedor sin el volumen montado), el caso se
    omite en vez de fallar por un problema de entorno ajeno a HU-02.
    """
    if not RUTA_BASE_DATOS.exists():
        pytest.skip(
            f"No se encontró la base de datos del backend en {RUTA_BASE_DATOS}; "
            "no se puede preparar un empleado con estado 'baja'."
        )

    numero_empleado = f"EMP-{9000 + (uuid.uuid4().int % 999):04d}"
    hoy = date.today().isoformat()
    ahora = datetime.utcnow().isoformat(sep=" ")

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    try:
        cursor = conexion.execute(
            """
            INSERT INTO empleados
                (numero_empleado, nombre, correo, puesto, departamento,
                 fecha_ingreso, estado, fecha_baja, creado_en)
            VALUES (?, ?, ?, ?, ?, ?, 'baja', ?, ?)
            """,
            (numero_empleado, nombre, correo, puesto, departamento, hoy, hoy, ahora),
        )
        conexion.commit()
        id_empleado = cursor.lastrowid
    finally:
        conexion.close()

    return {
        "id": id_empleado,
        "numero_empleado": numero_empleado,
        "nombre": nombre,
        "correo": correo,
        "estado": "baja",
    }


def test_cp01_ver_directorio_completo(url_api: str) -> None:
    """CP-01: Ver el directorio completo de empleados."""
    etiqueta = uuid.uuid4().hex[:8]
    _crear_empleado(url_api, nombre=f"Ana Torres {etiqueta}", puesto="Analista", departamento="Tecnología")
    _crear_empleado(url_api, nombre=f"Luis Pérez {etiqueta}", puesto="Ejecutivo", departamento="Ventas")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": etiqueta})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 2
    for empleado in cuerpo:
        for campo in ("numero_empleado", "nombre", "puesto", "departamento", "estado"):
            assert campo in empleado


def test_cp03_buscar_por_nombre_sin_distinguir_mayusculas(url_api: str) -> None:
    """CP-03: Buscar por nombre sin distinguir mayúsculas de minúsculas."""
    etiqueta = uuid.uuid4().hex[:8]
    nombre = f"Ana Torres {etiqueta}"
    _crear_empleado(url_api, nombre=nombre)

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": f"ANA TORRES {etiqueta}".lower()})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert any(empleado["nombre"] == nombre for empleado in cuerpo)


def test_cp05_buscar_por_correo_sin_distinguir_mayusculas(url_api: str) -> None:
    """CP-05: Buscar por correo sin distinguir mayúsculas de minúsculas."""
    etiqueta = uuid.uuid4().hex[:10]
    correo = f"luis.perez.{etiqueta}@empresa.com"
    _crear_empleado(url_api, nombre="Luis Pérez", correo=correo)

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": correo.upper()})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert any(empleado["correo"] == correo for empleado in cuerpo)


def test_cp07_filtrar_por_departamento(url_api: str) -> None:
    """CP-07: Filtrar empleados por departamento."""
    etiqueta = uuid.uuid4().hex[:8]
    _crear_empleado(url_api, nombre=f"Empleado Tec Uno {etiqueta}", departamento="Tecnología")
    _crear_empleado(url_api, nombre=f"Empleado Tec Dos {etiqueta}", departamento="Tecnología")
    _crear_empleado(url_api, nombre=f"Empleado Ventas {etiqueta}", departamento="Ventas")

    respuesta = httpx.get(
        f"{url_api}/api/empleados", params={"buscar": etiqueta, "departamento": "Tecnología"}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 2
    assert all(empleado["departamento"] == "Tecnología" for empleado in cuerpo)


def test_cp09_buscar_texto_sin_coincidencias(url_api: str) -> None:
    """CP-09: Buscar un texto que no coincide con ningún empleado."""
    etiqueta = uuid.uuid4().hex[:8]
    _crear_empleado(url_api, nombre=f"Ana Torres {etiqueta}")

    texto_sin_coincidencia = f"sin-coincidencias-{uuid.uuid4().hex}"
    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": texto_sin_coincidencia})

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cp11_empleado_baja_sigue_en_directorio(url_api: str) -> None:
    """CP-11: Un empleado dado de baja sigue apareciendo en el directorio."""
    etiqueta = uuid.uuid4().hex[:8]
    nombre = f"Sofía Díaz {etiqueta}"
    correo = f"sofia.diaz.{etiqueta}@empresa.com"
    _insertar_empleado_baja(nombre, correo, puesto="Analista", departamento="Tecnología")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": etiqueta})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    coincidencias = [empleado for empleado in cuerpo if empleado["nombre"] == nombre]
    assert len(coincidencias) == 1
    assert coincidencias[0]["estado"] == "baja"
