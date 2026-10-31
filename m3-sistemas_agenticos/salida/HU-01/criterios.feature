# language: es
Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  para darlo de alta en la empresa

  Escenario: Registro exitoso de un empleado con datos válidos
    Dado que no existe ningún empleado con el correo "ana.perez@empresa.com"
    Cuando registro un empleado con nombre "Ana Pérez", correo "Ana.Perez@empresa.com", puesto "Analista de Nómina", departamento "Recursos Humanos" y fecha de ingreso "2024-03-01"
    Entonces el sistema responde con estado 201
    Y el empleado queda registrado con numero_empleado "EMP-0001"
    Y el correo guardado es "ana.perez@empresa.com"
    Y el estado del empleado es "activo"
    Y la pantalla muestra el mensaje "Empleado EMP-0001 registrado con éxito"

  Escenario: Rechazar registro con correo ya existente (sin importar mayúsculas)
    Dado que ya existe un empleado registrado con el correo "ana.perez@empresa.com"
    Cuando registro un empleado con nombre "Ana P. Gómez", correo "ANA.PEREZ@empresa.com", puesto "Reclutadora", departamento "Recursos Humanos" y fecha de ingreso "2024-03-01"
    Entonces el sistema responde con estado 409
    Y la pantalla muestra el mensaje "El correo ya está registrado"
    Y no se crea un nuevo empleado

  Escenario: Rechazar registro con correo que no es corporativo
    Dado que no existe ningún empleado con el correo "carlos.ruiz@gmail.com"
    Cuando registro un empleado con nombre "Carlos Ruiz", correo "carlos.ruiz@gmail.com", puesto "Desarrollador", departamento "Tecnología" y fecha de ingreso "2024-03-01"
    Entonces el sistema responde con estado 422
    Y la pantalla muestra el mensaje "Usa el correo corporativo @empresa.com"
    Y no se crea un nuevo empleado

  Escenario: Rechazar registro con fecha de ingreso futura
    Dado que la fecha actual del sistema es "2024-05-10"
    Cuando registro un empleado con nombre "Laura Díaz", correo "laura.diaz@empresa.com", puesto "Contadora", departamento "Finanzas" y fecha de ingreso "2024-06-01"
    Entonces el sistema responde con estado 422
    Y la pantalla muestra el mensaje "La fecha de ingreso no puede ser futura"
    Y no se crea un nuevo empleado

  Escenario: Rechazar registro con nombre fuera del rango permitido
    Dado que no existe ningún empleado con el correo "jo@empresa.com"
    Cuando registro un empleado con nombre "J", correo "jo@empresa.com", puesto "Auxiliar", departamento "Operaciones" y fecha de ingreso "2024-03-01"
    Entonces el sistema responde con estado 422
    Y la pantalla indica que el campo "nombre" debe corregirse
    Y no se crea un nuevo empleado

  Escenario: Rechazar registro con departamento no permitido
    Dado que no existe ningún empleado con el correo "mario.leon@empresa.com"
    Cuando registro un empleado con nombre "Mario León", correo "mario.leon@empresa.com", puesto "Supervisor", departamento "Logística" y fecha de ingreso "2024-03-01"
    Entonces el sistema responde con estado 422
    Y la pantalla indica que el campo "departamento" debe corregirse
    Y no se crea un nuevo empleado

# Preguntas abiertas
# - No se especifica el mensaje exacto que debe mostrar la pantalla para errores genéricos de campo (regla 3);
#   se usó una redacción genérica "indica que el campo X debe corregirse". Confirmar el texto exacto esperado.
# - No se especifica si el límite de caracteres de "nombre" y "puesto" es inclusivo en los extremos (2 y 80 / 2 y 60);
#   se asumió que esos valores sí son válidos y solo valores por debajo del mínimo son inválidos.
