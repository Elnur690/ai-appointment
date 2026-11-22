import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { BrandLogo } from '../components/common/BrandLogo';
import {
  ArrowLeft,
  Mail,
  MessageSquare,
  MapPin,
  Clock,
  Send,
  CheckCircle2,
  AlertTriangle,
  Sun,
  Moon,
} from 'lucide-react';

const ContactPage = () => {
  const [lang, setLang] = useState(() => {
    try {
      return localStorage.getItem('randevu_lang') === 'en' ? 'en' : 'az';
    } catch {
      return 'az';
    }
  });
  const isAz = lang !== 'en';

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

  const [supportWhatsapp, setSupportWhatsapp] = useState('');
  useEffect(() => {
    api
      .get('/auth/public-config')
      .then((res) => {
        if (res.data?.support_whatsapp_number) {
          setSupportWhatsapp(res.data.support_whatsapp_number);
        }
      })
      .catch(() => {});
  }, []);

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    subject: 'Sales & Onboarding',
    message: '',
    website_honeypot: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await api.post('/auth/contact', form);
      setSubmitted(true);
      setForm({
        name: '',
        email: '',
        phone: '',
        subject: 'Sales & Onboarding',
        message: '',
        website_honeypot: '',
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          (isAz
            ? 'Mesaj göndərilə bilmədi. Zəhmət olmasa yenidən cəhd edin.'
            : 'Could not send message. Please try again.')
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-main)', color: 'var(--text-primary)' }}>
      {/* Header */}
      <header className="landing-header">
        <div className="landing-header-inner">
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', textDecoration: 'none', color: 'inherit' }}>
            <BrandLogo size={32} fontSize="1.25rem" />
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <button
              type="button"
              onClick={() => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))}
              className="btn btn-secondary"
              style={{ width: '36px', height: '36px', padding: 0, minHeight: 'auto' }}
              title={theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            <div className="landing-lang-pill">
              <button
                type="button"
                onClick={() => setLang('az')}
                style={{
                  border: 'none',
                  cursor: 'pointer',
                  padding: '0.26rem 0.6rem',
                  borderRadius: '999px',
                  fontSize: '0.76rem',
                  fontWeight: 700,
                  background: isAz ? 'var(--primary)' : 'transparent',
                  color: isAz ? '#ffffff' : 'var(--text-secondary)',
                }}
              >
                AZ
              </button>
              <button
                type="button"
                onClick={() => setLang('en')}
                style={{
                  border: 'none',
                  cursor: 'pointer',
                  padding: '0.26rem 0.6rem',
                  borderRadius: '999px',
                  fontSize: '0.76rem',
                  fontWeight: 700,
                  background: !isAz ? 'var(--primary)' : 'transparent',
                  color: !isAz ? '#ffffff' : 'var(--text-secondary)',
                }}
              >
                EN
              </button>
            </div>

            <Link
              to="/"
              className="btn btn-secondary"
              style={{ textDecoration: 'none', height: '36px', padding: '0 0.85rem', fontSize: '0.84rem', minHeight: 'auto' }}
            >
              <ArrowLeft size={15} /> {isAz ? 'Ana Səhifə' : 'Home'}
            </Link>
          </div>
        </div>
      </header>

      <main style={{ maxWidth: '1080px', margin: '0 auto', padding: '3rem 1.5rem 4.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <span className="badge badge-gold" style={{ marginBottom: '0.75rem' }}>
            <Mail size={14} /> {isAz ? 'BİZİMLƏ ƏLAQƏ' : 'CONTACT US'}
          </span>
          <h1 style={{ fontSize: 'clamp(1.85rem, 4vw, 2.6rem)', fontWeight: 800, marginBottom: '0.6rem' }}>
            {isAz ? 'Suallarınız Var? Komandamız Yardıma Hazırdır' : 'Questions? Our Team Is Here to Help'}
          </h1>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '640px', margin: '0 auto', fontSize: '0.98rem' }}>
            {isAz
              ? 'Satış, WhatsApp quraşdırılması, abunəlik ödənişləri, geri ödənişlər və ya partnyorluq üçün bizimlə əlaqə saxlayın.'
              : 'Reach out for onboarding, WhatsApp AI setup, subscription billing, refund inquiries, or agency partnerships.'}
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 340px), 1fr))', gap: '1.75rem', alignItems: 'start' }}>
          {/* Left Column: Direct Contact Info */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
            <div className="glass-card" style={{ padding: '1.65rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
                <Mail size={20} color="var(--primary)" />
                <h2 style={{ fontSize: '1.08rem', margin: 0 }}>{isAz ? 'E-poçt Dəstəyi' : 'Email Support'}</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.65rem' }}>
                {isAz
                  ? 'Ümumi suallar, ödəniş və geri ödəniş müraciətləri üçün:'
                  : 'For support, billing, and refund inquiries:'}
              </p>
              <a
                href="mailto:support@randevu.vip"
                style={{ color: 'var(--primary)', fontWeight: 700, fontSize: '1rem', textDecoration: 'none' }}
              >
                support@randevu.vip
              </a>
            </div>

            {supportWhatsapp && (
              <div className="glass-card" style={{ padding: '1.65rem', border: '1px solid rgba(16, 185, 129, 0.35)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
                  <MessageSquare size={20} color="var(--success)" />
                  <h2 style={{ fontSize: '1.08rem', margin: 0 }}>{isAz ? 'WhatsApp Dəstək' : 'WhatsApp Support'}</h2>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.85rem' }}>
                  {isAz
                    ? 'Sürətli cavab və canlı demo üçün birbaşa WhatsApp-da yazın:'
                    : 'Chat directly on WhatsApp for quick answers or a live walkthrough:'}
                </p>
                <a
                  href={`https://wa.me/${supportWhatsapp.replace(/[^0-9]/g, '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ textDecoration: 'none', width: '100%', justifyContent: 'center' }}
                >
                  <MessageSquare size={16} /> {supportWhatsapp}
                </a>
              </div>
            )}

            <div className="glass-card" style={{ padding: '1.65rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.65rem' }}>
                <MapPin size={20} color="var(--primary)" />
                <h2 style={{ fontSize: '1.08rem', margin: 0 }}>{isAz ? 'Şirkət Məlumatları' : 'Company Information'}</h2>
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.65 }}>
                <strong>Randevu.vip</strong> — AI Appointment & CRM SaaS
                <br />
                {isAz ? 'Ünvan: Bakı, Azərbaycan' : 'Location: Baku, Azerbaijan'}
                <br />
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.35rem' }}>
                  <Clock size={14} />{' '}
                  {isAz ? 'İş saatları: Hər gün 09:00 – 21:00 (AZT / UTC+4)' : 'Hours: Daily 09:00 – 21:00 (AZT / UTC+4)'}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '0.85rem', flexWrap: 'wrap', marginTop: '1rem', fontSize: '0.82rem' }}>
                <Link to="/terms" style={{ color: 'var(--primary)', textDecoration: 'none' }}>
                  {isAz ? 'İstifadə Şərtləri' : 'Terms'}
                </Link>
                <Link to="/privacy" style={{ color: 'var(--primary)', textDecoration: 'none' }}>
                  {isAz ? 'Məxfilik' : 'Privacy'}
                </Link>
                <Link to="/refund-policy" style={{ color: 'var(--primary)', textDecoration: 'none' }}>
                  {isAz ? 'Geri Ödəniş' : 'Refund Policy'}
                </Link>
              </div>
            </div>
          </div>

          {/* Right Column: Contact Form */}
          <div className="glass-card" style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.25rem' }}>
              {isAz ? 'Bizə Mesaj Göndərin' : 'Send Us a Message'}
            </h2>

            {submitted ? (
              <div
                style={{
                  padding: '1.5rem',
                  borderRadius: '12px',
                  background: 'rgba(16, 185, 129, 0.12)',
                  border: '1px solid var(--success)',
                  textAlign: 'center',
                }}
              >
                <CheckCircle2 size={34} color="var(--success)" style={{ marginBottom: '0.65rem' }} />
                <h3 style={{ marginBottom: '0.45rem', color: 'var(--success-text)' }}>
                  {isAz ? 'Mesajınız Göndərildi!' : 'Message Received!'}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.15rem' }}>
                  {isAz
                    ? 'Təşəkkür edirik. Komandamız ən qısa zamanda sizinlə əlaqə saxlayacaq.'
                    : 'Thank you for reaching out. Our team will reply shortly.'}
                </p>
                <button type="button" className="btn btn-secondary" onClick={() => setSubmitted(false)}>
                  {isAz ? 'Yeni Mesaj Yaz' : 'Send Another Message'}
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <div className="visually-hidden" aria-hidden="true">
                  <input
                    type="text"
                    tabIndex={-1}
                    autoComplete="off"
                    value={form.website_honeypot}
                    onChange={(e) => setForm({ ...form, website_honeypot: e.target.value })}
                  />
                </div>

                {error && (
                  <div
                    role="alert"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      background: 'rgba(239, 68, 68, 0.14)',
                      border: '1px solid var(--danger)',
                      color: 'var(--danger-text)',
                      marginBottom: '1rem',
                      fontSize: '0.88rem',
                    }}
                  >
                    <AlertTriangle size={16} />
                    <span>{error}</span>
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label">{isAz ? 'Ad və Soyad *' : 'Full Name *'}</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder={isAz ? 'Adınız' : 'Your name'}
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">{isAz ? 'E-poçt Ünvanı *' : 'Email Address *'}</label>
                  <input
                    type="email"
                    required
                    className="form-control"
                    placeholder="name@company.com"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">{isAz ? 'Telefon / WhatsApp (istəyə bağlı)' : 'Phone / WhatsApp (optional)'}</label>
                  <input
                    type="tel"
                    className="form-control"
                    placeholder="+994 50 000 00 00"
                    value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">{isAz ? 'Mövzu' : 'Subject'}</label>
                  <select
                    className="form-control"
                    value={form.subject}
                    onChange={(e) => setForm({ ...form, subject: e.target.value })}
                  >
                    <option value="Sales & Onboarding">{isAz ? 'Satış və Quraşdırma' : 'Sales & Onboarding'}</option>
                    <option value="Billing & Refunds">{isAz ? 'Ödəniş və Geri Ödəniş' : 'Billing & Refunds'}</option>
                    <option value="Technical Support">{isAz ? 'Texniki Dəstək' : 'Technical Support'}</option>
                    <option value="Partner / Reseller">{isAz ? 'Partnyorluq (Reseller)' : 'Partner / Reseller'}</option>
                  </select>
                </div>

                <div className="form-group" style={{ marginBottom: '1.35rem' }}>
                  <label className="form-label">{isAz ? 'Mesajınız *' : 'Message *'}</label>
                  <textarea
                    required
                    rows={4}
                    className="form-control"
                    placeholder={isAz ? 'Sualınızı və ya biznesiniz barədə qısa məlumat yazın...' : 'Tell us how we can help...'}
                    value={form.message}
                    onChange={(e) => setForm({ ...form, message: e.target.value })}
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  <Send size={16} />
                  {submitting
                    ? isAz ? 'Göndərilir...' : 'Sending...'
                    : isAz ? 'Mesajı Göndər' : 'Send Message'}
                </button>
              </form>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ContactPage;
