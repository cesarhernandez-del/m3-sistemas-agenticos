import { useState } from 'react'

function BajaEmpleado({ empleado, onCancelar, onConfirmado }) {
  const [fechaBaja, setFechaBaja] = useState('')
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  async function confirmar(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.id}/baja`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha_baja: fechaBaja }),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(cuerpo.detail)
        return
      }

      setMensajeExito(`Empleado ${cuerpo.numero_empleado} dado de baja con éxito`)
      onConfirmado(cuerpo)
    } catch {
      setMensajeError('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={confirmar}>
      <h2>Dar de baja a {empleado.numero_empleado}</h2>

      <label htmlFor="fecha_baja">Fecha de baja</label>
      <input
        id="fecha_baja"
        type="date"
        data-testid="empleado-fecha-baja"
        value={fechaBaja}
        onChange={(evento) => setFechaBaja(evento.target.value)}
      />

      <button type="submit" data-testid="confirmar-baja">
        Confirmar baja
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default BajaEmpleado
