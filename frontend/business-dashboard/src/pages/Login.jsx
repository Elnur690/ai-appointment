import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Sparkles, MessageSquare, Calendar, ShieldCheck, Globe, Check } from 'lucide-react';

const Login = ({ initialMode = 'login' }) => {
  const [searchParams] = useSearchParams();
  const refParam = searchParams.get('ref') || '';
  const [mode, setMode] = useState(refParam ? 'register' : initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [phone, setPhone] = useState('');
  const [referralCode, setReferralCode] = useState(refParam);
  const [plans, setPlans] = useState([]);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { login, fetchBusinessProfile } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get('/auth/plans')
      .then((res) => setPlans(res.data || []))
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
      setError(err.response?.data?.detail || 'Invalid email or password.');
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
        email,
        password,
        phone: phone || null,
        referral_code: referralCode || null,
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
      setError(err.response?.data?.detail || 'Registration failed. Please check your details.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', padding: '2rem 1.5rem', maxWidth: '1240px', margin: '0 auto' }}>
      {/* Top Navbar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Sparkles size={28} color="var(--primary)" />
          <span className="text-gradient" style={{ fontSize: '1.6rem', fontWeight: 700 }}>Randevu.vip</span>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            type="button"
            className={`btn ${mode === 'login' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setMode('login'); setError(''); }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`btn ${mode === 'register' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setMode('register'); setError(''); }}
          >
            Start Free Trial / Register
          </button>
        </div>
      </header>

      {/* Main Split Grid: Value Proposition + Auth Form */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '3rem', alignItems: 'start', marginBottom: '4rem' }}>
        <div>
          <span className="badge badge-info" style={{ marginBottom: '1rem', display: 'inline-block' }}>
            24/7 AI Receptionist for Salons, Clinics & Studios
          </span>
          <h1 style={{ fontSize: '2.5rem', lineHeight: 1.2, marginBottom: '1.25rem' }}>
            Automate Every Booking on WhatsApp, Instagram & Web
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: 1.6, marginBottom: '2rem' }}>
            Randevu.vip turns your WhatsApp and Instagram DMs into an intelligent booking engine in Azerbaijani, Russian, Turkish, and English — with shift-aware scheduling, Payriff/EPoint deposits, and white-label custom domains.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <MessageSquare size={22} color="var(--primary)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>WhatsApp & IG AI</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Instant text & voice note replies with human takeover anytime.</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <Calendar size={22} color="var(--secondary)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Zero Double-Bookings</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Real-time staff availability, buffers, and 24h/2h reminders.</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <ShieldCheck size={22} color="var(--success)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>No-Show Protection</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Automated Payriff & EPoint deposit links for high-risk slots.</div>
            </div>
            <div className="glass-card" style={{ padding: '1rem' }}>
              <Globe size={22} color="var(--warning)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>White-Label Domain</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Connect your own domain via CNAME to cname.randevu.vip.</div>
            </div>
          </div>
        </div>

        {/* Auth Card */}
        <div className="glass-card" style={{ padding: '2.5rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <button
              type="button"
              className={`btn ${mode === 'login' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, justifyContent: 'center' }}
              onClick={() => { setMode('login'); setError(''); }}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`btn ${mode === 'register' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, justifyContent: 'center' }}
              onClick={() => { setMode('register'); setError(''); }}
            >
              Register Business
            </button>
          </div>

          {error && (
            <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid var(--error)', borderRadius: '8px', color: 'var(--error)', marginBottom: '1.25rem', fontSize: '0.9rem' }}>
              {error}
            </div>
          )}

          {mode === 'login' ? (
            <form onSubmit={handleLogin}>
              <h2 style={{ marginBottom: '0.5rem' }}>Welcome Back</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                Sign in to manage your appointments, staff, and AI assistant.
              </p>
              <div className="form-group">
                <label className="form-label">Email Address</label>
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
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <button type="submit" disabled={submitting} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                {submitting ? 'Signing in...' : 'Sign In to Workspace'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <h2 style={{ marginBottom: '0.5rem' }}>Create Your Business Account</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                Launch your AI booking workspace in under 60 seconds.
              </p>
              <div className="form-group">
                <label className="form-label">Business / Salon / Clinic Name</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  placeholder="e.g. Bella Aesthetics Baku"
                  value={businessName}
                  onChange={(e) => setBusinessName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Owner Email Address</label>
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
                <label className="form-label">WhatsApp / Phone Number</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="+994 50 000 00 00"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  minLength={6}
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                <label className="form-label">Partner / Reseller Code (Optional)</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Optional referral code"
                  value={referralCode}
                  onChange={(e) => setReferralCode(e.target.value)}
                />
              </div>
              <button type="submit" disabled={submitting} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                {submitting ? 'Creating Workspace...' : 'Create Business Account'}
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Live Subscription Plans from PostgreSQL */}
      {plans.length > 0 && (
        <section style={{ marginBottom: '3rem' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>Transparent Subscription Plans</h2>
          <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            Every new business starts on the Starter tier and can upgrade anytime.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
            {plans.map((p) => (
              <div key={p.id} className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ fontSize: '1.35rem', marginBottom: '0.5rem' }}>{p.name}</h3>
                <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '1rem' }}>
                  {p.price} AZN<span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: 400 }}>/month</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>{p.message_limit >= 100000 ? 'Unlimited AI messages' : `${Number(p.message_limit).toLocaleString()} AI messages/mo`}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>WhatsApp, Instagram & Web Booking</span>
                </div>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ marginTop: 'auto', justifyContent: 'center' }}
                  onClick={() => { setMode('register'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                >
                  Get Started with {p.name}
                </button>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default Login;
