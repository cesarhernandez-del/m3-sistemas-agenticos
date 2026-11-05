# language: es

Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  para encontrar rápido a una persona

  Escenario: Ver el directorio completo de empleados
    Dado que existen los empleados:
      | numero_empleado | nombre        | puesto           | departamento      | estado |
      | EMP-0001        | Ana Torres    | Analista         | Tecnología        | activo |
      | EMP-0002        | Luis Pérez    | Ejecutivo        | Ventas            | activo |
    Cuando abro el directorio de empleados
    Entonces veo 2 empleados en la lista
    Y cada fila muestra número de empleado, nombre, puesto, departamento y estado

  Escenario: Buscar por nombre sin distinguir mayúsculas de minúsculas
    Dado que existe el empleado "EMP-0001" con nombre "Ana Torres"
    Cuando busco en el directorio el texto "ana torres"
    Entonces veo en los resultados al empleado "EMP-0001" con nombre "Ana Torres"

  Escenario: Buscar por correo sin distinguir mayúsculas de minúsculas
    Dado que existe el empleado "EMP-0002" con correo "luis.perez@empresa.com"
    Cuando busco en el directorio el texto "LUIS.PEREZ@EMPRESA.COM"
    Entonces veo en los resultados al empleado "EMP-0002" con correo "luis.perez@empresa.com"

  Escenario: Filtrar empleados por departamento
    Dado que existen los empleados:
      | numero_empleado | nombre        | departamento      |
      | EMP-0001        | Ana Torres    | Tecnología        |
      | EMP-0002        | Luis Pérez    | Ventas            |
      | EMP-0003        | Marta Ruiz    | Tecnología        |
    Cuando filtro el directorio por el departamento "Tecnología"
    Entonces veo 2 empleados en la lista
    Y todos los empleados mostrados tienen departamento "Tecnología"

  Escenario: Buscar un texto que no coincide con ningún empleado
    Dado que existe el empleado "EMP-0001" con nombre "Ana Torres"
    Cuando busco en el directorio el texto "Carlos Gómez"
    Entonces veo el mensaje "No se encontraron resultados"
    Y la lista de resultados está vacía

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que existe el empleado "EMP-0004" con nombre "Sofía Díaz" y estado "baja"
    Cuando abro el directorio de empleados
    Entonces veo en los resultados al empleado "EMP-0004" con nombre "Sofía Díaz"
    Y el estado mostrado para "EMP-0004" es "baja"

# Preguntas abiertas
# - No se especifica si el filtro por departamento se puede combinar con la búsqueda por nombre/correo al mismo tiempo.
# - No se especifica si existe paginación o límite de resultados cuando el directorio tiene muchos empleados.
# - No se especifica qué ocurre si se envía un valor de departamento que no está en la lista permitida (Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones).
