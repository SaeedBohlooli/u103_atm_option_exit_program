import React from 'react';

const StatusIndicator = ({ wsStatus, isReceivingData, flaskApiStatus, fieldContainerStyle }) => (
  <>
    <div style={fieldContainerStyle}>
      <div style={{
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        backgroundColor:
          wsStatus === 'Connected'
            ? (isReceivingData ? '#22c55e' : '#86efac')
            : wsStatus === 'Error'
              ? '#fbbf24'
              : '#ef4444',
        border: isReceivingData ? '2px solid #16a34a' : '2px solid transparent',
        transition: 'background 0.3s, border 0.3s'
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
  </>
);

export default StatusIndicator;
