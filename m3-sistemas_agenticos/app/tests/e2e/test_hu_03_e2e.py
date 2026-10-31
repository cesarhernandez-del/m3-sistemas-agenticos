"""Pruebas E2E para HU-03: editar empleado y darlo de baja.

Cada caso crea su propio empleado vía la API con un correo único (uuid)
y usa el id numérico devuelto para ubicar la fila y los controles en la
interfaz (fila-empleado-{id}, editar-empleado-{id}, etc.), según las
convenciones de data-testid de la aplicación.
"""

import uuid

import httpx
from playwright.sync_api import Page, expect


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


def _dar_de_baja(url_api: str, id_empleado: int, fecha_baja: str = "2024-01-01") -> dict:
    """Da de baja a un empleado vía la API y regresa el objeto actualizado."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{id_empleado}/baja", json={"fecha_baja": fecha_baja}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _ir_a_empleado(page: Page, url_web: str, empleado: dict) -> None:
    """Navega al directorio y filtra por el correo del empleado para aislarlo."""
    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(empleado["correo"])
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def test_cp02_editar_puesto_y_departamento_empleado_activo(
    page: Page, url_api: str, url_web: str
) -> None:
    """CP-02: Editar puesto y departamento de un empleado activo."""
    empleado = _crear_empleado(url_api, puesto="Analista", departamento="Ventas")
    _ir_a_empleado(page, url_web, empleado)

    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-departamento").select_option("Tecnología")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_contain_text("Analista Senior")
    expect(fila).to_contain_text("Tecnología")
    expect(page.get_by_test_id(f"numero-empleado-{empleado['id']}")).to_have_text(
        empleado["numero_empleado"]
    )


def test_cp04_error_editar_departamento_fuera_de_catalogo(
    page: Page, url_api: str, url_web: str
) -> None:
    """CP-04: Error al editar con un departamento fuera del catálogo.

    El <select> de departamento solo ofrece valores del catálogo, así que no
    hay forma de elegir "Marketing" desde la interfaz. Se inyecta la opción
    por DOM para simular un cliente desactualizado y así ejercitar la
    respuesta de error del backend cuando llega un departamento inválido.
    """
    empleado = _crear_empleado(url_api, puesto="Analista", departamento="Ventas")
    _ir_a_empleado(page, url_web, empleado)

    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    page.evaluate(
        """() => {
            const select = document.querySelector('[data-testid="empleado-departamento"]');
            const opcion = document.createElement('option');
            opcion.value = 'Marketing';
            opcion.textContent = 'Marketing';
            select.appendChild(opcion);
        }"""
    )
    page.get_by_test_id("empleado-departamento").select_option("Marketing")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_be_visible()


def test_cp06_error_editar_puesto_demasiado_corto(
    page: Page, url_api: str, url_web: str
) -> None:
    """CP-06: Error al editar con un puesto demasiado corto."""
    empleado = _crear_empleado(url_api, puesto="Analista", departamento="Ventas")
    _ir_a_empleado(page, url_web, empleado)

    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-puesto").fill("A")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_be_visible()


def test_cp08_error_editar_empleado_dado_de_baja(
    page: Page, url_api: str, url_web: str
) -> None:
    """CP-08: Error al intentar editar a un empleado dado de baja."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2020-01-01")
    _dar_de_baja(url_api, empleado["id"], fecha_baja="2024-01-01")
    _ir_a_empleado(page, url_web, empleado)

    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")

    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-puesto").fill("Coordinador")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_have_text(
        "No se puede editar a un empleado dado de baja"
    )


def test_cp10_dar_de_baja_empleado_activo(page: Page, url_api: str, url_web: str) -> None:
    """CP-10: Dar de baja a un empleado activo."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2022-03-01")
    _ir_a_empleado(page, url_web, empleado)

    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2024-06-15")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def test_cp12_error_dar_de_baja_fecha_anterior_a_ingreso(
    page: Page, url_api: str, url_web: str
) -> None:
    """CP-12: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    empleado = _crear_empleado(url_api, fecha_ingreso="2022-03-01")
    _ir_a_empleado(page, url_web, empleado)

    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2022-01-01")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-error")).to_be_visible()
