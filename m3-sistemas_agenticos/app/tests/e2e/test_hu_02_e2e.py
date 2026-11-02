"""Pruebas E2E para HU-02: directorio de empleados.

Cada caso crea sus propios empleados vía la API (con un identificador único
incrustado en el nombre) y usa ese identificador en el buscador del
directorio para aislar sus resultados del resto de los datos existentes.
"""

import uuid

import httpx
from playwright.sync_api import Page, expect


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


def _crear_empleado_dado_de_baja(
    url_api: str,
    nombre: str,
    correo: str,
    puesto: str,
    departamento: str,
) -> dict:
    """Crea un empleado vía la API y lo da de baja con POST /api/empleados/{id}/baja."""
    empleado = _crear_empleado(
        url_api, nombre=nombre, puesto=puesto, departamento=departamento, correo=correo
    )
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/baja",
        json={"fecha_baja": "2024-06-15"},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def test_cp02_ver_directorio_completo(page: Page, url_api: str, url_web: str) -> None:
    """CP-02: Ver el directorio completo de empleados."""
    etiqueta = uuid.uuid4().hex[:8]
    empleado1 = _crear_empleado(url_api, nombre=f"Ana Torres {etiqueta}", puesto="Analista", departamento="Tecnología")
    empleado2 = _crear_empleado(url_api, nombre=f"Luis Pérez {etiqueta}", puesto="Ejecutivo", departamento="Ventas")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(etiqueta)

    expect(page.get_by_test_id("tabla-empleados")).to_be_visible()
    expect(page.locator('[data-testid^="fila-empleado-"]')).to_have_count(2)

    fila1 = page.get_by_test_id(f"fila-empleado-{empleado1['id']}")
    expect(fila1).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado1['id']}")).to_have_text(empleado1["numero_empleado"])
    expect(fila1).to_contain_text(empleado1["nombre"])
    expect(fila1).to_contain_text("Analista")
    expect(fila1).to_contain_text("Tecnología")
    expect(page.get_by_test_id(f"estado-empleado-{empleado1['id']}")).to_have_text("Activo")

    fila2 = page.get_by_test_id(f"fila-empleado-{empleado2['id']}")
    expect(fila2).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado2['id']}")).to_have_text(empleado2["numero_empleado"])
    expect(fila2).to_contain_text(empleado2["nombre"])
    expect(fila2).to_contain_text("Ejecutivo")
    expect(fila2).to_contain_text("Ventas")
    expect(page.get_by_test_id(f"estado-empleado-{empleado2['id']}")).to_have_text("Activo")


def test_cp04_buscar_por_nombre_sin_distinguir_mayusculas(page: Page, url_api: str, url_web: str) -> None:
    """CP-04: Buscar por nombre sin distinguir mayúsculas de minúsculas."""
    etiqueta = uuid.uuid4().hex[:8]
    nombre = f"Ana Torres {etiqueta}"
    empleado = _crear_empleado(url_api, nombre=nombre)

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"ana torres {etiqueta}")

    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(fila).to_contain_text(nombre)


def test_cp06_buscar_por_correo_sin_distinguir_mayusculas(page: Page, url_api: str, url_web: str) -> None:
    """CP-06: Buscar por correo sin distinguir mayúsculas de minúsculas."""
    etiqueta = uuid.uuid4().hex[:10]
    correo = f"luis.perez.{etiqueta}@empresa.com"
    empleado = _crear_empleado(url_api, nombre="Luis Pérez", correo=correo)

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(correo.upper())

    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(fila).to_contain_text(correo)


def test_cp08_filtrar_por_departamento(page: Page, url_api: str, url_web: str) -> None:
    """CP-08: Filtrar empleados por departamento."""
    etiqueta = uuid.uuid4().hex[:8]
    _crear_empleado(url_api, nombre=f"Empleado Tec Uno {etiqueta}", departamento="Tecnología")
    _crear_empleado(url_api, nombre=f"Empleado Tec Dos {etiqueta}", departamento="Tecnología")
    _crear_empleado(url_api, nombre=f"Empleado Ventas {etiqueta}", departamento="Ventas")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(etiqueta)
    page.get_by_test_id("filtro-departamento").select_option("Tecnología")

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(2)
    for indice in range(2):
        expect(filas.nth(indice)).to_contain_text("Tecnología")


def test_cp10_buscar_texto_sin_coincidencias(page: Page, url_api: str, url_web: str) -> None:
    """CP-10: Buscar un texto que no coincide con ningún empleado."""
    etiqueta = uuid.uuid4().hex[:8]
    _crear_empleado(url_api, nombre=f"Ana Torres {etiqueta}")

    page.goto(url_web)
    texto_sin_coincidencia = f"sin-coincidencias-{uuid.uuid4().hex}"
    page.get_by_test_id("buscar-empleados").fill(texto_sin_coincidencia)

    sin_resultados = page.get_by_test_id("sin-resultados")
    expect(sin_resultados).to_be_visible()
    expect(sin_resultados).to_have_text("No se encontraron resultados")
    expect(page.get_by_test_id("tabla-empleados")).to_have_count(0)


def test_cp12_empleado_baja_sigue_en_directorio(page: Page, url_api: str, url_web: str) -> None:
    """CP-12: Un empleado dado de baja sigue apareciendo en el directorio."""
    etiqueta = uuid.uuid4().hex[:8]
    nombre = f"Sofía Díaz {etiqueta}"
    correo = f"sofia.diaz.{etiqueta}@empresa.com"
    empleado = _crear_empleado_dado_de_baja(url_api, nombre, correo, puesto="Analista", departamento="Tecnología")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(etiqueta)

    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(fila).to_contain_text(nombre)
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
