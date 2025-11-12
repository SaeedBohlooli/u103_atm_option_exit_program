import React, { useState } from 'react'

export default function SetParameters({ onSubmit } = {}) {
  const [values, setValues] = useState({
    base_atm_straddle: '1',
    contracts: '1',
    multiplier: '1',
    strike: '1',
  })

  const [errors, setErrors] = useState({})
  const [submitted, setSubmitted] = useState(null)
  const [loading, setLoading] = useState(false)
  const [serverResponse, setServerResponse] = useState(null)
  const [serverError, setServerError] = useState(null)

  function handleChange(e) {
    const { name, value } = e.target
    setValues(v => ({ ...v, [name]: value }))
    setErrors(e => ({ ...e, [name]: undefined }))
  }

  function validate() {
    const errs = {}
  if (!values.base_atm_straddle) errs.base_atm_straddle = 'Required'
  else if (Number.isNaN(Number(values.base_atm_straddle))) errs.base_atm_straddle = 'Must be a number'

    if (!values.contracts) errs.contracts = 'Required'
    else if (!Number.isInteger(Number(values.contracts))) errs.contracts = 'Must be an integer'

    if (!values.multiplier) errs.multiplier = 'Required'
    else if (Number.isNaN(Number(values.multiplier))) errs.multiplier = 'Must be a number'

    if (!values.strike) errs.strike = 'Required'
    else if (Number.isNaN(Number(values.strike))) errs.strike = 'Must be a number'

    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!validate()) return
    const payload = {
      base_atm_straddle: Number(values.base_atm_straddle),
      contracts: parseInt(values.contracts, 10),
      multiplier: Number(values.multiplier),
      strike: Number(values.strike),
    }
    setSubmitted(payload)
    if (typeof onSubmit === 'function') onSubmit(payload)

    // POST to Flask API
    setLoading(true)
    setServerResponse(null)
    setServerError(null)

    fetch('/api/update_params', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(async res => {
        const text = await res.text()
        // Try parse JSON, fallback to text
        try {
          const data = JSON.parse(text)
          if (!res.ok) throw new Error(data.error || JSON.stringify(data))
          setServerResponse(data)
        } catch (parseErr) {
          if (!res.ok) throw new Error(text || res.statusText)
          setServerResponse(text)
        }
      })
      .catch(err => {
        setServerError(err.message || String(err))
      })
      .finally(() => setLoading(false))
  }

  return (
    <div style={{ padding: 20, fontFamily: 'system-ui, Arial', maxWidth: 480 }}>
      <h2>Set Parameters</h2>
      <h3>Ver 1.3</h3>
      <form onSubmit={handleSubmit} noValidate>
        <label style={{ display: 'block', marginBottom: 8 }}>
          Base ATM Straddle Value
          <input
            name="base_atm_straddle"
            value={values.base_atm_straddle}
            onChange={handleChange}
            inputMode="decimal"
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
          />
          {errors.base_atm_straddle && (
            <div style={{ color: 'crimson', fontSize: 13 }}>{errors.base_atm_straddle}</div>
          )}
        </label>

       <label style={{ display: 'block', marginBottom: 8 }}>
          Multiplier
          <input
            name="multiplier"
            value={values.multiplier}
            onChange={handleChange}
            inputMode="decimal"
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
          />
          {errors.multiplier && (
            <div style={{ color: 'crimson', fontSize: 13 }}>{errors.multiplier}</div>
          )}
        </label>

        <label style={{ display: 'block', marginBottom: 8 }}>
          Contracts
          <input
            name="contracts"
            value={values.contracts}
            onChange={handleChange}
            inputMode="numeric"
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
          />
          {errors.contracts && (
            <div style={{ color: 'crimson', fontSize: 13 }}>{errors.contracts}</div>
          )}
        </label>



        <label style={{ display: 'block', marginBottom: 12 }}>
          Strike
          <input
            name="strike"
            value={values.strike}
            onChange={handleChange}
            inputMode="decimal"
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
          />
          {errors.strike && (
            <div style={{ color: 'crimson', fontSize: 13 }}>{errors.strike}</div>
          )}
        </label>

        <div style={{ display: 'flex', gap: 8 }}>
          <button type="submit" style={{ padding: '8px 12px' }}>
            Submit
          </button>
          <button
            type="button"
            onClick={() => {
              setValues({ base_atm_straddle: '1', contracts: '1', multiplier: '1', strike: '1' })
              setErrors({})
              setSubmitted(null)
              setServerResponse(null)
              setServerError(null)
            }}
            style={{ padding: '8px 12px' }}
          >
            Reset
          </button>
        </div>
      </form>

      {submitted && (
        <div style={{ marginTop: 16, padding: 12, background: '#f6f8fa', borderRadius: 6 }}>
          <strong>Submitted values</strong>
          <pre style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{JSON.stringify(submitted, null, 2)}</pre>
        </div>
      )}

      {loading && (
        <div style={{ marginTop: 12 }}>Sending to server…</div>
      )}

      {serverResponse && (
        <div style={{ marginTop: 12, padding: 12, background: '#e6ffed', borderRadius: 6 }}>
          <strong>Server response</strong>
          <pre style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{JSON.stringify(serverResponse, null, 2)}</pre>
        </div>
      )}

      {serverError && (
        <div style={{ marginTop: 12, padding: 12, background: '#ffecec', borderRadius: 6, color: '#a00' }}>
          <strong>Server error</strong>
          <div style={{ marginTop: 8 }}>{serverError}</div>
        </div>
      )}
    </div>
  )
}
