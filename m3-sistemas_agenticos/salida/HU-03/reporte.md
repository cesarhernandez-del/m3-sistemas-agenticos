# Reporte · HU-03

**Estado:** ESCALAR A UNA PERSONA
**Costo de agentes:** 3.54 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: No migres los data-testid ni las rutas a numero_empleado. Según convenciones_app.md, {id} es el campo id numérico del recurso, el mismo que ya usan HU-02 y sus pruebas. Las rutas nuevas son GET /api/empleados/{id}, PUT /api/empleados/{id} y POST /api/empleados/{id}/baja, y los testid nuevos son editar-empleado-{id} y baja-empleado-{id} con el id numérico. No modifiques el alta ni el directorio de HU-01 y HU-02.
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (12 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 7 failed, 17 passed, 3 warnings in 12.98s
- Triage → desarrollador: Al dar de baja a un empleado, este desaparece del directorio en lugar de seguir apareciendo con estado "baja", incumpliendo el escenario "Dar de baja a un empleado activo" que exige que el empleado "sigue apareciendo en el directorio". Esto afecta tanto a la prueba de API (test_cp11) como a las E2E (test_cp06 con el correo generado y test_cp12).
- Código corregido; redespliegue OK
- Pruebas E2E: 10 failed, 14 passed, 3 warnings in 52.91s
- Triage → automatizador: Las 10 pruebas fallan porque las filas de empleados esperadas (fila-empleado-88, 89, 94-100) nunca aparecen en el directorio; la aplicación sigue mostrando la pantalla de "Registrar empleado" sin haber navegado ni confirmado la creación/precondición de los empleados de prueba antes de buscarlos. Esto indica que los tests no esperan correctamente a que el empleado se registre (o no navegan a la vista de listado) antes de aserciones sobre las filas, usando selectores que apuntan a un estado de la UI que aún no se alcanzó.
- Pruebas corregidas
- Pruebas E2E: 10 failed, 14 passed, 3 warnings in 52.56s

## Última ejecución de pruebas
```
10 failed, 14 passed, 3 warnings in 52.56s
- tests.e2e.test_hu_02_e2e::test_cp04_buscar_por_nombre_sin_distinguir_mayusculas[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-120") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-120")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_02_e2e::test_cp06_buscar_por_correo_sin_distinguir_mayusculas[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-121") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-121")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_02_e2e::test_cp08_filtrar_por_departamento[chromium]
  AssertionError: Locator expected to have count '2'
Actual value: 0 
Call log:
  - Expect "to_have_count" locator("[data-testid^=\"fila-empleado-\"]") with timeout 5000ms
  - waiting for locator("[data-testid^=\"fila-empleado-\"]")
    14 × locator resolved to 0 elements
       - unexpected value "0"
- tests.e2e.test_hu_02_e2e::test_cp12_empleado_baja_sigue_en_directorio[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-126") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-126")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_03_e2e::test_cp02_editar_puesto_y_departamento_empleado_activo[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-127") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-127")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_03_e2e::test_cp04_error_editar_departamento_fuera_de_catalogo[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-128") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-128")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_03_e2e::test_cp06_error_editar_puesto_demasiado_corto[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-129") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-129")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_03_e2e::test_cp08_error_editar_empleado_dado_de_baja[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-130") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-130")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_03_e2e::test_cp10_dar_de_baja_empleado_activo[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-131") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-131")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
- tests.e2e.test_hu_03_e2e::test_cp12_error_dar_de_baja_fecha_anterior_a_ingreso[chromium]
  AssertionError: Locator expected to be visible
Actual value: None
Error: element(s) not found 
Call log:
  - Expect "to_be_visible" get_by_test_id("fila-empleado-132") with timeout 5000ms
  - waiting for get_by_test_id("fila-empleado-132")

Aria snapshot:
- heading "Registrar empleado" [level=1]
- text: Nombre
- textbox "Nombre"
- text: Correo
- textbox "Correo"
- text: Puesto
- textbox "Puesto"
-
```