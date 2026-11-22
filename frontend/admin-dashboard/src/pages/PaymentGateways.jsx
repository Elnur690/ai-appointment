import React, { useEffect, useState } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import apiClient from '../api/client';
import { CreditCard, Banknote, ShieldCheck, CheckCircle2, XCircle, ExternalLink } from 'lucide-react';

const GATEWAY_ICONS = {
  cash: Banknote,
  suby: CreditCard,
  payriff: CreditCard,
  epoint: ShieldCheck,
  // Disabled: creem, paymegate
};

const PaymentGateways = () => {
  const { paymentGateways, fetchPaymentGateways, togglePaymentGateway } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [testAmount, setTestAmount] = useState('1.00');
  const [testCurrency, setTestCurrency] = useState('AZN');
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [testError, setTestError] = useState('');
  const [refundRules, setRefundRules] = useState({
    auto_refund_enabled: true,
    auto_refund_window_hours: 48,
    auto_refund_max_amount_azn: 100,
    require_reason: true,
    allow_business_self_cancel: true,
  });
  const [refundRulesMsg, setRefundRulesMsg] = useState('');
  const [refundRequests, setRefundRequests] = useState([]);
  const [supportWhatsapp, setSupportWhatsapp] = useState('');
  const [supportMsg, setSupportMsg] = useState('');

  const loadRefundData = async () => {
    const [rulesRes, listRes, supRes] = await Promise.all([
      apiClient.get('/saas-admin/refund-rules').catch(() => ({ data: null })),
      apiClient.get('/saas-admin/refunds').catch(() => ({ data: [] })),
      apiClient.get('/saas-admin/support-settings').catch(() => ({ data: null })),
    ]);
    if (rulesRes.data) setRefundRules(rulesRes.data);
    setRefundRequests(Array.isArray(listRes.data) ? listRes.data : []);
    if (supRes.data) setSupportWhatsapp(supRes.data.support_whatsapp_number || '');
  };

  const handleSaveSupportWhatsapp = async (e) => {
    e.preventDefault();
    setSupportMsg('');
    await apiClient.put('/saas-admin/support-settings', {
      support_whatsapp_number: supportWhatsapp,
    });
    setSupportMsg(
      isAz
        ? 'WhatsApp dəstək nömrəsi yadda saxlanıldı (Ana səhifədə aktivdir).'
        : 'WhatsApp support number saved (live on landing page).'
    );
    setTimeout(() => setSupportMsg(''), 3500);
  };

  useEffect(() => {
    fetchPaymentGateways();
    loadRefundData();
  }, [fetchPaymentGateways]);

  const handleSaveRefundRules = async (e) => {
    e.preventDefault();
    setRefundRulesMsg('');
    await apiClient.put('/saas-admin/refund-rules', refundRules);
    setRefundRulesMsg(isAz ? 'Geri ödəniş qaydaları yadda saxlanıldı.' : 'Refund rules saved.');
    setTimeout(() => setRefundRulesMsg(''), 3000);
  };

  const handleRefundDecision = async (id, action) => {
    await apiClient.post(`/saas-admin/refunds/${id}/${action}`, {});
    await loadRefundData();
  };

  const handleRunLiveTest = async (e) => {
    e.preventDefault();
    setTestError('');
    setTestResult(null);
    setTestLoading(true);
    try {
      const res = await apiClient.post('/saas-admin/payment-gateways/test', {
        amount: Number(testAmount),
        currency: testCurrency,
      });
      setTestResult(res.data);
    } catch (err) {
      setTestError(err.response?.data?.detail || err.message || 'Test checkout failed');
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1>{isAz ? 'Ödəniş Şlüzlərinin İdarə Edilməsi' : 'Payment Gateways Control'}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz
              ? 'Randevu.vip platformasındakı bütün bizneslər üçün ödəniş şlüzlərini (Nağd, Suby.fi, Payriff, EPoint) aktiv və ya deaktiv edin.'
              : 'Enable or disable payment gateways platform-wide across all businesses on Randevu.vip.'}
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
        {paymentGateways.map((gw, idx) => {
          const IconComponent = GATEWAY_ICONS[gw.provider] || CreditCard;
          const isEnabled = Boolean(gw.enabled);

          return (
            <div
              key={gw.provider}
              className="glass-card"
              style={{
                padding: '2rem',
                display: 'flex',
                flexDirection: 'column',
                border: isEnabled ? '1px solid rgba(16, 185, 129, 0.35)' : '1px solid var(--border-color)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div
                    style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: '10px',
                      background: isEnabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255,255,255,0.05)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <IconComponent size={24} color={isEnabled ? 'var(--success)' : 'var(--text-secondary)'} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary-start)', textTransform: 'uppercase' }}>
                      {isAz ? `Şlüz #${idx + 1}` : `Gateway #${idx + 1}`} • {gw.provider}
                    </div>
                    <h2 style={{ fontSize: '1.3rem', margin: '0.15rem 0 0' }}>{gw.name}</h2>
                  </div>
                </div>

                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    padding: '0.3rem 0.75rem',
                    borderRadius: '999px',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    background: isEnabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: isEnabled ? 'var(--success)' : 'var(--error)',
                  }}
                >
                  {isEnabled ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                  {isEnabled ? (isAz ? 'Aktiv' : 'Enabled') : isAz ? 'Deaktiv' : 'Disabled'}
                </span>
              </div>

              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, flex: 1, marginBottom: '1.5rem' }}>
                {gw.description}
              </p>

              <div
                style={{
                  paddingTop: '1rem',
                  borderTop: '1px solid var(--border-color)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {gw.requires_credentials
                    ? gw.env_configured
                      ? isAz
                        ? `.env konfiqurasiyası: Aktiv (${gw.env_hint})`
                        : `.env configured (${gw.env_hint})`
                      : isAz
                      ? `.env açarı təyin edilməyib (${gw.provider === 'suby' ? 'SUBY_API_KEY' : gw.provider === 'epoint' ? 'Biznes Paneli' : 'PAYRIFF_SECRET_KEY'})`
                      : `Set ${gw.provider === 'suby' ? 'SUBY_API_KEY' : gw.provider === 'epoint' ? 'Business Dashboard' : 'PAYRIFF_SECRET_KEY'} in .env`
                    : isAz
                    ? 'Daxili kassa / nağd ödəniş üsulu'
                    : 'Built-in Ledger Method'}
                </span>

                <button
                  type="button"
                  className={isEnabled ? 'btn btn-secondary' : 'btn btn-primary'}
                  onClick={() => togglePaymentGateway(gw.provider, !isEnabled)}
                  style={{ minWidth: '150px', justifyContent: 'center' }}
                >
                  {isEnabled
                    ? isAz
                      ? 'Şlüzü Söndür'
                      : 'Disable Gateway'
                    : isAz
                    ? 'Şlüzü Aktivləşdir'
                    : 'Enable Gateway'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Platform WhatsApp Support Number (Floating Button on Landing Page) */}
      <div className="glass-card" style={{ padding: '1.75rem', marginTop: '2rem', border: '1px solid rgba(16, 185, 129, 0.35)' }}>
        <h2 style={{ fontSize: '1.2rem', marginBottom: '0.35rem' }}>
          {isAz ? 'WhatsApp Dəstək Nömrəsi (Ana Səhifə)' : 'WhatsApp Support Number (Landing Page)'}
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1rem' }}>
          {isAz
            ? 'Burada daxil etdiyiniz nömrə randevu.vip ana səhifəsində üzən WhatsApp dəstək düyməsi kimi görünəcək.'
            : 'The number entered here appears as a floating WhatsApp chat button on the randevu.vip landing page.'}
        </p>
        <form onSubmit={handleSaveSupportWhatsapp} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <input
            type="tel"
            className="form-control"
            style={{ maxWidth: '300px' }}
            placeholder="+994501234567"
            value={supportWhatsapp}
            onChange={(e) => setSupportWhatsapp(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">
            {isAz ? 'Nömrəni Yadda Saxla' : 'Save Number'}
          </button>
          {supportMsg && <span style={{ color: 'var(--success)', fontSize: '0.86rem', fontWeight: 600 }}>{supportMsg}</span>}
        </form>
      </div>

      {/* Live Suby.fi Payment Test (with Live AZN -> USD Conversion) */}
      <div className="glass-card" style={{ padding: '1.75rem', marginTop: '2rem', border: '1px solid rgba(212, 175, 55, 0.35)' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.35rem' }}>
          {isAz ? 'Canlı Ödəniş Testi (Suby.fi USD / EUR)' : 'Live Payment Test (Suby.fi USD / EUR)'}
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
          {isAz
            ? 'İstənilən məbləğ daxil edib real Suby.fi ödəniş sessiyası yaradın. AZN daxil etdikdə canlı məzənnə ilə avtomatik USD-yə çevrilir.'
            : 'Enter any amount to generate a real Suby.fi checkout session. AZN amounts are automatically converted to USD using the live exchange rate.'}
        </p>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          Webhook URL:{' '}
          <code style={{ padding: '0.2rem 0.45rem', borderRadius: '6px', background: 'rgba(0,0,0,0.25)' }}>
            https://api.randevu.vip/api/v1/webhooks/payments/suby
          </code>
        </div>

        <form onSubmit={handleRunLiveTest} style={{ display: 'flex', gap: '0.85rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0, minWidth: '160px' }}>
            <label className="form-label">{isAz ? 'Məbləğ' : 'Amount'}</label>
            <input
              type="number"
              step="0.01"
              min="0.10"
              required
              className="form-control"
              value={testAmount}
              onChange={(e) => setTestAmount(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0, minWidth: '120px' }}>
            <label className="form-label">{isAz ? 'Valyuta' : 'Currency'}</label>
            <select className="form-control" value={testCurrency} onChange={(e) => setTestCurrency(e.target.value)}>
              <option value="AZN">AZN</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary" disabled={testLoading}>
            {testLoading
              ? isAz
                ? 'Yaradılır...'
                : 'Creating...'
              : isAz
              ? 'Real Test Ödənişi Yarat'
              : 'Create Live Test Payment'}
          </button>
        </form>

        {testError && (
          <div style={{ marginTop: '1rem', color: 'var(--error)', fontSize: '0.9rem' }}>
            {testError}
          </div>
        )}

        {testResult && (
          <div
            style={{
              marginTop: '1.25rem',
              padding: '1rem',
              borderRadius: '10px',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.35)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div>
              <div style={{ fontWeight: 700, color: 'var(--success)', marginBottom: '0.25rem' }}>
                {testResult.original_amount} {testResult.original_currency} ➔ ${testResult.usd_amount} USD (Rate: {testResult.fx_rate})
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                Order UUID: {testResult.order_uuid}
              </div>
            </div>
            <a
              href={testResult.checkout_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.45rem' }}
            >
              <ExternalLink size={16} />
              {isAz ? 'Ödəniş Səhifəsini Aç' : 'Open Live Checkout'}
            </a>
          </div>
        )}
      </div>

      {/* Refund & Auto-Refund Rules */}
      <div className="glass-card" style={{ padding: '1.75rem', marginTop: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.35rem' }}>
          {isAz ? 'Geri Ödəniş (Refund) və Avto-Refund Qaydaları' : 'Refund & Auto-Refund Policy Rules'}
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
          {isAz
            ? 'Hansı geri ödəniş tələblərinin avtomatik təsdiqlənəcəyini və hansılarının Admin təsdiqinə düşəcəyini tənzimləyin.'
            : 'Control which refund requests qualify for instant auto-refund vs. manual SaaS Admin approval.'}
        </p>
        {refundRulesMsg && (
          <div style={{ color: 'var(--success)', marginBottom: '1rem', fontSize: '0.9rem' }}>{refundRulesMsg}</div>
        )}
        <form onSubmit={handleSaveRefundRules}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">
                {isAz ? 'Avto-Refund Müddəti (Saat)' : 'Auto-Refund Window (Hours)'}
              </label>
              <input
                type="number"
                min="0"
                max="720"
                className="form-control"
                value={refundRules.auto_refund_window_hours}
                onChange={(e) =>
                  setRefundRules({ ...refundRules, auto_refund_window_hours: Number(e.target.value) || 0 })
                }
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">
                {isAz ? 'Maksimum Avto-Refund (AZN)' : 'Max Auto-Refund Amount (AZN)'}
              </label>
              <input
                type="number"
                min="0"
                step="1"
                className="form-control"
                value={refundRules.auto_refund_max_amount_azn}
                onChange={(e) =>
                  setRefundRules({ ...refundRules, auto_refund_max_amount_azn: Number(e.target.value) || 0 })
                }
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={Boolean(refundRules.auto_refund_enabled)}
                onChange={(e) => setRefundRules({ ...refundRules, auto_refund_enabled: e.target.checked })}
              />
              <span>{isAz ? 'Avto-Refund Aktivdir' : 'Enable Auto-Refund'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={Boolean(refundRules.require_reason)}
                onChange={(e) => setRefundRules({ ...refundRules, require_reason: e.target.checked })}
              />
              <span>{isAz ? 'Səbəb Tələb Olunsun' : 'Require Reason'}</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={Boolean(refundRules.allow_business_self_cancel)}
                onChange={(e) => setRefundRules({ ...refundRules, allow_business_self_cancel: e.target.checked })}
              />
              <span>{isAz ? 'Biznes Öz Hesabını Ləğv Edə Bilsin' : 'Allow Self-Service Account Cancellation'}</span>
            </label>
          </div>
          <button type="submit" className="btn btn-primary">
            {isAz ? 'Qaydaları Yadda Saxla' : 'Save Refund Rules'}
          </button>
        </form>
      </div>

      {/* Refund Requests Queue */}
      <div className="glass-card" style={{ padding: '1.75rem', marginTop: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>
          {isAz ? 'Geri Ödəniş Tələbləri (Approve / Reject)' : 'Refund Requests Queue'}
        </h2>
        {refundRequests.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
            {isAz ? 'Hələ geri ödəniş tələbi yoxdur.' : 'No refund requests submitted yet.'}
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {refundRequests.map((rr) => (
              <div
                key={rr.id}
                style={{
                  padding: '1rem',
                  borderRadius: '10px',
                  border: '1px solid var(--border-color)',
                  background: 'rgba(255,255,255,0.02)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '1rem',
                }}
              >
                <div>
                  <div style={{ fontWeight: 700 }}>
                    {rr.business_name} • {Number(rr.amount).toFixed(2)} {rr.currency}
                  </div>
                  <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                    Status: <strong>{rr.status}</strong> {rr.reason ? `• ${rr.reason}` : ''}
                  </div>
                </div>
                {rr.status === 'pending' && (
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={() => handleRefundDecision(rr.id, 'approve')}
                    >
                      {isAz ? 'Təsdiqlə (Refund)' : 'Approve'}
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ color: 'var(--error)' }}
                      onClick={() => handleRefundDecision(rr.id, 'reject')}
                    >
                      {isAz ? 'Rədd Et' : 'Reject'}
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentGateways;
