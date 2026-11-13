import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Bot, CreditCard, Globe, QrCode, CheckCircle2, RefreshCw, X, Save } from 'lucide-react';

const Settings = () => {
  const { fetchBusinessProfile } = useAuthStore();
  const [businessName, setBusinessName] = useState('');
  const [customDomain, setCustomDomain] = useState('');
  const [domainVerifyResult, setDomainVerifyResult] = useState(null);
  const [showQrModal, setShowQrModal] = useState(false);
  const [isQrLoading, setIsQrLoading] = useState(false);
  const [whatsappState, setWhatsappState] = useState({ status: 'not_checked', qr_code_data_url: null, instance_name: '' });
  const [saveMessage, setSaveMessage] = useState('');

  const [aiTone, setAiTone] = useState({
    language: 'az',
    tone: 'professional',
    custom_instructions: '',
    payriff_merchant_id: '',
    epoint_public_key: '',
  });

  useEffect(() => {
    api
      .get('/businesses/')
      .then((res) => {
        const b = res.data;
        setBusinessName(b.name || '');
        setCustomDomain(b.custom_domain || '');
        const s = b.settings || {};
        setAiTone({
          language: s.language || 'az',
          tone: s.tone || 'professional',
          custom_instructions: s.custom_instructions || '',
          payriff_merchant_id: s.payriff_merchant_id || '',
          epoint_public_key: s.epoint_public_key || '',
        });
      })
      .catch(() => {});
  }, []);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSaveMessage('');
    await api.put('/businesses/', {
      name: businessName,
      custom_domain: customDomain || null,
      settings: aiTone,
    });
    await fetchBusinessProfile();
    setSaveMessage('Settings saved successfully.');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const handleVerifyDomain = async () => {
    if (!customDomain) return;
    try {
      const res = await api.post('/businesses/custom-domain/verify', { custom_domain: customDomain });
      setDomainVerifyResult(res.data);
      await fetchBusinessProfile();
    } catch (err) {
      setDomainVerifyResult({ error: err.response?.data?.detail || 'Verification failed' });
    }
  };

  const handleGenerateQr = async () => {
    setIsQrLoading(true);
    setShowQrModal(true);
    try {
      const res = await api.get('/businesses/whatsapp/qr-code');
      setWhatsappState(res.data || { status: 'unavailable', qr_code_data_url: null });
    } catch (err) {
      setWhatsappState({ status: 'unavailable', detail: err.message, qr_code_data_url: null });
    } finally {
      setIsQrLoading(false);
    }
  };

  return (
    <div style={{ padding: '1rem 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>Business Settings & Integrations</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Configure your business profile, AI receptionist language, payment gateway keys, custom domain, and WhatsApp line.
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={handleSaveSettings}>
          <Save size={16} />
          Save All Changes
        </button>
      </div>

      {saveMessage && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid var(--success)', borderRadius: '8px', color: 'var(--success)', marginBottom: '1.5rem' }}>
          {saveMessage}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '1.5rem' }}>
        {/* 1. Business Profile & AI Language */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Bot color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>Business Profile & AI Receptionist</h2>
          </div>

          <div className="form-group">
            <label className="form-label">Business Name</label>
            <input
              type="text"
              className="form-control"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Default AI Language</label>
            <select
              className="form-control"
              value={aiTone.language}
              onChange={(e) => setAiTone({ ...aiTone, language: e.target.value })}
            >
              <option value="az">Azerbaijani (Azərbaycan dili)</option>
              <option value="en">English</option>
              <option value="ru">Russian (Русский)</option>
              <option value="tr">Turkish (Türkçe)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Custom AI Instructions / Greeting</label>
            <textarea
              className="form-control"
              rows={3}
              placeholder="Optional instructions for how the AI should greet and assist customers..."
              value={aiTone.custom_instructions}
              onChange={(e) => setAiTone({ ...aiTone, custom_instructions: e.target.value })}
            />
          </div>
        </div>

        {/* 2. White-Label Custom Domain */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Globe color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>White-Label Custom Domain</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Point your custom domain or subdomain via CNAME to <code>cname.randevu.vip</code>.
          </p>

          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Custom Domain</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="form-control"
                value={customDomain}
                onChange={(e) => setCustomDomain(e.target.value)}
                placeholder="booking.yourdomain.az"
              />
              <button type="button" className="btn btn-secondary" onClick={handleVerifyDomain}>
                Verify DNS
              </button>
            </div>
          </div>

          {domainVerifyResult && (
            <div style={{ fontSize: '0.85rem', color: domainVerifyResult.cname_verified ? 'var(--success)' : 'var(--warning)' }}>
              {domainVerifyResult.error ||
                (domainVerifyResult.cname_verified
                  ? `Verified CNAME -> ${domainVerifyResult.expected_target}`
                  : `Pending DNS CNAME -> ${domainVerifyResult.expected_target || 'cname.randevu.vip'}`)}
            </div>
          )}
        </div>

        {/* 3. Payment Gateways */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <CreditCard color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>Payment Gateway Credentials</h2>
          </div>

          <div className="form-group">
            <label className="form-label">Payriff Merchant ID</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter your Payriff Merchant ID"
              value={aiTone.payriff_merchant_id}
              onChange={(e) => setAiTone({ ...aiTone, payriff_merchant_id: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">EPoint Public Key</label>
            <input
              type="text"
              className="form-control"
              placeholder="Enter your EPoint Public Key"
              value={aiTone.epoint_public_key}
              onChange={(e) => setAiTone({ ...aiTone, epoint_public_key: e.target.value })}
            />
          </div>
        </div>

        {/* 4. WhatsApp Instance QR Code */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <QrCode color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>WhatsApp Business Line</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
            Link your business WhatsApp number directly to your AI receptionist by scanning the Evolution API QR code.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleGenerateQr}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <QrCode size={18} />
            <span>Check Status / Generate WhatsApp QR Code</span>
          </button>
        </div>
      </div>

      {/* WhatsApp QR Modal */}
      {showQrModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.85)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}
        >
          <div className="glass-card" style={{ padding: '2rem', maxWidth: '420px', width: '100%', textAlign: 'center', position: 'relative' }}>
            <button
              type="button"
              onClick={() => setShowQrModal(false)}
              style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: '#fff', cursor: 'pointer' }}
            >
              <X size={24} />
            </button>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>WhatsApp Connection</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Open WhatsApp on your phone ➔ Linked Devices ➔ Link a Device.
            </p>

            {isQrLoading ? (
              <div style={{ padding: '2.5rem 0' }}>
                <RefreshCw size={32} color="var(--primary)" style={{ marginBottom: '1rem' }} />
                <p>Connecting to Evolution API...</p>
              </div>
            ) : whatsappState.status === 'connected' ? (
              <div style={{ padding: '2rem 0', color: 'var(--success)' }}>
                <CheckCircle2 size={42} style={{ marginBottom: '0.75rem' }} />
                <div style={{ fontWeight: 600 }}>WhatsApp Instance Connected</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Instance: {whatsappState.instance_name}
                </div>
              </div>
            ) : whatsappState.qr_code_data_url ? (
              <div>
                <img
                  src={whatsappState.qr_code_data_url}
                  alt="WhatsApp Pairing QR Code"
                  style={{ width: '240px', height: '240px', borderRadius: '12px', padding: '0.75rem', background: '#fff', marginBottom: '1rem' }}
                />
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Scan with WhatsApp to pair ({whatsappState.instance_name})
                </div>
              </div>
            ) : (
              <div style={{ padding: '1.5rem 0', color: 'var(--warning)' }}>
                <p style={{ margin: 0 }}>
                  Evolution API status: <strong>{whatsappState.status}</strong>
                </p>
                {whatsappState.detail && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                    {whatsappState.detail}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;