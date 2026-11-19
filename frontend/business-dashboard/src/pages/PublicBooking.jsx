import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { BrandLogo } from '../components/common/BrandLogo';
import api from '../api/client';
import { Calendar, CheckCircle2, Clock, CreditCard } from 'lucide-react';

const PublicBooking = ({ customDomain = null }) => {
  const { businessId } = useParams();
  const [business, setBusiness] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [bookingResult, setBookingResult] = useState(null);
  const [form, setForm] = useState({
    service_id: '',
    staff_id: '',
    date: new Date().toISOString().slice(0, 10),
    time: '11:00',
    customer_name: '',
    customer_phone: '',
  });

  useEffect(() => {
    const query = businessId
      ? `business_id=${encodeURIComponent(businessId)}`
      : `domain=${encodeURIComponent(customDomain || window.location.hostname)}`;
    api
      .get(`/businesses/public/resolve?${query}`)
      .then((res) => {
        setBusiness(res.data);
        setForm((prev) => ({
          ...prev,
          service_id: res.data?.services?.[0]?.id || '',
          staff_id: res.data?.staff?.[0]?.id || '',
        }));
      })
      .catch(() => setError('Biznes randevu səhifəsi tapılmadı / Booking page not found.'))
      .finally(() => setLoading(false));
  }, [businessId, customDomain]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!business) return;
    setError('');
    setSubmitting(true);
    try {
      const res = await api.post(`/businesses/public/${business.id}/book`, form);
      if (res.data?.error) {
        setError(res.data.error);
      } else {
        setBookingResult(res.data.appointment);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Randevu yaradıla bilmədi.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Yüklənir...</p>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', maxWidth: '680px', margin: '0 auto', padding: '2rem 1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <BrandLogo size={34} fontSize="1.35rem" />
        <span className="badge badge-gold">Onlayn Randevu</span>
      </div>

      {error && !business ? (
        <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--error)' }}>
          {error}
        </div>
      ) : bookingResult ? (
        <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
          <CheckCircle2 size={44} color="var(--success)" style={{ marginBottom: '0.75rem' }} />
          <h2 style={{ marginBottom: '0.5rem' }}>
            {bookingResult.deposit_required
              ? 'Randevu Yaradıldı — Beh Ödənişi Gözlənilir'
              : 'Randevunuz Təsdiqləndi!'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            {bookingResult.service} • {bookingResult.staff} • {bookingResult.date} {bookingResult.time}
          </p>
          {bookingResult.deposit_required && (
            <div style={{ marginBottom: '1.25rem' }}>
              <p style={{ color: 'var(--gold)', fontWeight: 700, marginBottom: '0.75rem' }}>
                Beh məbləği: {Number(bookingResult.deposit_amount).toFixed(2)} AZN
              </p>
              {bookingResult.checkout_url && (
                <a
                  href={bookingResult.checkout_url}
                  className="btn btn-gold"
                  style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  <CreditCard size={18} />
                  Beh Ödənişini Tamamla
                </a>
              )}
            </div>
          )}
          <button type="button" className="btn btn-secondary" onClick={() => setBookingResult(null)}>
            Yeni Randevu Al
          </button>
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '2rem' }}>
          <h1 style={{ fontSize: '1.65rem', marginBottom: '0.35rem' }}>{business?.name}</h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Xidmət, mütəxəssis və vaxt seçərək birbaşa onlayn randevu alın.
          </p>

          {error && (
            <div style={{ padding: '0.75rem', borderRadius: '8px', background: 'rgba(239,68,68,0.14)', color: '#fca5a5', marginBottom: '1rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Xidmət</label>
              <select
                className="form-control"
                required
                value={form.service_id}
                onChange={(e) => setForm({ ...form, service_id: e.target.value })}
              >
                {(business?.services || []).map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} — {s.price} {s.currency} ({s.duration_minutes} dəq)
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Mütəxəssis</label>
              <select
                className="form-control"
                required
                value={form.staff_id}
                onChange={(e) => setForm({ ...form, staff_id: e.target.value })}
              >
                {(business?.staff || []).map((st) => (
                  <option key={st.id} value={st.id}>
                    {st.name} ({st.role})
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label"><Calendar size={14} /> Tarix</label>
                <input
                  type="date"
                  className="form-control"
                  required
                  value={form.date}
                  onChange={(e) => setForm({ ...form, date: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label"><Clock size={14} /> Saat</label>
                <input
                  type="time"
                  className="form-control"
                  required
                  value={form.time}
                  onChange={(e) => setForm({ ...form, time: e.target.value })}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Adınız və Soyadınız</label>
              <input
                type="text"
                className="form-control"
                required
                placeholder="məs: Aysel Məmmədova"
                value={form.customer_name}
                onChange={(e) => setForm({ ...form, customer_name: e.target.value })}
              />
            </div>

            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
              <label className="form-label">Telefon (WhatsApp)</label>
              <input
                type="tel"
                className="form-control"
                required
                placeholder="+994 50 000 00 00"
                value={form.customer_phone}
                onChange={(e) => setForm({ ...form, customer_phone: e.target.value })}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={submitting} style={{ width: '100%', justifyContent: 'center' }}>
              {submitting ? 'Göndərilir...' : 'Randevunu Təsdiqlə'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default PublicBooking;
