"""Pruebas de API para HU-03: editar empleado y darlo de baja.

Cada caso crea su propio empleado vía la API con un correo único (uuid)
para poder repetirse sin choques con datos existentes. Las rutas usan el
id numérico del empleado (no numero_empleado), según las convenciones de
la aplicación.
"""

import uuid

import httpx


def _crear_empleado(
    url_api: str,
    nombre: str = "Ana Gómez",
    puesto: str = "Analista",
    departamento: str = "Ventas",
    fecha_ingreso: str = "2022-03-01",
    correo: str | None = None,
) -> dict:
    """Crea un empleado vía la API y regresa el objeto creado."""
    payload = {
        "nombre": nombre,
        "correo": correo or f"empleado.{uuid.uuid4().hex[:10]}@empresa.com",
        "puesto": puesto,
        "departamento": departamento,
        "fecha_ingreso": fecha_ingreso,
    }
    respuesta = httpx.post(f"{url_api}/api/empleados", json=payload)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cp01_editar_puesto_y_departamento_empleado_activo(url_api: str) -> None:
    """CP-01: Editar puesto y departamento de un empleado activo."""
    empleado = _crear_empleado(url_api, puesto="Analista", departamento="Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}",
        json={"puesto": "Analista Senior", "departamento": "Tecnología"},
    )

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["puesto"] == "Analista Senior"
    assert cuerpo["departamento"] == "Tecnología"
    assert cuerpo["numero_empleado"] == empleado["numero_empleado"]
    assert cuerpo["correo"] == empleado["correo"]

    verificacion = httpx.get(f"{url_api}/api/empleados/{empleado['id']}")
    assert verificacion.status_code == 200
    cuerpo_verificado = verificacion.json()
    assert cuerpo_verificado["puesto"] == "Analista Senior"
    assert cuerpo_verificado["departamento"] == "Tecnología"
    assert cuerpo_verificado["numero_empleado"] == empleado["numero_empleado"]
    assert cuerpo_verificado["correo"] == empleado["correo"]


def test_cp03_error_editar_departamento_fuera_de_catalogo(url_api: str) -> None:
    """CP-03: Error al editar con un departamento fuera del catálogo."""
    empleado = _crear_empleado(url_api, puesto="Analista", departamento="Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}",
        json={"departamento": "Marketing"},
    )

    assert respuesta.status_code == 422
    assert "departamento" in respuesta.json()["detail"]


def test_cp05_error_editar_puesto_demasiado_corto(url_api: str) -> None:
    """CP-05: Error al editar con un puesto demasiado corto."""
    empleado = _crear_empleado(url_api, puesto="Analista", departamento="Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}",
        json={"puesto": "A"},
    )

    assert respuesta.status_code == 422
    assert "puesto" in respuesta.json()["detail"]


def test_cp07_error_editar_empleado_dado_de_baja(url_api: str) -> None:
    """CP-07: Error al intentar editar a un empleado dado de baja."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2020-01-01")
    baja = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja",
        json={"fecha_baja": "2024-01-01"},
    )
    assert baja.status_code == 200, baja.text

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}",
        json={"puesto": "Coordinador"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"


def test_cp09_dar_de_baja_empleado_activo(url_api: str) -> None:
    """CP-09: Dar de baja a un empleado activo."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2022-03-01")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja",
        json={"fecha_baja": "2024-06-15"},
    )

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "baja"
    assert cuerpo["fecha_baja"] == "2024-06-15"

    verificacion = httpx.get(f"{url_api}/api/empleados/{empleado['id']}")
    assert verificacion.status_code == 200
    cuerpo_verificado = verificacion.json()
    assert cuerpo_verificado["estado"] == "baja"
    assert cuerpo_verificado["fecha_baja"] == "2024-06-15"

    listado = httpx.get(f"{url_api}/api/empleados", params={"buscar": empleado["correo"]})
    assert listado.status_code == 200
    assert any(item["id"] == empleado["id"] for item in listado.json())


def test_cp11_error_dar_de_baja_fecha_anterior_a_ingreso(url_api: str) -> None:
    """CP-11: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2022-03-01")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja",
        json={"fecha_baja": "2022-01-01"},
    )

    assert respuesta.status_code == 422
    assert "fecha_baja" in respuesta.json()["detail"]
