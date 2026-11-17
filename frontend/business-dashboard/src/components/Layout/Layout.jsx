import React, { useEffect } from 'react';
import { Outlet, Navigate, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { LogOut, User } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { UI_TEXT } from '../../i18n/translations';
import './Layout.css';

export const Layout = () => {
  const { isAuthenticated, user, businessContext, fetchBusinessProfile, logout, language, setLanguage } = useAuthStore();
  const navigate = useNavigate();
  const lang = language || 'az';
  const t = (UI_TEXT[lang] || UI_TEXT.az).sidebar;

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
            <span style={{ fontWeight: 600 }}>{businessContext?.name || t.workspace}</span>
            {businessContext?.custom_domain && (
              <span className="badge badge-info">{businessContext.custom_domain}</span>
            )}
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            {/* Language Switcher (AZ default | EN) */}
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border)',
                borderRadius: '999px',
                padding: '0.18rem',
              }}
            >
              <button
                type="button"
                onClick={() => setLanguage('az')}
                style={{
                  border: 'none',
                  cursor: 'pointer',
                  padding: '0.28rem 0.6rem',
                  borderRadius: '999px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  background: lang === 'az' ? 'var(--primary)' : 'transparent',
                  color: lang === 'az' ? '#fff' : 'var(--text-secondary)',
                }}
              >
                AZ
              </button>
              <button
                type="button"
                onClick={() => setLanguage('en')}
                style={{
                  border: 'none',
                  cursor: 'pointer',
                  padding: '0.28rem 0.6rem',
                  borderRadius: '999px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  background: lang === 'en' ? 'var(--primary)' : 'transparent',
                  color: lang === 'en' ? '#fff' : 'var(--text-secondary)',
                }}
              >
                EN
              </button>
            </div>

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
              {t.logout}
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
