import React, { useEffect } from 'react';
import { Outlet, Navigate, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { LogOut, User } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import './Layout.css';

export const Layout = () => {
  const { isAuthenticated, user, businessContext, fetchBusinessProfile, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      fetchBusinessProfile();
    }
  }, [isAuthenticated, fetchBusinessProfile]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <Sidebar />
      <div className="main-content">
        <header className="topbar glass" style={{ borderRadius: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontWeight: 600 }}>{businessContext?.name || 'Business Workspace'}</span>
            {businessContext?.custom_domain && (
              <span className="badge badge-info">{businessContext.custom_domain}</span>
            )}
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              <User size={16} />
              <span>{user?.email || user?.name || 'Owner'}</span>
            </div>
            <button
              onClick={handleLogout}
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            >
              <LogOut size={15} />
              Logout
            </button>
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
