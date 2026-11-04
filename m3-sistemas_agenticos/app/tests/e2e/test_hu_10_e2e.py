"""Pruebas E2E para HU-10: solicitar vacaciones.

Cada caso crea su propio empleado vía la API con un correo único (uuid) y
usa el id numérico devuelto para ubicar la fila y los controles en la
interfaz (fila-empleado-{id}, vacaciones-abrir-{id}, etc.), según las
convenciones de data-testid de la aplicación.

CP-06 y CP-08 piden llegar al formulario de vacaciones de un empleado sin
usar el botón de su fila (empleado inexistente o dado de baja). La pantalla
de vacaciones (VacacionesEmpleado.jsx) solo se monta desde el directorio al
hacer clic en ese botón y recibe el empleado como prop; no existe una ruta
propia (por ejemplo /vacaciones/{id}) para abrirla directamente. Por eso
esos dos casos solo automatizan la parte verificable (el botón no aparece)
y se marcan como "skipped" en la parte que requiere forzar el envío sin
pasar por el botón: es un hueco de la aplicación para reportar al equipo de
desarrollo, no algo que esta prueba deba resolver.
"""

import uuid

import httpx
import pytest
from playwright.sync_api import Page, expect


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


def _solicitar_vacaciones_api(
    url_api: str, id_empleado: int, fecha_inicio: str, fecha_fin: str
) -> httpx.Response:
    """Envía una solicitud de vacaciones vía la API, usada para preparar datos."""
    return httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def _ir_a_empleado(page: Page, url_web: str, empleado: dict) -> None:
    """Navega al directorio y filtra por el correo del empleado para aislarlo."""
    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(empleado["correo"])
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def _abrir_vacaciones_y_enviar(
    page: Page, id_empleado: int, fecha_inicio: str, fecha_fin: str
) -> None:
    """Abre el formulario de vacaciones del empleado y envía la solicitud."""
    page.get_by_test_id(f"vacaciones-abrir-{id_empleado}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill(fecha_inicio)
    page.get_by_test_id("vacaciones-fecha-fin").fill(fecha_fin)
    page.get_by_test_id("vacaciones-enviar").click()


def test_cp02_registrar_solicitud_valida(page: Page, url_api: str, url_web: str) -> None:
    """CP-02: Registrar una solicitud de vacaciones válida."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")
    _ir_a_empleado(page, url_web, empleado)

    _abrir_vacaciones_y_enviar(page, empleado["id"], "2026-07-06", "2026-07-10")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."
    )


def test_cp04_festivos_y_fin_de_semana_no_se_descuentan(
    page: Page, url_api: str, url_web: str
) -> None:
    """CP-04: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2025-12-21")
    _ir_a_empleado(page, url_web, empleado)

    _abrir_vacaciones_y_enviar(page, empleado["id"], "2026-12-21", "2026-12-31")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."
    )


def test_cp06_rechaza_empleado_inexistente(page: Page, url_web: str) -> None:
    """CP-06: Rechazar la solicitud cuando el empleado no existe.

    Se verifica lo único observable desde la interfaz: no hay fila ni botón
    'vacaciones-abrir-9999' en el directorio para un empleado inexistente.
    Forzar el envío del formulario para ese id no es posible porque la
    pantalla de vacaciones no tiene una ruta propia (ver nota del módulo);
    se reporta como hueco de la aplicación en vez de simularlo.
    """
    page.goto(url_web)

    expect(page.get_by_test_id("fila-empleado-9999")).to_have_count(0)
    expect(page.get_by_test_id("vacaciones-abrir-9999")).to_have_count(0)

    pytest.skip(
        "La app no expone una ruta para abrir el formulario de vacaciones de un "
        "empleado sin pasar por su botón de fila; no se puede forzar el envío "
        "para comprobar el mensaje 'Empleado no encontrado'. Reportado como "
        "hueco de la aplicación, no se automatiza con datos simulados."
    )


def test_cp08_rechaza_empleado_dado_de_baja(page: Page, url_api: str, url_web: str) -> None:
    """CP-08: Rechazar la solicitud de un empleado dado de baja.

    Se verifica lo observable desde la interfaz: el botón
    'vacaciones-abrir-{id}' no aparece en la fila de un empleado de baja.
    Forzar el envío sin ese botón no es posible (ver nota del módulo).
    """
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-01-01")
    _dar_de_baja(url_api, empleado["id"], fecha_baja="2024-06-01")
    _ir_a_empleado(page, url_web, empleado)

    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
    expect(page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}")).to_have_count(0)

    pytest.skip(
        "La app no expone una ruta para abrir el formulario de vacaciones de un "
        "empleado dado de baja sin su botón de fila (que no existe); no se "
        "puede forzar el envío para comprobar el detail de error. Reportado "
        "como hueco de la aplicación, no se automatiza con datos simulados."
    )


def test_cp10_rechaza_fin_anterior_a_inicio(page: Page, url_api: str, url_web: str) -> None:
    """CP-10: Rechazar cuando la fecha de fin es anterior a la fecha de inicio."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")
    _ir_a_empleado(page, url_web, empleado)

    _abrir_vacaciones_y_enviar(page, empleado["id"], "2026-07-10", "2026-07-06")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp12_rechaza_periodo_que_cruza_de_anio(page: Page, url_api: str, url_web: str) -> None:
    """CP-12: Rechazar un periodo que cruza de un año a otro."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")
    _ir_a_empleado(page, url_web, empleado)

    _abrir_vacaciones_y_enviar(page, empleado["id"], "2026-12-28", "2027-01-08")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp14_rechaza_anio_sin_tabla_de_festivos(page: Page, url_api: str, url_web: str) -> None:
    """CP-14: Rechazar un año que no está en la tabla de festivos."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2023-01-01")
    _ir_a_empleado(page, url_web, empleado)

    _abrir_vacaciones_y_enviar(page, empleado["id"], "2025-07-06", "2025-07-10")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp16_rechaza_sin_un_anio_de_antiguedad(page: Page, url_api: str, url_web: str) -> None:
    """CP-16: Rechazar una solicitud sin un año de antigüedad cumplido."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2025-12-21")
    _ir_a_empleado(page, url_web, empleado)

    _abrir_vacaciones_y_enviar(page, empleado["id"], "2026-12-18", "2026-12-18")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp18_rechaza_periodo_sin_dias_habiles(page: Page, url_api: str, url_web: str) -> None:
    """CP-18: Rechazar un periodo sin ningún día hábil."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")
    _ir_a_empleado(page, url_web, empleado)

    _abrir_vacaciones_y_enviar(page, empleado["id"], "2026-07-11", "2026-07-12")

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "El periodo no incluye días hábiles"
    )


def test_cp20_rechaza_solicitud_que_rebasa_dias_disponibles(
    page: Page, url_api: str, url_web: str
) -> None:
    """CP-20: Rechazar una solicitud que rebasa los días disponibles del año."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2024-03-10")
    for fecha_inicio, fecha_fin in (
        ("2026-07-06", "2026-07-10"),
        ("2026-07-13", "2026-07-17"),
        ("2026-07-20", "2026-07-21"),
    ):
        consumo = _solicitar_vacaciones_api(url_api, empleado["id"], fecha_inicio, fecha_fin)
        assert consumo.status_code == 201, consumo.text

    _ir_a_empleado(page, url_web, empleado)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("0")

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-11-02")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-11-02")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )
