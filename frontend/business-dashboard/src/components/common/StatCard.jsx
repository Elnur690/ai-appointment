import React from 'react';

export const StatCard = ({ title, value, icon: Icon, trend }) => (
  <div className="glass hover-lift" style={{ padding: '1.5rem', flex: 1, minWidth: '200px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
      <span style={{ color: 'var(--text-secondary)' }}>{title}</span>
      {Icon && <Icon size={24} style={{ color: '#0ea5e9' }} />}
    </div>
    <h3 style={{ margin: 0, fontSize: '2rem' }}>{value}</h3>
    {trend && (
      <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: trend.positive ? 'var(--success)' : 'var(--error)' }}>
        {trend.positive ? '+' : '-'}{trend.value}% from last month
      </div>
    )}
  </div>
);\n