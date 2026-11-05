# language: es
Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial

  Escenario: Editar puesto y departamento de un empleado activo
    Dado que existe el empleado "EMP-0007" con correo "ana.gomez@empresa.com", puesto "Analista", departamento "Ventas" y estado "activo"
    Cuando edito el empleado "EMP-0007" con puesto "Analista Senior" y departamento "Tecnología"
    Entonces la respuesta tiene código 200
    Y el empleado "EMP-0007" muestra puesto "Analista Senior"
    Y el empleado "EMP-0007" muestra departamento "Tecnología"
    Y el número de empleado sigue siendo "EMP-0007"
    Y el correo sigue siendo "ana.gomez@empresa.com"

  Escenario: Error al editar con un departamento fuera del catálogo
    Dado que existe el empleado "EMP-0007" con puesto "Analista", departamento "Ventas" y estado "activo"
    Cuando edito el empleado "EMP-0007" con departamento "Marketing"
    Entonces la respuesta tiene código 422
    Y la pantalla indica que el campo "departamento" debe corregirse

  Escenario: Error al editar con un puesto demasiado corto
    Dado que existe el empleado "EMP-0007" con puesto "Analista", departamento "Ventas" y estado "activo"
    Cuando edito el empleado "EMP-0007" con puesto "A"
    Entonces la respuesta tiene código 422
    Y la pantalla indica que el campo "puesto" debe corregirse

  Escenario: Error al intentar editar a un empleado dado de baja
    Dado que existe el empleado "EMP-0010" con estado "baja"
    Cuando edito el empleado "EMP-0010" con puesto "Coordinador"
    Entonces la respuesta tiene código 409
    Y el mensaje de error es "No se puede editar a un empleado dado de baja"

  Escenario: Dar de baja a un empleado activo
    Dado que existe el empleado "EMP-0007" con fecha_ingreso "2022-03-01" y estado "activo"
    Cuando doy de baja al empleado "EMP-0007" con fecha_baja "2024-06-15"
    Entonces la respuesta tiene código 200
    Y el empleado "EMP-0007" muestra estado "baja"
    Y el empleado "EMP-0007" muestra fecha_baja "2024-06-15"
    Y el empleado "EMP-0007" sigue apareciendo en el directorio

  Escenario: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso
    Dado que existe el empleado "EMP-0007" con fecha_ingreso "2022-03-01" y estado "activo"
    Cuando doy de baja al empleado "EMP-0007" con fecha_baja "2022-01-01"
    Entonces la respuesta tiene código 422
    Y la pantalla indica que el campo "fecha_baja" debe corregirse

# Preguntas abiertas
# - ¿Qué debe pasar si una solicitud de edición incluye un nuevo valor para "correo" o "numero_empleado"?
#   ¿Se ignora el cambio silenciosamente o la API responde con un error (y con qué código y mensaje)?
# - Para los datos inválidos cubiertos por la regla general "Cualquier otro dato inválido responde 422"
#   (departamento fuera de catálogo, puesto corto, fecha_baja anterior a fecha_ingreso), no hay un
#   mensaje exacto definido en las reglas de negocio; se usó una redacción genérica ("la pantalla
#   indica que el campo X debe corregirse"). Confirmar el texto exacto esperado en cada caso.
