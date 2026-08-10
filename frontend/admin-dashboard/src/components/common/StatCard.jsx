import React from 'react';

const StatCard = ({ title, value, icon: Icon, trend, trendValue }) => {
  return (
    <div className="glass-card" style={{ padding: '1.5rem' }}>
      <div className="flex-between" style={{ marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', fontWeight: 500, margin: 0 }}>
          {title}
        </h3>
        <div style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
          <Icon size={20} color="var(--primary-start)" />
        </div>
      </div>
      <div className="flex-between" style={{ alignItems: 'flex-end' }}>
        <h2 style={{ fontSize: '1.875rem', margin: 0, fontWeight: 700 }}>{value}</h2>
        {trend && (
          <span style={{ 
            fontSize: '0.875rem', 
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            color: trend === 'up' ? 'var(--success)' : 'var(--error)'
          }}>
            {trend === 'up' ? '↑' : '↓'} {trendValue}
          </span>
        )}
      </div>
    </div>
  );
};

export default StatCard;
