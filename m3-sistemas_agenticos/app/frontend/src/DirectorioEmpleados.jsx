import { useEffect, useState } from 'react'
import EditarEmpleado from './EditarEmpleado'
import BajaEmpleado from './BajaEmpleado'

function DirectorioEmpleados({ onFormularioAbierto }) {
  const [empleados, setEmpleados] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [busqueda, setBusqueda] = useState('')
  const [departamentoFiltro, setDepartamentoFiltro] = useState('')
  const [empleadoEditando, setEmpleadoEditando] = useState(null)
  const [empleadoDandoBaja, setEmpleadoDandoBaja] = useState(null)

  function cargarEmpleados() {
    const parametros = new URLSearchParams()
    if (busqueda) parametros.set('buscar', busqueda)
    if (departamentoFiltro) parametros.set('departamento', departamentoFiltro)

    fetch(`/api/empleados?${parametros.toString()}`)
      .then((respuesta) => respuesta.json())
      .then(setEmpleados)
      .catch(() => setEmpleados([]))
  }

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  useEffect(cargarEmpleados, [busqueda, departamentoFiltro])

  function cerrarFormularios() {
    setEmpleadoEditando(null)
    setEmpleadoDandoBaja(null)
    onFormularioAbierto?.(false)
  }

  return (
    <section>
      <h1>Directorio de empleados</h1>

      <input
        data-testid="buscar-empleados"
        placeholder="Buscar por nombre o correo"
        value={busqueda}
        onChange={(evento) => setBusqueda(evento.target.value)}
      />

      <select
        data-testid="filtro-departamento"
        value={departamentoFiltro}
        onChange={(evento) => setDepartamentoFiltro(evento.target.value)}
      >
        <option value="">Todos</option>
        {departamentos.map((departamento) => (
          <option key={departamento} value={departamento}>
            {departamento}
          </option>
        ))}
      </select>

      {empleados.length === 0 ? (
        <p data-testid="sin-resultados">No se encontraron resultados</p>
      ) : (
        <table data-testid="tabla-empleados">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Puesto</th>
              <th>Departamento</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map((empleado) => (
              <tr key={empleado.id} data-testid={`fila-empleado-${empleado.id}`}>
                <td data-testid={`numero-empleado-${empleado.id}`}>
                  {empleado.numero_empleado}
                </td>
                <td>{empleado.nombre}</td>
                <td>{empleado.correo}</td>
                <td>{empleado.puesto}</td>
                <td>{empleado.departamento}</td>
                <td data-testid={`estado-empleado-${empleado.id}`}>
                  {empleado.estado === 'baja' ? 'Baja' : 'Activo'}
                </td>
                <td>
                  <button
                    data-testid={`editar-empleado-${empleado.id}`}
                    onClick={() => {
                      setEmpleadoDandoBaja(null)
                      setEmpleadoEditando(empleado)
                      onFormularioAbierto?.(true)
                    }}
                  >
                    Editar
                  </button>
                  <button
                    data-testid={`baja-empleado-${empleado.id}`}
                    onClick={() => {
                      setEmpleadoEditando(null)
                      setEmpleadoDandoBaja(empleado)
                      onFormularioAbierto?.(true)
                    }}
                  >
                    Dar de baja
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {empleadoEditando && (
        <EditarEmpleado
          empleado={empleadoEditando}
          departamentos={departamentos}
          onCancelar={cerrarFormularios}
          onGuardado={cargarEmpleados}
        />
      )}

      {empleadoDandoBaja && (
        <BajaEmpleado
          empleado={empleadoDandoBaja}
          onCancelar={cerrarFormularios}
          onConfirmado={cargarEmpleados}
        />
      )}
    </section>
  )
}

export default DirectorioEmpleados
