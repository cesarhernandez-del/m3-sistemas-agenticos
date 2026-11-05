import { useState } from 'react'

const DEPARTAMENTOS = [
  'Tecnología',
  'Ventas',
  'Finanzas',
  'Recursos Humanos',
  'Operaciones',
]

const VALORES_INICIALES = {
  nombre: '',
  correo: '',
  puesto: '',
  departamento: '',
  fecha_ingreso: '',
}

function FormularioEmpleado() {
  const [datos, setDatos] = useState(VALORES_INICIALES)
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  function actualizarCampo(campo, valor) {
    setDatos((anterior) => ({ ...anterior, [campo]: valor }))
  }

  async function guardarEmpleado(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')

    const camposVacios = Object.values(datos).some((valor) => valor.trim() === '')
    if (camposVacios) {
      setMensajeError('Completa todos los campos')
      return
    }

    try {
      const respuesta = await fetch('/api/empleados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(cuerpo.detail)
        return
      }

      setMensajeExito(`Empleado ${cuerpo.numero_empleado} registrado con éxito`)
      setDatos(VALORES_INICIALES)
    } catch {
      setMensajeError('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={guardarEmpleado}>
      <h1>Registrar empleado</h1>

      <label htmlFor="nombre">Nombre</label>
      <input
        id="nombre"
        data-testid="empleado-nombre"
        value={datos.nombre}
        onChange={(evento) => actualizarCampo('nombre', evento.target.value)}
      />

      <label htmlFor="correo">Correo</label>
      <input
        id="correo"
        data-testid="empleado-correo"
        value={datos.correo}
        onChange={(evento) => actualizarCampo('correo', evento.target.value)}
      />

      <label htmlFor="puesto">Puesto</label>
      <input
        id="puesto"
        data-testid="empleado-puesto"
        value={datos.puesto}
        onChange={(evento) => actualizarCampo('puesto', evento.target.value)}
      />

      <label htmlFor="departamento">Departamento</label>
      <select
        id="departamento"
        data-testid="empleado-departamento"
        value={datos.departamento}
        onChange={(evento) => actualizarCampo('departamento', evento.target.value)}
      >
        <option value="">Selecciona un departamento</option>
        {DEPARTAMENTOS.map((departamento) => (
          <option key={departamento} value={departamento}>
            {departamento}
          </option>
        ))}
      </select>

      <label htmlFor="fecha_ingreso">Fecha de ingreso</label>
      <input
        id="fecha_ingreso"
        type="date"
        data-testid="empleado-fecha-ingreso"
        value={datos.fecha_ingreso}
        onChange={(evento) => actualizarCampo('fecha_ingreso', evento.target.value)}
      />

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default FormularioEmpleado
