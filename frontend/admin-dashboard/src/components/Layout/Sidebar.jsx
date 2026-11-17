import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Layers,
  CreditCard,
  Handshake,
  Wallet,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { BrandLogo } from '../common/BrandLogo';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout, language, setLanguage } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: isAz ? 'İdarə Paneli' : 'Dashboard' },
    { path: '/businesses', icon: Building2, label: isAz ? 'Bizneslər' : 'Businesses' },
    { path: '/plans', icon: Layers, label: isAz ? 'Paketlər və Kanallar' : 'Plans & Channels' },
    { path: '/payment-gateways', icon: Wallet, label: isAz ? 'Ödəniş Şlüzləri' : 'Payment Gateways' },
    { path: '/resellers', icon: Handshake, label: isAz ? 'Partnyorlar (Resellers)' : 'Resellers & Partners' },
    { path: '/subscriptions', icon: CreditCard, label: isAz ? 'Abunəliklər' : 'Subscriptions' },
  ];

  return (
    <div
      style={{
        width: collapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)',
        background: 'var(--surface-color)',
        borderRight: '1px solid var(--border-color)',
        transition: 'width 0.3s ease',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
      }}
    >
      <div
        style={{
          padding: '1.25rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          borderBottom: '1px solid var(--border-color)',
          gap: '0.5rem',
        }}
      >
        {!collapsed && (
          <NavLink to="/" style={{ textDecoration: 'none' }}>
            <BrandLogo size={32} fontSize="1.2rem" />
          </NavLink>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className="btn-ghost" style={{ padding: '0.25rem', border: 'none' }}>
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {!collapsed && (
        <div style={{ padding: '0.75rem 1.25rem 0', display: 'flex', justifyContent: 'center' }}>
          <div
            style={{
              display: 'inline-flex',
              width: '100%',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border-color)',
              borderRadius: '999px',
              padding: '0.18rem',
            }}
          >
            <button
              type="button"
              onClick={() => setLanguage('az')}
              style={{
                flex: 1,
                border: 'none',
                cursor: 'pointer',
                padding: '0.3rem 0.5rem',
                borderRadius: '999px',
                fontSize: '0.75rem',
                fontWeight: 700,
                background: isAz ? 'var(--primary-start)' : 'transparent',
                color: isAz ? '#fff' : 'var(--text-secondary)',
              }}
            >
              AZ
            </button>
            <button
              type="button"
              onClick={() => setLanguage('en')}
              style={{
                flex: 1,
                border: 'none',
                cursor: 'pointer',
                padding: '0.3rem 0.5rem',
                borderRadius: '999px',
                fontSize: '0.75rem',
                fontWeight: 700,
                background: !isAz ? 'var(--primary-start)' : 'transparent',
                color: !isAz ? '#fff' : 'var(--text-secondary)',
              }}
            >
              EN
            </button>
          </div>
        </div>
      )}

      <nav style={{ flex: 1, padding: '1.25rem 0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              color: isActive ? 'white' : 'var(--text-secondary)',
              background: isActive ? 'var(--primary-gradient)' : 'transparent',
              textDecoration: 'none',
              fontWeight: 500,
              transition: 'all 0.2s',
              justifyContent: collapsed ? 'center' : 'flex-start',
            })}
          >
            <item.icon size={20} />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
        {!collapsed && (
          <div style={{ marginBottom: '1rem' }}>
            <p style={{ margin: 0, fontWeight: 500 }}>{user?.name}</p>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>{user?.email}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="btn btn-ghost"
          style={{ width: '100%', justifyContent: collapsed ? 'center' : 'flex-start', color: 'var(--error)' }}
        >
          <LogOut size={20} />
          {!collapsed && (isAz ? 'Çıxış' : 'Logout')}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
