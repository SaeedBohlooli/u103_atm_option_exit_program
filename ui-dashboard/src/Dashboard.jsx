import React, { useState, useEffect } from 'react'
import { config } from './config'

function Dashboard({ onLogout, onNavigateToOrderSetup }) {
  const [flaskApiStatus, setFlaskApiStatus] = useState('Checking...')
  const [wsStatus, setWsStatus] = useState('Disconnected')

  // Flask API health check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(config.FLASK_HEALTH_URL)
        if (response.ok) {
          setFlaskApiStatus('Connected')
        } else {
          setFlaskApiStatus('Error')
        }
      } catch (error) {
        setFlaskApiStatus('Disconnected')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)

    return () => clearInterval(interval)
  }, [])

  // WebSocket status check
  useEffect(() => {
    let ws
    let reconnectTimeout

    const connect = () => {
      ws = new WebSocket(config.WEBSOCKET_URL)

      ws.onopen = () => {
        setWsStatus('Connected')
      }

      ws.onerror = () => {
        setWsStatus('Error')
      }

      ws.onclose = () => {
        setWsStatus('Reconnecting...')
        reconnectTimeout = setTimeout(() => {
          connect()
        }, 3000)
      }
    }

    connect()

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
      if (ws) {
        ws.close()
      }
    }
  }, [])

  return (
    <div style={{ fontFamily: 'system-ui, Arial', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#3b82f6',
        color: 'white',
        padding: '15px 30px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>Trading Dashboard</h1>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: flaskApiStatus === 'Connected' ? '#22c55e' : flaskApiStatus === 'Error' ? '#fbbf24' : '#ef4444'
            }}></div>
            <span style={{ fontSize: '14px' }}>
              API: <span style={{ 
                color: flaskApiStatus === 'Connected' ? '#86efac' : '#fca5a5',
                fontWeight: '500'
              }}>{flaskApiStatus}</span>
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: wsStatus === 'Connected' ? '#86efac' : wsStatus === 'Error' ? '#fbbf24' : '#ef4444'
            }}></div>
            <span style={{ fontSize: '14px' }}>
              WS: <span style={{ 
                color: wsStatus === 'Connected' ? '#86efac' : '#fca5a5',
                fontWeight: '500'
              }}>{wsStatus}</span>
            </span>
          </div>
          <button
            onClick={onLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#60a5fa',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '30px', backgroundColor: '#f5f5f5' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ margin: '0 0 20px 0' }}>Welcome to Trading Dashboard</h2>
          
          {/* Stats Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>Total Portfolio Value</h3>
              <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#3b82f6' }}>$0.00</p>
            </div>
            
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>Active Positions</h3>
              <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#3b82f6' }}>0</p>
            </div>
            
            <div style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>Today's P&L</h3>
              <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#059669' }}>$0.00</p>
            </div>
          </div>

          {/* Order Setup Section */}
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '30px'
          }}>
            <h3 style={{ margin: '0 0 15px 0', fontSize: '22px' }}>Order Setup</h3>
            <p style={{ color: '#666', margin: '0 0 25px 0', fontSize: '15px' }}>Configure and manage your trading orders with advanced options.</p>
            <button
              onClick={onNavigateToOrderSetup}
              style={{
                padding: '15px 40px',
                backgroundColor: 'transparent',
                color: '#3b82f6',
                border: '2px solid #3b82f6',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                minWidth: '200px'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#3b82f6'
                e.target.style.color = 'white'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'transparent'
                e.target.style.color = '#3b82f6'
              }}
            >
              Go to Order Setup →
            </button>
          </div>

          {/* Recent Activity */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ marginTop: 0 }}>Recent Activity</h3>
            <p style={{ color: '#666' }}>No recent activity</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        backgroundColor: '#3b82f6',
        color: '#eff6ff',
        textAlign: 'center',
        padding: '20px',
        fontSize: '14px'
      }}>
        © {new Date().getFullYear()} Trading Dashboard. All rights reserved.
      </footer>
    </div>
  )
}

export default Dashboard
