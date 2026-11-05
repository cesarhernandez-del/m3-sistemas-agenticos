import { useEffect, useState } from 'react'

function VacacionesEmpleado({ empleado, onCancelar }) {
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [diasDisponibles, setDiasDisponibles] = useState(null)
  const [mensaje, setMensaje] = useState('')

  function cargarSaldo() {
    fetch(`/api/empleados/${empleado.id}/vacaciones`)
      .then((respuesta) => respuesta.json())
      .then((cuerpo) => setDiasDisponibles(cuerpo.dias_disponibles))
      .catch(() => setDiasDisponibles(null))
  }

  useEffect(cargarSaldo, [empleado.id])

  async function enviar(evento) {
    evento.preventDefault()
    setMensaje('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.id}/vacaciones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha_inicio: fechaInicio, fecha_fin: fechaFin }),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        setMensaje(cuerpo.detail)
        return
      }

      const anio = cuerpo.fecha_inicio.slice(0, 4)
      setMensaje(
        `Solicitud registrada: ${cuerpo.dias_habiles} días hábiles. Te quedan ${cuerpo.dias_restantes} días hábiles en ${anio}.`
      )
      cargarSaldo()
    } catch {
      setMensaje('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={enviar}>
      <h2>Solicitar vacaciones de {empleado.numero_empleado}</h2>

      <p>
        Días disponibles en el año:{' '}
        <span data-testid="vacaciones-disponibles">
          {diasDisponibles ?? '...'}
        </span>
      </p>

      <label htmlFor="vacaciones_fecha_inicio">Fecha de inicio</label>
      <input
        id="vacaciones_fecha_inicio"
        type="date"
        data-testid="vacaciones-fecha-inicio"
        value={fechaInicio}
        onChange={(evento) => setFechaInicio(evento.target.value)}
      />

      <label htmlFor="vacaciones_fecha_fin">Fecha de fin</label>
      <input
        id="vacaciones_fecha_fin"
        type="date"
        data-testid="vacaciones-fecha-fin"
        value={fechaFin}
        onChange={(evento) => setFechaFin(evento.target.value)}
      />

      <button type="submit" data-testid="vacaciones-enviar">
        Enviar solicitud
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}
    </form>
  )
}

export default VacacionesEmpleado
