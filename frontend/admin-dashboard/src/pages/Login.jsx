import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Sparkles } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, language, setLanguage } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError(isAz ? 'Zəhmət olmasa bütün xanaları doldurun' : 'Please fill in all fields');
      return;
    }
    try {
      await login(email, password);
      navigate('/');
    } catch {
      setError(isAz ? 'E-poçt və ya şifrə yanlışdır' : 'Invalid credentials');
    }
  };

  return (
    <div className="flex-center" style={{ minHeight: '100vh', position: 'relative', overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          top: '-10%',
          left: '-10%',
          width: '50vw',
          height: '50vw',
          background: 'radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%)',
          filter: 'blur(60px)',
          zIndex: 0,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '-10%',
          right: '-10%',
          width: '50vw',
          height: '50vw',
          background: 'radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%)',
          filter: 'blur(60px)',
          zIndex: 0,
        }}
      />

      <div className="glass-card animate-slide-up" style={{ width: '100%', maxWidth: '420px', padding: '2.5rem', zIndex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
          <div
            style={{
              display: 'inline-flex',
              background: 'rgba(255,255,255,0.06)',
              border: '1px solid var(--border-color)',
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
                padding: '0.28rem 0.65rem',
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
                border: 'none',
                cursor: 'pointer',
                padding: '0.28rem 0.65rem',
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

        <div className="flex-center" style={{ flexDirection: 'column', marginBottom: '2rem', textAlign: 'center' }}>
          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '16px', marginBottom: '1rem' }}>
            <Sparkles size={32} color="var(--primary-start)" />
          </div>
          <h1 className="gradient-text" style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>
            Randevu.vip Admin
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz
              ? 'Biznesləri, paketləri, ödəniş şlüzlərini və AI modellərini idarə etmək üçün daxil olun'
              : 'Sign in to manage tenants, plans, payment gateways & AI models'}
          </p>
        </div>

        {error && (
          <div
            style={{
              padding: '0.75rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid var(--error)',
              borderRadius: '8px',
              color: 'var(--error)',
              marginBottom: '1rem',
              fontSize: '0.875rem',
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">{isAz ? 'E-poçt Ünvanı' : 'Email Address'}</label>
            <input
              type="email"
              className="form-control"
              placeholder="admin@randevu.vip"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: '2rem' }}>
            <label className="form-label">{isAz ? 'Şifrə' : 'Password'}</label>
            <input
              type="password"
              className="form-control"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
            {isAz ? 'Daxil Ol' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
