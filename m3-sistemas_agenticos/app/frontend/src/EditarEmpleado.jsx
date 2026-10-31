import { useState } from 'react'

function EditarEmpleado({ empleado, departamentos, onCancelar, onGuardado }) {
  const [puesto, setPuesto] = useState(empleado.puesto)
  const [departamento, setDepartamento] = useState(empleado.departamento)
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  async function guardar(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ puesto, departamento }),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(cuerpo.detail)
        return
      }

      setMensajeExito(`Empleado ${cuerpo.numero_empleado} actualizado con éxito`)
      onGuardado(cuerpo)
    } catch {
      setMensajeError('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={guardar}>
      <h2>Editar empleado {empleado.numero_empleado}</h2>

      <label htmlFor="puesto">Puesto</label>
      <input
        id="puesto"
        data-testid="empleado-puesto"
        value={puesto}
        onChange={(evento) => setPuesto(evento.target.value)}
      />

      <label htmlFor="departamento">Departamento</label>
      <select
        id="departamento"
        data-testid="empleado-departamento"
        value={departamento}
        onChange={(evento) => setDepartamento(evento.target.value)}
      >
        {departamentos.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default EditarEmpleado
