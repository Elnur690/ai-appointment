import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Building2, Layers, CreditCard, LogOut, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/businesses', icon: Building2, label: 'Businesses' },
    { path: '/plans', icon: Layers, label: 'Plans' },
    { path: '/subscriptions', icon: CreditCard, label: 'Subscriptions' },
  ];

  return (
    <div style={{
      width: collapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)',
      background: 'var(--surface-color)',
      borderRight: '1px solid var(--border-color)',
      transition: 'width 0.3s ease',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      position: 'sticky',
      top: 0
    }}>
      <div style={{ 
        padding: '1.5rem', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: collapsed ? 'center' : 'space-between',
        borderBottom: '1px solid var(--border-color)'
      }}>
        {!collapsed && <h2 className="gradient-text" style={{ margin: 0, fontSize: '1.25rem' }}>AI Admin</h2>}
        <button onClick={() => setCollapsed(!collapsed)} className="btn-ghost" style={{ padding: '0.25rem', border: 'none' }}>
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <nav style={{ flex: 1, padding: '1.5rem 0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
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
              justifyContent: collapsed ? 'center' : 'flex-start'
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
        <button onClick={handleLogout} className="btn btn-ghost" style={{ width: '100%', justifyContent: collapsed ? 'center' : 'flex-start', color: 'var(--error)' }}>
          <LogOut size={20} />
          {!collapsed && 'Logout'}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
