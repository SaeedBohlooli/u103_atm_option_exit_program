import StatusIndicator from './StatusIndicator';
import React, { useEffect, useState, useMemo, useCallback } from 'react'
import { config } from './config'

// Style constants to prevent recreation on every render
const inputStyle = {
  flex: 1,
  padding: '2px 6px',
  border: '1px solid #d1d5db',
  borderRadius: '0',
  fontSize: '11px',
  fontFamily: 'monospace',
  backgroundColor: 'white'
}

const labelStyle = {
  fontSize: '11px',
  color: '#374151',
  fontWeight: '600',
  minWidth: '140px',
  fontFamily: 'monospace'
}

const fieldContainerStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '6px'
}

function OrderSetup({ onBack }) {
  // Reset handler to clear all form fields
  const handleReset = useCallback(() => {
    setFrequency('');
    setRollingNumber('');
    setAtmTrigger('');
    setSpxTrigger('');
    setBaseAtmTrigger('');
    setEntrySpx1('');
    setEntrySpx2('');
    setBaseAtm1('');
    setBaseAtm2('');
    setContracts1('');
    setContracts2('');
    setOptionType1('');
    setOptionType2('');
    setCloseShortStrike1('');
    setCloseShortStrike2('');
    setCloseLongStrike1('');
    setCloseLongStrike2('');
    setLimtOrderTypeLimit1('');
    setLimtOrderTypeLimit2('');
    setCloseShortStrikeCombo1('');
    setCloseShortStrikeCombo2('');
    setCloseLongStrikeCombo1('');
    setCloseLongStrikeCombo2('');
    setCloseLongStrikeSingleLeg1('');
    setCloseLongStrikeSingleLeg2('');
  }, []);
  const [records, setRecords] = useState([])
  const [wsStatus, setWsStatus] = useState('Disconnected')
  const [isReceivingData, setIsReceivingData] = useState(false)
  const [flaskApiStatus, setFlaskApiStatus] = useState('Checking...')
  const [spxPrice, setSpxPrice] = useState(null)
  const [prevSpxPrice, setPrevSpxPrice] = useState(null)
  const [dayHighestAtmStrike, setDayHighestAtmStrike] = useState(null)
  const [lastAtmStrike, setLastAtmStrike] = useState(null)
  const [diffHighBase, setDiffHighBase] = useState(null)
  const [diffBaseLast, setDiffBaseLast] = useState(null)
  const [callSpreadMax, setCallSpreadMax] = useState(null)
  const [putSpreadMax, setPutSpreadMax] = useState(null)
  const [callSpreadMin, setCallSpreadMin] = useState(null)
  const [putSpreadMin, setPutSpreadMin] = useState(null)
  const [callSpreadLatest, setCallSpreadLatest] = useState(null)
  const [putSpreadLatest, setPutSpreadLatest] = useState(null)
  
  // Form fields
  const [frequency, setFrequency] = useState('')
  const [rollingNumber, setRollingNumber] = useState('')
  const [atmTrigger, setAtmTrigger] = useState('')
  const [spxTrigger, setSpxTrigger] = useState('')
  const [baseAtmTrigger, setBaseAtmTrigger] = useState('')
  const [entrySpx1, setEntrySpx1] = useState('')
  const [entrySpx2, setEntrySpx2] = useState('')
  const [baseAtm1, setBaseAtm1] = useState('')
  const [baseAtm2, setBaseAtm2] = useState('')
  const [contracts1, setContracts1] = useState('')
  const [contracts2, setContracts2] = useState('')
  const [optionType1, setOptionType1] = useState('')
  const [optionType2, setOptionType2] = useState('')
  // Close Existing Positions
  const [closeShortStrike1, setCloseShortStrike1] = useState('')
  const [closeShortStrike2, setCloseShortStrike2] = useState('')
  const [closeLongStrike1, setCloseLongStrike1] = useState('')
  const [closeLongStrike2, setCloseLongStrike2] = useState('')
  const [limtOrderTypeLimit1, setLimtOrderTypeLimit1] = useState('')
  const [limtOrderTypeLimit2, setLimtOrderTypeLimit2] = useState('')
  // Cancel Open Pending Orders
  const [closeShortStrikeCombo1, setCloseShortStrikeCombo1] = useState('')
  const [closeShortStrikeCombo2, setCloseShortStrikeCombo2] = useState('')
  const [closeLongStrikeCombo1, setCloseLongStrikeCombo1] = useState('')
  const [closeLongStrikeCombo2, setCloseLongStrikeCombo2] = useState('')
  const [closeLongStrikeSingleLeg1, setCloseLongStrikeSingleLeg1] = useState('')
  const [closeLongStrikeSingleLeg2, setCloseLongStrikeSingleLeg2] = useState('')
  const [sortColumn, setSortColumn] = useState(null)
  const [sortDirection, setSortDirection] = useState('asc')

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    const formData = {
      request_type: 'SETUP_ORDER',
      status: 'WEB_SUBMITTED',
      frequency,
      rolling_number: rollingNumber,
      atm_trigger: atmTrigger,
      spx_price_trigger: spxTrigger,
      base_atm_trigger: baseAtmTrigger,
      orders: [
        {
          entry_spx_price: entrySpx1,
          base_atm_price: baseAtm1,
          contracts: contracts1,
          option_type: optionType1,
          close_short_strike: closeShortStrike1,
          close_long_strike: closeLongStrike1,
          limt_order_type_limit: limtOrderTypeLimit1,
          close_short_strike_combo: closeShortStrikeCombo1,
          close_long_strike_combo: closeLongStrikeCombo1,
          close_long_strike_single_leg: closeLongStrikeSingleLeg1
        },
        {
          entry_spx_price: entrySpx2,
          base_atm_price: baseAtm2,
          contracts: contracts2,
          option_type: optionType2,
          close_short_strike: closeShortStrike2,
          close_long_strike: closeLongStrike2,
          limt_order_type_limit: limtOrderTypeLimit2,
          close_short_strike_combo: closeShortStrikeCombo2,
          close_long_strike_combo: closeLongStrikeCombo2,
          close_long_strike_single_leg: closeLongStrikeSingleLeg2
        }
      ]
    }
    
    try {
      const response = await fetch(config.FLASK_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        console.log('Order setup submitted successfully')
        alert('Order setup saved successfully!')
        handleReset()
      } else {
        console.error('Failed to submit order setup')
        alert('Failed to save order setup')
      }
    } catch (error) {
      console.error('Error submitting order setup:', error)
      alert('Error saving order setup')
    }
  }, [frequency, rollingNumber, atmTrigger, spxTrigger, baseAtmTrigger, entrySpx1, entrySpx2, baseAtm1, baseAtm2, contracts1, contracts2, optionType1, optionType2, closeShortStrike1, closeShortStrike2, closeLongStrike1, closeLongStrike2, limtOrderTypeLimit1, limtOrderTypeLimit2, closeShortStrikeCombo1, closeShortStrikeCombo2, closeLongStrikeCombo1, closeLongStrikeCombo2, closeLongStrikeSingleLeg1, closeLongStrikeSingleLeg2])


  const handleSort = useCallback((column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }, [sortColumn, sortDirection])

  const sortedRecords = useMemo(() => {
    if (!sortColumn) return records
    
    return [...records].sort((a, b) => {
      let aVal = a[sortColumn];
      let bVal = b[sortColumn];
      // Special handling for timestamp/date columns
      if (sortColumn && sortColumn.toLowerCase().includes('time')) {
        const aDate = new Date(aVal);
        const bDate = new Date(bVal);
        if (!isNaN(aDate) && !isNaN(bDate)) {
          return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
        }
      }
      // Convert to numbers if possible
      const aNum = parseFloat(aVal);
      const bNum = parseFloat(bVal);
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
      }
      // String comparison
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [records, sortColumn, sortDirection])

  useEffect(() => {
    let ws
    let reconnectTimeout

    const connect = () => {
      ws = new WebSocket(config.WEBSOCKET_URL)

      ws.onopen = () => {
        setWsStatus('Connected')
      }

      ws.onmessage = (event) => {
        setIsReceivingData(true)
        setTimeout(() => setIsReceivingData(false), 2000)
        try {
          const data = JSON.parse(event.data)
          
          // Handle tick data for SPX price
          if (data.type === 'tick' && data.symbol === 'SPX') {
            setPrevSpxPrice((prev) => spxPrice);
            setSpxPrice(data.price);
          }
          
          // Check for application_state type OR if the wrapper exists
          if (data.type === 'application_state' || data.atm_straddle_tracker_obj_wrapper) {
            const wrapper = data.data.atm_straddle_tracker_obj_wrapper
            const trackerRecords = wrapper?.records || []
            setRecords(trackerRecords)
            setDayHighestAtmStrike(wrapper?.day_highest_atm_strike)
            setLastAtmStrike(wrapper?.last_atm_strike)
            setDiffHighBase(wrapper?.diff_high_base)
            setDiffBaseLast(wrapper?.diff_base_last)
            setCallSpreadMax(wrapper?.call_spread_max)
            setPutSpreadMax(wrapper?.put_spread_max)
            setCallSpreadMin(wrapper?.call_spread_min)
            setPutSpreadMin(wrapper?.put_spread_min)
            setCallSpreadLatest(wrapper?.call_spread_latest)
            setPutSpreadLatest(wrapper?.put_spread_latest)
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err)
        }
      }

      ws.onerror = (error) => {
        setWsStatus('Error')
        console.error('WebSocket error:', error)
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
    const interval = setInterval(checkHealth, 5000) // Check every 5 seconds

    return () => clearInterval(interval)
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
        <h1 style={{ margin: 0, fontSize: '24px' }}>Order Setup</h1>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          {/* 1st indicator (if any) can go here */}
          {/* WebSocket indicator - now second */}
          <div style={fieldContainerStyle}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: wsStatus === 'Connected' ? (isReceivingData ? '#22c55e' : '#86efac') : wsStatus === 'Error' ? '#fbbf24' : '#ef4444',
              boxShadow: isReceivingData ? '0 0 8px rgba(34, 197, 94, 0.8)' : 'none',
              animation: isReceivingData ? 'pulse 1s infinite' : 'none'
            }}></div>
            <span style={{ fontSize: '14px' }}>
              WS: {' '}
              <span style={{
                color:
                  wsStatus === 'Connected'
                    ? (isReceivingData ? '#22c55e' : '#86efac')
                    : wsStatus === 'Error'
                      ? '#fbbf24'
                      : '#fca5a5',
                fontWeight: '500',
                minWidth: 90,
                display: 'inline-block'
              }}>
                {wsStatus === 'Connected'
                  ? (isReceivingData ? 'Receiving' : 'Connected')
                  : wsStatus === 'Error'
                    ? 'Error'
                    : 'Disconnected'}
              </span>
            </span>
          </div>
          {/* Flask API indicator - now after WS */}
          <div style={fieldContainerStyle}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: flaskApiStatus === 'Connected' ? '#22c55e' : flaskApiStatus === 'Error' ? '#fbbf24' : '#ef4444'
            }}></div>
            <span style={{ fontSize: '14px' }}>
              Flask API: <span style={{ 
                color: flaskApiStatus === 'Connected' ? '#86efac' : '#fca5a5',
                fontWeight: '500'
              }}>{flaskApiStatus}</span>
            </span>
          </div>
          <button
            onClick={onBack}
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
            Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '30px', backgroundColor: '#f5f5f5' }}>
        <div style={{ maxWidth: '1600px', margin: '0 auto', display: 'flex', gap: '20px' }}>
          {/* Left Side - Table */}
          <div style={{
            flex: 2,
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            maxHeight: 'calc(100vh - 200px)',
            overflow: 'auto'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '24px', marginBottom: '15px' }}>
              <h2 style={{ margin: 0, color: '#1f2937', fontSize: '18px', display: 'inline-block' }}>ATM Straddle Tracker Records</h2>
              {spxPrice !== null && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '13px', color: '#6b7280', fontWeight: '600' }}>SPX Price: </span>
                  {(() => {
                    let color = '#d97706';
                    let arrow = '';
                    let percent = null;
                    if (prevSpxPrice !== null && spxPrice !== null) {
                      if (spxPrice > prevSpxPrice) {
                        color = '#22c55e'; // green
                        arrow = '▲';
                      } else if (spxPrice < prevSpxPrice) {
                        color = '#ef4444'; // red
                        arrow = '▼';
                      }
                      percent = ((spxPrice - prevSpxPrice) / prevSpxPrice) * 100;
                    }
                    return (
                      <>
                        <span style={{
                          fontSize: '22px',
                          color,
                          fontWeight: '900',
                          fontFamily: 'monospace',
                          letterSpacing: '1px',
                          textShadow: '0 1px 4px #fcd34d, 0 0px 2px #fff',
                          transition: 'color 0.3s'
                        }}>
                          {spxPrice.toFixed(2)} {arrow}
                        </span>
                        {percent !== null && (
                          <span style={{
                            fontSize: '13px',
                            color,
                            fontWeight: '700',
                            marginLeft: '8px',
                            fontFamily: 'monospace'
                          }}>
                            ({percent > 0 ? '+' : ''}{percent.toFixed(2)}%)
                          </span>
                        )}
                      </>
                    );
                  })()}
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: '30px', padding: '10px', backgroundColor: '#f9fafb', borderRadius: '4px', flexWrap: 'wrap', alignItems: 'flex-start' }}>
              <div>
                <span style={{ fontSize: '12px', color: '#6b7280', fontWeight: '500' }}>Highest ATM Straddle Value: </span>
                <span style={{ fontSize: '14px', color: '#1f2937', fontWeight: '600' }}>{dayHighestAtmStrike ?? 'N/A'}</span>
              </div>
              <div>
                <span style={{ fontSize: '12px', color: '#6b7280', fontWeight: '500' }}>Last ATM: </span>
                <span style={{ fontSize: '14px', color: '#1f2937', fontWeight: '600' }}>{lastAtmStrike ?? 'N/A'}</span>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '500', marginBottom: '2px' }}>Diff (High - Base): <span style={{ fontSize: '14px', color: '#1f2937', fontWeight: '600' }}>{diffHighBase ?? 'N/A'}</span></div>
                <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '500' }}>Diff (Base - Last): <span style={{ fontSize: '14px', color: '#1f2937', fontWeight: '600' }}>{diffBaseLast ?? 'N/A'}</span></div>
              </div>
              <div style={{ marginLeft: 'auto' }}>
                <table style={{ borderCollapse: 'collapse', fontSize: '11px' }}>
                  <thead>
                    <tr>
                      <th style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap' }}></th>
                      <th style={{ padding: '4px 8px', textAlign: 'center', borderBottom: '1px solid #d1d5db', color: '#6b7280', fontWeight: '500' }}>Call</th>
                      <th style={{ padding: '4px 8px', textAlign: 'center', borderBottom: '1px solid #d1d5db', color: '#6b7280', fontWeight: '500' }}>Put</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ padding: '4px 8px', color: '#6b7280', fontWeight: '500' }}>Spread Max</td>
                      <td style={{ padding: '4px 8px', textAlign: 'center', color: '#1f2937', fontWeight: '600' }}>{callSpreadMax ?? 'N/A'}</td>
                      <td style={{ padding: '4px 8px', textAlign: 'center', color: '#1f2937', fontWeight: '600' }}>{putSpreadMax ?? 'N/A'}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '4px 8px', color: '#6b7280', fontWeight: '500' }}>Spread Min</td>
                      <td style={{ padding: '4px 8px', textAlign: 'center', color: '#1f2937', fontWeight: '600' }}>{callSpreadMin ?? 'N/A'}</td>
                      <td style={{ padding: '4px 8px', textAlign: 'center', color: '#1f2937', fontWeight: '600' }}>{putSpreadMin ?? 'N/A'}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '4px 8px', color: '#6b7280', fontWeight: '500' }}>Spread Last</td>
                      <td style={{ padding: '4px 8px', textAlign: 'center', color: '#1f2937', fontWeight: '600' }}>{callSpreadLatest ?? 'N/A'}</td>
                      <td style={{ padding: '4px 8px', textAlign: 'center', color: '#1f2937', fontWeight: '600' }}>{putSpreadLatest ?? 'N/A'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <p style={{ fontSize: '12px', color: '#666', marginBottom: '15px' }}>
              Records count: {records.length} | WS Status: {wsStatus}
            </p>
            {records.length === 0 ? (
              <div style={{ 
                padding: '20px', 
                backgroundColor: '#fef3c7', 
                borderRadius: '4px',
                color: '#92400e'
              }}>
                <p style={{ margin: 0 }}>
                  {wsStatus === 'Connected' 
                    ? 'Connected to WebSocket, waiting for data...' 
                    : `WebSocket status: ${wsStatus}. No records available yet.`}
                </p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                      <th onClick={() => handleSort('timestamp')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Timestamp {sortColumn === 'timestamp' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('symbol_price')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        SPX Price {sortColumn === 'symbol_price' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('atm_strike')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        ATM Strike {sortColumn === 'atm_strike' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('call_bid')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Call Bid {sortColumn === 'call_bid' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('call_ask')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Call Ask {sortColumn === 'call_ask' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('put_bid')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Put Bid {sortColumn === 'put_bid' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('put_ask')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Put Ask {sortColumn === 'put_ask' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('sum_put_call_ask')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Sum Put+Call Ask {sortColumn === 'sum_put_call_ask' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('difference')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Difference {sortColumn === 'difference' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('x_diffs_total')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        x_diffs_total {sortColumn === 'x_diffs_total' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('call_spread')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Call Spread {sortColumn === 'call_spread' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                      <th onClick={() => handleSort('put_spread')} style={{ padding: '8px', textAlign: 'left', fontWeight: '600', color: '#374151', whiteSpace: 'nowrap', cursor: 'pointer', userSelect: 'none' }}>
                        Put Spread {sortColumn === 'put_spread' && (sortDirection === 'asc' ? '▲' : '▼')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedRecords.map((record, index) => (
                      <tr key={index} style={{ 
                        borderBottom: '1px solid #e5e7eb',
                        backgroundColor: index % 2 === 0 ? 'white' : '#f9fafb'
                      }}>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.timestamp}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.symbol_price}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.atm_strike}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.call_bid}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.call_ask}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.put_bid}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.put_ask}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.sum_put_call_ask}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.difference}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.x_diffs_total}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.call_spread}</td>
                        <td style={{ padding: '8px', color: '#6b7280', whiteSpace: 'nowrap' }}>{record.put_spread}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Right Side - Content */}
          <div style={{
            flex: 1,
            backgroundColor: '#f8f9fa',
            padding: '10px',
            borderRadius: '0',
            border: '1px solid #d1d5db'
          }}>
            <h2 style={{ marginTop: 0, marginBottom: '6px', color: '#1f2937', fontSize: '13px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.5px', borderBottom: '2px solid #3b82f6', paddingBottom: '3px' }}>Order Setup</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  Time Setup Frequency
                </label>
                <input
                  type="text"
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  Rolling Entries
                </label>
                <input
                  type="text"
                  value={rollingNumber}
                  onChange={(e) => setRollingNumber(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  ATM Trigger
                </label>
                <input
                  type="text"
                  value={atmTrigger}
                  onChange={(e) => setAtmTrigger(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  SPX Trigger (Drop Negative)
                </label>
                <input
                  type="text"
                  value={spxTrigger}
                  onChange={(e) => setSpxTrigger(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  Base ATM Trigger
                </label>
                <input
                  type="text"
                  value={baseAtmTrigger}
                  onChange={(e) => setBaseAtmTrigger(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={{ margin: '16px 0 4px 0', borderTop: '2px solid #3b82f6', paddingTop: '8px' }}>
                <h3 style={{ margin: 0, color: '#1f2937', fontSize: '13px', fontWeight: '700', textTransform: 'uppercase', fontFamily: 'monospace' }}>Manual Entry</h3>
              </div>
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  Entry Level SPX Price
                </label>
                <input
                  type="text"
                  value={entrySpx1}
                  onChange={(e) => setEntrySpx1(e.target.value)}
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={entrySpx2}
                  onChange={(e) => setEntrySpx2(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  Base ATM
                </label>
                <input
                  type="text"
                  value={baseAtm1}
                  onChange={(e) => setBaseAtm1(e.target.value)}
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={baseAtm2}
                  onChange={(e) => setBaseAtm2(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  Contracts
                </label>
                <input
                  type="text"
                  value={contracts1}
                  onChange={(e) => setContracts1(e.target.value)}
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={contracts2}
                  onChange={(e) => setContracts2(e.target.value)}
                  style={inputStyle}
                />
              </div>
              
              <div style={fieldContainerStyle}>
                <label style={labelStyle}>
                  Option Type Put Call
                </label>
                <select
                  value={optionType1}
                  onChange={(e) => setOptionType1(e.target.value)}
                  style={{ ...inputStyle, minWidth: 70 }}
                >
                  <option value="">Select</option>
                  <option value="Call">Call</option>
                  <option value="Put">Put</option>
                </select>
                <select
                  value={optionType2}
                  onChange={(e) => setOptionType2(e.target.value)}
                  style={{ ...inputStyle, minWidth: 70 }}
                >
                  <option value="">Select</option>
                  <option value="Call">Call</option>
                  <option value="Put">Put</option>
                </select>
              </div>
              
              <div style={{ borderTop: '2px solid #3b82f6', paddingTop: '4px', marginTop: '4px' }}>
                <h3 style={{ margin: '0 0 2px 0', color: '#1f2937', fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', fontFamily: 'monospace' }}>Close Existing Positions</h3>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  <div style={fieldContainerStyle}>
                    <label style={labelStyle}>
                      Close Short Strike
                    </label>
                    <input
                      type="text"
                      value={closeShortStrike1}
                      onChange={(e) => setCloseShortStrike1(e.target.value)}
                      style={inputStyle}
                    />
                    <input
                      type="text"
                      value={closeShortStrike2}
                      onChange={(e) => setCloseShortStrike2(e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                  
                  <div style={fieldContainerStyle}>
                    <label style={labelStyle}>
                      Close Long Strike
                    </label>
                    <input
                      type="text"
                      value={closeLongStrike1}
                      onChange={(e) => setCloseLongStrike1(e.target.value)}
                      style={inputStyle}
                    />
                    <input
                      type="text"
                      value={closeLongStrike2}
                      onChange={(e) => setCloseLongStrike2(e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                  
                  <div style={fieldContainerStyle}>
                    <label style={labelStyle}>
                      LMT Order Type's limit
                    </label>
                    <input
                      type="text"
                      value={limtOrderTypeLimit1}
                      onChange={(e) => setLimtOrderTypeLimit1(e.target.value)}
                      style={inputStyle}
                    />
                    <input
                      type="text"
                      value={limtOrderTypeLimit2}
                      onChange={(e) => setLimtOrderTypeLimit2(e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                </div>
              </div>
              
              <div style={{ borderTop: '2px solid #3b82f6', paddingTop: '4px', marginTop: '4px' }}>
                <h3 style={{ margin: '0 0 2px 0', color: '#1f2937', fontSize: '11px', fontWeight: '700', textTransform: 'uppercase', fontFamily: 'monospace' }}>Cancel Open Pending Orders</h3>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  <div style={fieldContainerStyle}>
                    <label style={labelStyle}>
                      Close Short Strike of Combo
                    </label>
                    <input
                      type="text"
                      value={closeShortStrikeCombo1}
                      onChange={(e) => setCloseShortStrikeCombo1(e.target.value)}
                      style={inputStyle}
                    />
                    <input
                      type="text"
                      value={closeShortStrikeCombo2}
                      onChange={(e) => setCloseShortStrikeCombo2(e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                  
                  <div style={fieldContainerStyle}>
                    <label style={labelStyle}>
                      Close Long Strike of Combo
                    </label>
                    <input
                      type="text"
                      value={closeLongStrikeCombo1}
                      onChange={(e) => setCloseLongStrikeCombo1(e.target.value)}
                      style={inputStyle}
                    />
                    <input
                      type="text"
                      value={closeLongStrikeCombo2}
                      onChange={(e) => setCloseLongStrikeCombo2(e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                  
                  <div style={fieldContainerStyle}>
                    <label style={labelStyle}>
                      Close Long Strike single leg
                    </label>
                    <input
                      type="text"
                      value={closeLongStrikeSingleLeg1}
                      onChange={(e) => setCloseLongStrikeSingleLeg1(e.target.value)}
                      style={inputStyle}
                    />
                    <input
                      type="text"
                      value={closeLongStrikeSingleLeg2}
                      onChange={(e) => setCloseLongStrikeSingleLeg2(e.target.value)}
                      style={inputStyle}
                    />
                  </div>
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center', marginTop: '16px', marginBottom: '8px' }}>
                <StatusIndicator
                  wsStatus={wsStatus}
                  isReceivingData={isReceivingData}
                  flaskApiStatus={flaskApiStatus}
                  fieldContainerStyle={fieldContainerStyle}
                />
              </div>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '12px' }}>
                <button type="submit" style={{ padding: '8px 20px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', fontSize: '14px', cursor: 'pointer', fontWeight: 600 }}>
                  Submit
                </button>
                <button type="button" onClick={handleReset} style={{ padding: '8px 20px', backgroundColor: '#f3f4f6', color: '#1f2937', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '14px', cursor: 'pointer', fontWeight: 600 }}>
                  Reset
                </button>
              </div>
              <footer
                style={{
                  color: '#eff6ff',
                  textAlign: 'center',
                  padding: '20px',
                  fontSize: '14px'
                }}
              >
                © {new Date().getFullYear()} Trading Dashboard. All rights reserved.
              </footer>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}

export default OrderSetup




