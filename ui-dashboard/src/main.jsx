import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'
import { config } from './config'
import Dashboard from './Dashboard'
import OrderSetup from './OrderSetup'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentPage, setCurrentPage] = useState('dashboard')

  const handleLogin = (e) => {
    e.preventDefault()
    
    if (username === config.auth.username && password === config.auth.password) {
      console.log('Login successful')
      setError('')
      setIsLoggedIn(true)
    } else {
      setError('Invalid username or password')
    }
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setUsername('')
    setPassword('')
    setError('')
    setCurrentPage('dashboard')
  }

  if (isLoggedIn) {
    if (currentPage === 'order-setup') {
      return <OrderSetup onBack={() => setCurrentPage('dashboard')} />
    }
    return <Dashboard onLogout={handleLogout} onNavigateToOrderSetup={() => setCurrentPage('order-setup')} />
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      fontFamily: 'system-ui, Arial'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <h1 style={{ marginBottom: '30px', textAlign: 'center' }}>Trading Dashboard</h1>
        {error && (
          <div style={{
            padding: '10px',
            marginBottom: '20px',
            backgroundColor: '#fee',
            color: '#c33',
            borderRadius: '4px',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
              }}
              required
            />
          </div>
          <div style={{ marginBottom: '30px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px'
              }}
              required
            />
          </div>
          <button 
            type="submit"
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Login
          </button>
        </form>
      </div>
      <footer style={{
        marginTop: '40px',
        textAlign: 'center',
        color: '#666',
        fontSize: '14px'
      }}>
        © {new Date().getFullYear()} Trading Dashboard. All rights reserved.
      </footer>
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
