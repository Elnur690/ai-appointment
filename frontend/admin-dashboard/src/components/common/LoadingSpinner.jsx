import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex-center" style={{ padding: '2rem' }}>
      <div style={{
        width: '40px',
        height: '40px',
        border: '3px solid rgba(6, 182, 212, 0.2)',
        borderTopColor: 'var(--primary-start)',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }}></div>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
