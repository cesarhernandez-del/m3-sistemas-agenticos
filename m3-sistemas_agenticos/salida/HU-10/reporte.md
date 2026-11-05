# Reporte · HU-10

**Estado:** LISTA
**Costo de agentes:** 1.72 USD
**Ciclos de corrección:** 0

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: Ajustes: los errores de reglas responden 400 y el empleado dado de baja 409; solo el formato de fecha inválido es el 422 automático de FastAPI. Los días hábiles se cuentan incluyendo la fecha de inicio y la de fin. El mensaje del tope dice siempre “días hábiles”, también cuando N es 1. El mensaje de éxito en vacaciones-mensaje es exactamente “Solicitud registrada: N días hábiles. Te quedan M días hábiles en AAAA.”. Si GET no recibe anio, usa el año en curso. Abrir vacaciones solo puede cerrar los formularios de editar y dar de baja; el formulario de alta y el directorio siguen visibles. No modifiques el comportamiento de HU-01 a HU-03.
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (20 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 42 passed, 2 skipped, 1 warning in 5.13s

## Última ejecución de pruebas
```
42 passed, 2 skipped, 1 warning in 5.13s

```