import React from 'react';

export const BrandLogo = ({
  size = 36,
  fontSize = '1.35rem',
  label = 'Randevu.vip',
  showText = true,
}) => {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.65rem' }}>
      <img
        src="/logo.png"
        alt="Randevu.vip Logo"
        width={size}
        height={size}
        style={{
          width: `${size}px`,
          height: `${size}px`,
          borderRadius: `${Math.round(size * 0.26)}px`,
          objectFit: 'cover',
          boxShadow: '0 4px 14px rgba(212, 175, 55, 0.25), 0 0 0 1px rgba(212, 175, 55, 0.45)',
          flexShrink: 0,
        }}
      />
      {showText && (
        <span className="gradient-text" style={{ fontSize, fontWeight: 800, letterSpacing: '-0.02em' }}>
          {label}
        </span>
      )}
    </span>
  );
};

export default BrandLogo;
