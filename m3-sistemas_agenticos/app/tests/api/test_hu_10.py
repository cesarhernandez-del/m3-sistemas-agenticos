"""Pruebas de API para HU-10: solicitar vacaciones.

Cada caso crea su propio empleado vía la API con un correo único (uuid)
para poder repetirse sin choques con datos existentes. Las rutas usan el
id numérico del empleado (no numero_empleado), según las convenciones de
la aplicación.
"""

import uuid

import httpx


def _crear_empleado(
    url_api: str,
    fecha_ingreso: str,
    nombre: str = "Vacaciones Prueba",
    puesto: str = "Analista",
    departamento: str = "Ventas",
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


def _dar_de_baja(url_api: str, id_empleado: int, fecha_baja: str) -> dict:
    """Da de baja a un empleado vía la API y regresa el objeto actualizado."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/baja", json={"fecha_baja": fecha_baja}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _solicitar_vacaciones(
    url_api: str, id_empleado: int, fecha_inicio: str, fecha_fin: str
) -> httpx.Response:
    """Envía una solicitud de vacaciones vía la API sin afirmar el resultado."""
    return httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def test_cp01_registrar_solicitud_valida(url_api: str) -> None:
    """CP-01: Registrar una solicitud de vacaciones válida."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["empleado_id"] == empleado["id"]
    assert cuerpo["dias_habiles"] == 5
    assert cuerpo["dias_restantes"] == 7


def test_cp03_festivos_y_fin_de_semana_no_se_descuentan(url_api: str) -> None:
    """CP-03: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2025-12-21")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-21", "2026-12-31")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 8
    assert cuerpo["dias_restantes"] == 4


def test_cp05_rechaza_empleado_inexistente(url_api: str) -> None:
    """CP-05: Rechazar la solicitud cuando el empleado no existe."""
    respuesta = _solicitar_vacaciones(url_api, 9999, "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp07_rechaza_empleado_dado_de_baja(url_api: str) -> None:
    """CP-07: Rechazar la solicitud de un empleado dado de baja."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-01-01")
    _dar_de_baja(url_api, empleado["id"], fecha_baja="2024-06-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp09_rechaza_fin_anterior_a_inicio(url_api: str) -> None:
    """CP-09: Rechazar cuando la fecha de fin es anterior a la fecha de inicio."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-10", "2026-07-06")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp11_rechaza_periodo_que_cruza_de_anio(url_api: str) -> None:
    """CP-11: Rechazar un periodo que cruza de un año a otro."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-28", "2027-01-08")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp13_rechaza_anio_sin_tabla_de_festivos(url_api: str) -> None:
    """CP-13: Rechazar un año que no está en la tabla de festivos."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2023-01-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2025-07-06", "2025-07-10")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp15_rechaza_sin_un_anio_de_antiguedad(url_api: str) -> None:
    """CP-15: Rechazar una solicitud sin un año de antigüedad cumplido."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2025-12-21")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-18", "2026-12-18")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp17_rechaza_periodo_sin_dias_habiles(url_api: str) -> None:
    """CP-17: Rechazar un periodo sin ningún día hábil."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-11", "2026-07-12")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp19_rechaza_solicitud_que_rebasa_dias_disponibles(url_api: str) -> None:
    """CP-19: Rechazar una solicitud que rebasa los días disponibles del año."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")

    for fecha_inicio, fecha_fin in (
        ("2026-07-06", "2026-07-10"),
        ("2026-07-13", "2026-07-17"),
        ("2026-07-20", "2026-07-21"),
    ):
        consumo = _solicitar_vacaciones(url_api, empleado["id"], fecha_inicio, fecha_fin)
        assert consumo.status_code == 201, consumo.text

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-11-02", "2026-11-02")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )
