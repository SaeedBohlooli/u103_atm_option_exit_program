import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ padding: 20, fontFamily: 'system-ui, Arial' }}>
      <h1>Hello, ATM Exit UI</h1>
      <p>Count: {count}</p>
      <button aria-label="Increment count" onClick={() => setCount(c => c + 1)}>
        Add
      </button>
    </div>
  )
}

// Mount the app. If there's no <div id="root"> in the HTML, create one so
// this file can be used as a standalone quick test entry.
const ROOT_ID = 'root'
let rootEl = document.getElementById(ROOT_ID)
if (!rootEl) {
  rootEl = document.createElement('div')
  rootEl.id = ROOT_ID
  // insert at top of body so it's visible even if index.html is minimal
  document.body.insertBefore(rootEl, document.body.firstChild)
}

createRoot(rootEl).render(<App />)

export default App
