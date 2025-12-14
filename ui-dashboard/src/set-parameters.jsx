import React from 'react'
import { createRoot } from 'react-dom/client'
import SetParameters from './SetParameters.jsx'

const ROOT_ID = 'root'
let rootEl = document.getElementById(ROOT_ID)
if (!rootEl) {
  rootEl = document.createElement('div')
  rootEl.id = ROOT_ID
  document.body.insertBefore(rootEl, document.body.firstChild)
}

createRoot(rootEl).render(<SetParameters />)

export default SetParameters
