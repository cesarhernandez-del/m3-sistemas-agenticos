# language: es

Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  Quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  Para darlo de alta en la empresa

  Escenario: Registro exitoso de un empleado
    Dado que no existe ningún empleado con correo "ana.lopez@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | nombre     | correo                  | puesto                | departamento | fecha_ingreso |
      | Ana López  | Ana.Lopez@Empresa.com   | Analista de Sistemas  | Tecnología   | 2024-01-15    |
    Entonces el sistema responde con código 201
    Y el empleado queda registrado con número de empleado "EMP-0001"
    Y el correo guardado del empleado es "ana.lopez@empresa.com"
    Y el estado del empleado es "activo"
    Y la pantalla muestra un mensaje de confirmación que incluye el número de empleado "EMP-0001"

  Escenario: No se puede registrar un empleado con un correo ya existente
    Dado que existe un empleado registrado con correo "carlos.ruiz@empresa.com"
    Cuando intento registrar un empleado con correo "CARLOS.RUIZ@EMPRESA.COM", nombre "Laura Díaz", puesto "Contador", departamento "Finanzas" y fecha_ingreso "2024-02-01"
    Entonces el sistema responde con código 409
    Y el mensaje es "El correo ya está registrado"

  Escenario: No se puede registrar un empleado con un correo que no es corporativo
    Dado que no existe ningún empleado con correo "laura.perez@gmail.com"
    Cuando intento registrar un empleado con correo "laura.perez@gmail.com", nombre "Laura Pérez", puesto "Vendedor", departamento "Ventas" y fecha_ingreso "2024-02-01"
    Entonces el sistema responde con código 422
    Y el mensaje es "Usa el correo corporativo @empresa.com"

  Escenario: No se puede registrar un empleado con fecha de ingreso futura
    Dado que no existe ningún empleado con correo "mario.soto@empresa.com"
    Cuando intento registrar un empleado con correo "mario.soto@empresa.com", nombre "Mario Soto", puesto "Técnico", departamento "Operaciones" y fecha_ingreso "2999-01-01"
    Entonces el sistema responde con código 422
    Y el mensaje es "La fecha de ingreso no puede ser futura"

  Esquema del escenario: No se puede registrar un empleado con datos obligatorios inválidos
    Dado que no existe ningún empleado con correo "<correo>"
    Cuando intento registrar un empleado con correo "<correo>", nombre "<nombre>", puesto "<puesto>", departamento "<departamento>" y fecha_ingreso "<fecha_ingreso>"
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "<campo_invalido>" debe corregirse

    Ejemplos:
      | correo                  | nombre       | puesto     | departamento | fecha_ingreso | campo_invalido |
      | pedro.gil@empresa.com   | A            | Analista   | Tecnología   | 2024-02-01    | nombre         |
      | sara.cruz@empresa.com   |              | Analista   | Tecnología   | 2024-02-01    | nombre         |
      | ivan.leon@empresa.com   | Iván León    | B          | Tecnología   | 2024-02-01    | puesto         |
      | eva.ponce@empresa.com   | Eva Ponce    | Diseñador  | Marketing    | 2024-02-01    | departamento   |
      | noe.ramos@empresa.com   | Noé Ramos    | Supervisor | Operaciones  |                | fecha_ingreso  |

# Preguntas abiertas
# - ¿Cuál es el texto exacto del mensaje de confirmación tras registrar? La nota del PO solo indica que debe incluir el número asignado, pero no da la redacción literal.
# - Para la regla "cualquier otro dato inválido responde 422 y la pantalla muestra qué campo corregir" (regla 3), ¿existe un mensaje exacto por campo (por ejemplo "El nombre debe tener entre 2 y 80 caracteres") o basta con señalar el nombre del campo?
# - ¿El campo "nombre" y "puesto" tienen alguna restricción de formato (caracteres especiales, números) además del largo mínimo y máximo?
