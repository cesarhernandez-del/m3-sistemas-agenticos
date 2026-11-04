# language: es

Característica: Solicitar vacaciones
  Como empleado de la empresa
  Quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  Para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Registrar una solicitud de vacaciones válida
    Dado un empleado activo con id 1, fecha_ingreso "2024-03-10" y 0 días hábiles usados en el año 2026
    Cuando solicita vacaciones con "POST /api/empleados/1/vacaciones", fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 5
    Y el campo "dias_restantes" de la respuesta es 7
    Y la pantalla muestra en "vacaciones-mensaje" el texto "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."

  Escenario: Los sábados, domingos y festivos dentro del periodo no se descuentan
    Dado un empleado activo con id 2, fecha_ingreso "2025-12-21" y 0 días hábiles usados en el año 2026
    Cuando solicita vacaciones con "POST /api/empleados/2/vacaciones", fecha_inicio "2026-12-21" y fecha_fin "2026-12-31"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 8
    Y el campo "dias_restantes" de la respuesta es 4
    Y la pantalla muestra en "vacaciones-mensaje" el texto "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."

  Escenario: Rechazar la solicitud cuando el empleado no existe
    Dado que no existe un empleado con id 9999
    Cuando solicita vacaciones con "POST /api/empleados/9999/vacaciones", fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 404
    Y el campo "detail" de la respuesta es "Empleado no encontrado"

  Escenario: Rechazar la solicitud de un empleado dado de baja
    Dado un empleado con id 3 en estado "baja"
    Cuando solicita vacaciones con "POST /api/empleados/3/vacaciones", fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 409
    Y el campo "detail" de la respuesta es "No se pueden solicitar vacaciones para un empleado dado de baja"

  Escenario: Rechazar cuando la fecha de fin es anterior a la fecha de inicio
    Dado un empleado activo con id 1, fecha_ingreso "2024-03-10"
    Cuando solicita vacaciones con "POST /api/empleados/1/vacaciones", fecha_inicio "2026-07-10" y fecha_fin "2026-07-06"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Rechazar un periodo que cruza de un año a otro
    Dado un empleado activo con id 1, fecha_ingreso "2024-03-10"
    Cuando solicita vacaciones con "POST /api/empleados/1/vacaciones", fecha_inicio "2026-12-28" y fecha_fin "2027-01-08"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Rechazar un año que no está en la tabla de festivos
    Dado un empleado activo con id 4, fecha_ingreso "2023-01-01"
    Cuando solicita vacaciones con "POST /api/empleados/4/vacaciones", fecha_inicio "2025-07-06" y fecha_fin "2025-07-10"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Rechazar una solicitud sin un año de antigüedad cumplido
    Dado un empleado activo con id 5, fecha_ingreso "2025-12-21"
    Cuando solicita vacaciones con "POST /api/empleados/5/vacaciones", fecha_inicio "2026-12-18" y fecha_fin "2026-12-18"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Rechazar un periodo sin ningún día hábil
    Dado un empleado activo con id 1, fecha_ingreso "2024-03-10"
    Cuando solicita vacaciones con "POST /api/empleados/1/vacaciones", fecha_inicio "2026-07-11" y fecha_fin "2026-07-12"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "El periodo no incluye días hábiles"

  Escenario: Rechazar una solicitud que rebasa los días disponibles del año
    Dado un empleado activo con id 6, fecha_ingreso "2024-03-10" y 12 días hábiles usados en el año 2026
    Cuando solicita vacaciones con "POST /api/empleados/6/vacaciones", fecha_inicio "2026-11-02" y fecha_fin "2026-11-02"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "La solicitud excede los días disponibles: quedan 0 días hábiles"

# Preguntas abiertas
# Ninguna: las reglas de negocio, los mensajes exactos y la API quedaron completos
# en contexto/reglas_vacaciones.md y contexto/convenciones_vacaciones.md.
