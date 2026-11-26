import React, { useEffect, useState } from 'react';
import { Outlet, Navigate, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { LogOut, User, Sun, Moon } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { UI_TEXT } from '../../i18n/translations';
import './Layout.css';

export const Layout = () => {
  const { isAuthenticated, user, businessContext, fetchBusinessProfile, logout, language, setLanguage } = useAuthStore();
  const navigate = useNavigate();
  const lang = language || 'az';
  const t = (UI_TEXT[lang] || UI_TEXT.az).sidebar;
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('randevu_theme') || 'dark';
    } catch {
      return 'dark';
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('randevu_theme', theme);
    } catch {}
  }, [theme]);

  useEffect(() => {
    if (isAuthenticated && user?.role !== 'reseller' && user?.role !== 'saas_owner') {
      fetchBusinessProfile();
    }
  }, [isAuthenticated, user?.role, fetchBusinessProfile]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role === 'reseller') {
    return <Navigate to="/partner" replace />;
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (user?.role === 'saas_owner') {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
        }}
      >
        <div className="glass-card" style={{ maxWidth: '460px', width: '100%', padding: '2rem', textAlign: 'center' }}>
          <h2 style={{ marginBottom: '0.75rem' }}>
            {lang === 'en' ? 'Admin Account Detected' : 'Admin Hesabı Aşkar Edildi'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: 1.55 }}>
            {lang === 'en'
              ? 'This account has Platform Administrator (saas_owner) privileges and does not belong to a business workspace. Please sign in through the Admin Dashboard.'
              : 'Bu hesab Platforma Administratoru (saas_owner) hüququna malikdir və biznes panelinə aid deyil. Zəhmət olmasa Admin Panelindən daxil olun.'}
          </p>
          <button
            type="button"
            onClick={handleLogout}
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            <LogOut size={16} />
            {lang === 'en' ? 'Sign Out & Switch Account' : 'Çıxış Et və Hesabı Dəyiş'}
          </button>
        </div>
      </div>
    );
  }

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
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button
              type="button"
              onClick={() => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))}
              className="btn btn-secondary"
              style={{ padding: '0.38rem 0.55rem', minHeight: 'auto' }}
              title={theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>
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
