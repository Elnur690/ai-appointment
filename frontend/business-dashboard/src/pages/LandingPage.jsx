import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import {
  Sparkles,
  MessageSquare,
  Calendar,
  ShieldCheck,
  Globe,
  Check,
  Mic,
  RefreshCw,
  Zap,
  Gift,
  BookOpen,
  Users,
  ArrowRight,
} from 'lucide-react';

const getAppOrigin = () => {
  if (typeof window === 'undefined') return 'https://app.randevu.vip';
  const { protocol, hostname } = window.location;
  if (hostname === 'randevu.vip' || hostname === 'www.randevu.vip') {
    return `${protocol}//app.randevu.vip`;
  }
  return window.location.origin;
};

const LandingPage = () => {
  const [searchParams] = useSearchParams();
  const refCode = searchParams.get('ref') || '';
  const [plans, setPlans] = useState([]);

  useEffect(() => {
    api
      .get('/auth/plans')
      .then((res) => setPlans(res.data || []))
      .catch(() => setPlans([]));
  }, []);

  const appOrigin = getAppOrigin();
  const loginUrl = `${appOrigin}/login${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;
  const registerUrl = `${appOrigin}/register${refCode ? `?ref=${encodeURIComponent(refCode)}` : ''}`;

  const features = [
    {
      icon: MessageSquare,
      color: 'var(--primary)',
      title: 'WhatsApp & Instagram AI Receptionist',
      desc: 'Replies 24/7 in Azerbaijani, Russian, Turkish, and English to check availability and book appointments automatically.',
    },
    {
      icon: Mic,
      color: 'var(--secondary)',
      title: 'Voice Note Understanding',
      desc: 'Customers can send WhatsApp voice messages naturally — the AI transcribes and books the exact requested slot.',
    },
    {
      icon: Calendar,
      color: 'var(--success)',
      title: 'Shift-Aware Staff Scheduling',
      desc: 'Supports Morning, Evening, and Full-Day shifts, buffer times, overtime rules, and instant human takeover.',
    },
    {
      icon: ShieldCheck,
      color: 'var(--warning)',
      title: 'No-Show Protection & Local Payments',
      desc: 'Collects automated online deposits via Payriff and EPoint for high-risk bookings and tracks full salon revenue.',
    },
    {
      icon: RefreshCw,
      color: 'var(--primary)',
      title: 'Predictive Cadence Rebooking',
      desc: 'Automatically reminds clients when their next haircut, manicure, or treatment cycle is due.',
    },
    {
      icon: Zap,
      color: 'var(--secondary)',
      title: 'Last-Minute Flash Drops & Waitlist',
      desc: 'Fills cancelled or empty slots automatically by notifying waitlisted clients with time-limited offers.',
    },
    {
      icon: Gift,
      color: 'var(--success)',
      title: 'Digital Gift Vouchers & VIP Loyalty',
      desc: 'Sell digital gift cards directly over WhatsApp and reward repeat customers with Silver & VIP Gold tiers.',
    },
    {
      icon: BookOpen,
      color: 'var(--warning)',
      title: 'RAG Knowledge Base ("Learn from Mistakes")',
      desc: 'Teach your AI your exact parking info, policies, and pricing corrections powered by PostgreSQL pgvector.',
    },
    {
      icon: Globe,
      color: 'var(--primary)',
      title: 'White-Label Custom Domains',
      desc: 'Connect your own domain via CNAME (cname.randevu.vip) for a fully branded booking experience.',
    },
  ];

  return (
    <div style={{ minHeight: '100vh', color: 'var(--text-primary)' }}>
      {/* Top Navigation */}
      <header
        style={{
          maxWidth: '1240px',
          margin: '0 auto',
          padding: '1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
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

        <nav style={{ display: 'flex', alignItems: 'center', gap: '1.75rem', flexWrap: 'wrap' }}>
          <a href="#features" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
            Features
          </a>
          <a href="#how-it-works" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
            How It Works
          </a>
          <a href="#pricing" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
            Plans & Pricing
          </a>
          <a href={loginUrl} className="btn btn-secondary" style={{ textDecoration: 'none' }}>
            Sign In
          </a>
          <a href={registerUrl} className="btn btn-primary" style={{ textDecoration: 'none' }}>
            Start Free Trial <ArrowRight size={16} />
          </a>
        </nav>
      </header>

      {/* Hero Section */}
      <section
        style={{
          maxWidth: '1100px',
          margin: '0 auto',
          padding: '4rem 1.5rem 3.5rem',
          textAlign: 'center',
        }}
      >
        <span className="badge badge-info" style={{ marginBottom: '1.25rem', display: 'inline-block', fontSize: '0.85rem' }}>
          AI Appointment & Revenue Platform for Salons, Clinics & Studios
        </span>
        <h1 style={{ fontSize: 'clamp(2.2rem, 5vw, 3.6rem)', lineHeight: 1.15, marginBottom: '1.5rem', fontWeight: 800 }}>
          Turn Your WhatsApp & Instagram Into a <span className="text-gradient">24/7 AI Receptionist</span>
        </h1>
        <p
          style={{
            color: 'var(--text-secondary)',
            fontSize: '1.15rem',
            lineHeight: 1.65,
            maxWidth: '760px',
            margin: '0 auto 2.5rem',
          }}
        >
          Stop losing clients to missed messages and double-bookings. Randevu.vip replies to texts and voice notes in seconds, books appointments into your live staff calendar, and sends automated 24h & 2h reminders.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <a
            href={registerUrl}
            className="btn btn-primary"
            style={{ padding: '0.9rem 1.75rem', fontSize: '1rem', textDecoration: 'none' }}
          >
            Launch Your Workspace on app.randevu.vip <ArrowRight size={18} />
          </a>
          <a
            href={loginUrl}
            className="btn btn-secondary"
            style={{ padding: '0.9rem 1.75rem', fontSize: '1rem', textDecoration: 'none' }}
          >
            Sign In to Existing Account
          </a>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" style={{ maxWidth: '1200px', margin: '0 auto', padding: '3rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>Go Live in 3 Simple Steps</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2.5rem' }}>
          Everything is managed from your dedicated workspace at <strong>app.randevu.vip</strong>.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          <div className="glass-card" style={{ padding: '2rem' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.5rem' }}>STEP 01</div>
            <h3 style={{ marginBottom: '0.75rem' }}>Create Your Business Account</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Register your salon, clinic, or studio and configure your services, durations, prices, and staff shifts.
            </p>
          </div>
          <div className="glass-card" style={{ padding: '2rem' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--secondary)', marginBottom: '0.5rem' }}>STEP 02</div>
            <h3 style={{ marginBottom: '0.75rem' }}>Scan the WhatsApp QR Code</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Pair your existing business WhatsApp number directly inside your dashboard settings in one scan.
            </p>
          </div>
          <div className="glass-card" style={{ padding: '2rem' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--success)', marginBottom: '0.5rem' }}>STEP 03</div>
            <h3 style={{ marginBottom: '0.75rem' }}>AI Books & Reminds Automatically</h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Your AI receptionist handles inquiries, schedules appointments, and lets you take over any chat with one click.
            </p>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section id="features" style={{ maxWidth: '1240px', margin: '0 auto', padding: '3rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>
          Built for Modern Service Businesses
        </h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2.5rem' }}>
          Complete booking automation, revenue protection, and client retention in one platform.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {features.map((f, idx) => (
            <div key={idx} className="glass-card" style={{ padding: '1.75rem' }}>
              <f.icon size={26} color={f.color} style={{ marginBottom: '1rem' }} />
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>{f.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6, margin: 0 }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Live Subscription Plans */}
      <section id="pricing" style={{ maxWidth: '1200px', margin: '0 auto', padding: '3.5rem 1.5rem' }}>
        <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>Transparent Subscription Plans</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '2.5rem' }}>
          Start on Starter and upgrade anytime as your team and booking volume grow.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {plans.map((p) => (
            <div key={p.id} className="glass-card" style={{ padding: '2.25rem', display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>{p.name}</h3>
              <div style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--primary)', marginBottom: '1.5rem' }}>
                {p.price} AZN
                <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', fontWeight: 400 }}>/month</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem', flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>
                    {p.message_limit >= 100000
                      ? 'Unlimited AI messages'
                      : `${Number(p.message_limit).toLocaleString()} AI messages / month`}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>Up to {p.max_branches || 1} branch(es)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <Check size={16} color="var(--success)" />
                  <span>WhatsApp, Instagram & Web Booking</span>
                </div>
                {p.allows_voice_messages && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <Check size={16} color="var(--success)" />
                    <span>WhatsApp Voice Note Booking</span>
                  </div>
                )}
                {p.allows_online_payments && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <Check size={16} color="var(--success)" />
                    <span>Payriff & EPoint Online Deposits</span>
                  </div>
                )}
                {p.allows_custom_domain && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <Check size={16} color="var(--success)" />
                    <span>White-Label Custom CNAME Domain</span>
                  </div>
                )}
              </div>

              <a
                href={registerUrl}
                className="btn btn-primary"
                style={{ justifyContent: 'center', textDecoration: 'none', width: '100%' }}
              >
                Get Started with {p.name}
              </a>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--border)',
          marginTop: '3rem',
          padding: '2.5rem 1.5rem',
          textAlign: 'center',
          color: 'var(--text-secondary)',
          fontSize: '0.9rem',
        }}
      >
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="var(--primary)" />
            <strong style={{ color: 'var(--text-primary)' }}>Randevu.vip</strong> — AI Appointment & Booking Platform
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <a href={loginUrl} style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
              Workspace Login (app.randevu.vip)
            </a>
            <a href={registerUrl} style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
              Register Business
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
