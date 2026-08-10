import React from 'react';

const colors = {
  confirmed: { bg: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' },
  pending: { bg: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' },
  completed: { bg: 'rgba(14, 165, 233, 0.1)', color: '#0ea5e9' },
  cancelled: { bg: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)' },
  no_show: { bg: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)' }
};

export const StatusBadge = ({ status }) => {
  const style = colors[status] || colors.pending;
  return (
    <span style={{
      padding: '0.25rem 0.75rem',
      borderRadius: '9999px',
      fontSize: '0.875rem',
      backgroundColor: style.bg,
      color: style.color,
      textTransform: 'capitalize'
    }}>
      {status.replace('_', ' ')}
    </span>
  );
};\n