import { useState } from 'react'
import FormularioEmpleado from './FormularioEmpleado'
import DirectorioEmpleados from './DirectorioEmpleados'

function App() {
  const [hayFormularioAbierto, setHayFormularioAbierto] = useState(false)

  return (
    <>
      {!hayFormularioAbierto && <FormularioEmpleado />}
      <DirectorioEmpleados onFormularioAbierto={setHayFormularioAbierto} />
    </>
  )
}

export default App
