import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { UI_TEXT, getPlanFeatureItems } from '../i18n/translations';
import api from '../api/client';
import { Sparkles, MessageSquare, Calendar, ShieldCheck, Globe, Check, X } from 'lucide-react';

const Login = ({ initialMode = 'login' }) => {
  const [searchParams] = useSearchParams();
  const refParam = searchParams.get('ref') || '';
  const [mode, setMode] = useState(refParam ? 'register' : initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [phone, setPhone] = useState('');
  const [referralCode, setReferralCode] = useState(refParam);
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [plans, setPlans] = useState([]);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { login, fetchBusinessProfile, language, setLanguage } = useAuthStore();
  const navigate = useNavigate();
  const lang = language || 'az';
  const t = (UI_TEXT[lang] || UI_TEXT.az).auth;

  useEffect(() => {
    api
      .get('/auth/plans')
      .then((res) => {
        const list = res.data || [];
        setPlans(list);
        if (list.length > 0 && !selectedPlanId) {
          setSelectedPlanId(list[0].id);
        }
      })
      .catch(() => setPlans([]));
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('access_token', res.data.access_token);
      login({
        name: email.split('@')[0],
        email,
        role: res.data.role || 'owner',
        business_id: res.data.business_id,
      });
      await fetchBusinessProfile();
      navigate('/');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          (lang === 'en' ? 'Invalid email or password.' : 'E-poçt və ya şifrə yanlışdır.')
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const res = await api.post('/auth/register', {
        business_name: businessName,
        owner_name: ownerName || businessName,
        email,
        password,
        phone: phone || null,
        referral_code: referralCode || null,
        plan_id: selectedPlanId || null,
      });
      localStorage.setItem('access_token', res.data.access_token);
      login({
        name: businessName,
        email,
        role: res.data.role || 'owner',
        business_id: res.data.business_id,
      });
      await fetchBusinessProfile();
      navigate('/');
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          (lang === 'en'
            ? 'Registration failed. Please check your details.'
            : 'Qeydiyyat zamanı xəta baş verdi. Məlumatları yoxlayın.')
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        padding: '2rem 1.5rem',
        maxWidth: '1280px',
        margin: '0 auto',
      }}
    >
      {/* Top Navbar */}
      <header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '3rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Sparkles size={28} color="var(--primary)" />
          <span className="text-gradient" style={{ fontSize: '1.6rem', fontWeight: 700 }}>
            Randevu.vip
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Language Switcher (AZ default | EN) */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border)',
              borderRadius: '999px',
              padding: '0.2rem',
            }}
          >
            <button
              type="button"
              onClick={() => setLanguage('az')}
              style={{
                border: 'none',
                cursor: 'pointer',
                padding: '0.35rem 0.7rem',
                borderRadius: '999px',
                fontSize: '0.8rem',
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
                padding: '0.35rem 0.7rem',
                borderRadius: '999px',
                fontSize: '0.8rem',
                fontWeight: 700,
                background: lang === 'en' ? 'var(--primary)' : 'transparent',
                color: lang === 'en' ? '#fff' : 'var(--text-secondary)',
              }}
            >
              EN
            </button>
          </div>

          <button
            type="button"
            className={`btn ${mode === 'login' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setMode('login');
              setError('');
            }}
          >
            {t.signInTab}
          </button>
          <button
            type="button"
            className={`btn ${mode === 'register' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setMode('register');
              setError('');
            }}
          >
            {t.registerTab}
          </button>
        </div>
      </header>

      {/* Main Split Grid: Value Proposition + Auth Form */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '3rem',
          alignItems: 'start',
          marginBottom: '4rem',
        }}
      >
        <div>
          <span className="badge badge-info" style={{ marginBottom: '1rem', display: 'inline-block' }}>
            {t.heroBadge}
          </span>
          <h1 style={{ fontSize: '2.4rem', lineHeight: 1.2, marginBottom: '1.25rem' }}>{t.heroTitle}</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: 1.6, marginBottom: '2rem' }}>
            {t.heroDesc}
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <MessageSquare size={22} color="var(--primary)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{t.card1Title}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.card1Desc}</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <Calendar size={22} color="var(--secondary)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{t.card2Title}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.card2Desc}</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <ShieldCheck size={22} color="var(--success)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{t.card3Title}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.card3Desc}</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <Globe size={22} color="var(--warning)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{t.card4Title}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t.card4Desc}</div>
            </div>
          </div>
        </div>

        {/* Auth Card */}
        <div className="glass-card" style={{ padding: '2.5rem' }}>
          <div
            style={{
              display: 'flex',
              gap: '0.5rem',
              marginBottom: '1.5rem',
              borderBottom: '1px solid var(--border-color)',
              paddingBottom: '1rem',
            }}
          >
            <button
              type="button"
              className={`btn ${mode === 'login' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, justifyContent: 'center' }}
              onClick={() => {
                setMode('login');
                setError('');
              }}
            >
              {t.signInTab}
            </button>
            <button
              type="button"
              className={`btn ${mode === 'register' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, justifyContent: 'center' }}
              onClick={() => {
                setMode('register');
                setError('');
              }}
            >
              {t.registerBusinessBtn}
            </button>
          </div>

          {error && (
            <div
              style={{
                padding: '0.75rem 1rem',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid var(--error)',
                borderRadius: '8px',
                color: 'var(--error)',
                marginBottom: '1.25rem',
                fontSize: '0.9rem',
              }}
            >
              {error}
            </div>
          )}

          {mode === 'login' ? (
            <form onSubmit={handleLogin}>
              <h2 style={{ marginBottom: '0.5rem' }}>{t.welcomeBack}</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                {t.signInSubtitle}
              </p>
              <div className="form-group">
                <label className="form-label">{t.emailLabel}</label>
                <input
                  type="email"
                  className="form-control"
                  required
                  placeholder="you@yourbusiness.az"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                <label className="form-label">{t.passwordLabel}</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
              >
                {submitting ? t.signingIn : t.signInSubmit}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <h2 style={{ marginBottom: '0.5rem' }}>{t.createAccountTitle}</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                {t.createAccountSubtitle}
              </p>
              <div className="form-group">
                <label className="form-label">{t.businessNameLabel}</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  placeholder={t.businessNamePlaceholder}
                  value={businessName}
                  onChange={(e) => setBusinessName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">{t.ownerNameLabel}</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder={t.ownerNamePlaceholder}
                  value={ownerName}
                  onChange={(e) => setOwnerName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">{t.ownerEmailLabel}</label>
                <input
                  type="email"
                  className="form-control"
                  required
                  placeholder="owner@yourbusiness.az"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">{t.phoneLabel}</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="+994 50 000 00 00"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">{t.passwordLabel}</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  minLength={6}
                  placeholder={t.passwordHint}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                <label className="form-label">{t.referralLabel}</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder={t.referralPlaceholder}
                  value={referralCode}
                  onChange={(e) => setReferralCode(e.target.value)}
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
              >
                {submitting ? t.creatingWorkspace : t.createAccountSubmit}
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Live Subscription Plans with ALL Platform Features */}
      {plans.length > 0 && (
        <section style={{ marginBottom: '3rem' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>{t.plansTitle}</h2>
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            {t.plansSubtitle}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
            {plans.map((p) => {
              const allFeatures = getPlanFeatureItems(p, lang);
              return (
                <div key={p.id} className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <h3 style={{ fontSize: '1.4rem', margin: 0 }}>{p.name}</h3>
                    {p.allows_free_trial !== false && (p.trial_days ?? 14) > 0 && (
                      <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                        {lang === 'en' ? `${p.trial_days ?? 14}-Day Free Trial` : `${p.trial_days ?? 14} Gün Pulsuz Sınaq`}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '2.1rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '1.25rem' }}>
                    {p.price} AZN
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: 400 }}>
                      {t.perMonth}
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem', marginBottom: '1.75rem', flex: 1 }}>
                    {allFeatures.map((item) => (
                      <div
                        key={item.key}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '0.55rem',
                          fontSize: '0.86rem',
                          opacity: item.included ? 1 : 0.45,
                        }}
                      >
                        {item.included ? (
                          <Check size={16} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
                        ) : (
                          <X size={16} color="var(--text-secondary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                        )}
                        <span>{item.label}</span>
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{ marginTop: 'auto', justifyContent: 'center', width: '100%' }}
                    onClick={() => {
                      setSelectedPlanId(p.id);
                      setMode('register');
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                  >
                    {t.selectPlanCta(p.name)}
                  </button>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
};

export default Login;
