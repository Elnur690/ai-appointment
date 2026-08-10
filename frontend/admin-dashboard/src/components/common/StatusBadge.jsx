import React from 'react';

const StatusBadge = ({ status }) => {
  const getBadgeClass = () => {
    switch (status.toLowerCase()) {
      case 'active': return 'badge-active';
      case 'suspended': return 'badge-suspended';
      case 'trial': return 'badge-trial';
      default: return '';
    }
  };

  return (
    <span className={`badge ${getBadgeClass()}`}>
      <span style={{ 
        width: 6, height: 6, borderRadius: '50%', 
        background: 'currentColor', display: 'inline-block' 
      }}></span>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

export default StatusBadge;
