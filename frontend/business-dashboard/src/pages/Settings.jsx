import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Bot, CreditCard, Globe, QrCode, CheckCircle2, RefreshCw, X } from 'lucide-react';

const Settings = () => {
  const { language } = useAuthStore();
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [customDomain, setCustomDomain] = useState('booking.beautystudio.az');
  const [domainStatus, setDomainStatus] = useState('Verified & Active');
  const [showQrModal, setShowQrModal] = useState(false);
  const [isQrLoading, setIsQrLoading] = useState(false);
  const [qrCodeDataUrl, setQrCodeDataUrl] = useState('');

  const [aiTone, setAiTone] = useState({
    language: 'az',
    tone: 'professional',
    greeting_style: 'formal',
    custom_instructions: 'Alisiz və mehriban xidmət göstərin.'
  });
  const [gateways, setGateways] = useState({
    payriff_merchant_id: 'PRF_99841',
    epoint_public_key: 'EP_88291'
  });

  const handleGenerateQr = () => {
    setIsQrLoading(true);
    setShowQrModal(true);
    // Simulate backend calling unexposed evolution-api internally and returning base64 QR
    setTimeout(() => {
      setQrCodeDataUrl('https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=WHATSAPP_PAIR_SESSION_994501234567');
      setIsQrLoading(false);
    }, 800);
  };

  return (
    <div className="page-container" style={{ padding: '2rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Business Settings & Integration</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Configure AI Providers, Payment Gateways, Custom Domains, and WhatsApp Connection.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
        {/* 1. AI Engine Provider Assigned by Plan */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Bot color="var(--primary-start)" size={24} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>AI Provider Engine (Plan Assigned)</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            AI Model Engine is configured and assigned exclusively by the SaaS Owner based on your active subscription plan tier.
          </p>
          
          <div className="form-group" style={{ marginBottom: '1.25rem', padding: '0.85rem 1rem', background: 'rgba(255,255,255,0.04)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <label className="form-label" style={{ marginBottom: '0.25rem' }}>Assigned AI Model Engine</label>
            <p style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--primary-start)' }}>
              ⚡ Google Gemini 3.5 Flash (Assigned by Pro Plan)
            </p>
          </div>

          <div className="form-group">
            <label className="form-label">AI Conversation Language (Default: Azerbaijani)</label>
            <select className="form-control" value={aiTone.language} onChange={(e) => setAiTone({...aiTone, language: e.target.value})}>
              <option value="az">Azerbaijani (Azərbaycan dili)</option>
              <option value="en">English</option>
              <option value="ru">Russian (Русский)</option>
            </select>
          </div>
        </div>

        {/* 2. Custom Domain CNAME / A-Record */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Globe color="var(--primary-start)" size={24} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>White-Label Custom Domain</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>Connect your custom Apex domain (`beautystudio.az`) or subdomain (`booking.beautystudio.az`) for white-label customer portals.</p>

          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Custom Domain Name (Apex or Subdomain)</label>
            <input type="text" className="form-control" value={customDomain} onChange={(e) => setCustomDomain(e.target.value)} placeholder="beautystudio.az or booking.beautystudio.az" />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)' }}>
            <CheckCircle2 size={18} />
            <span>Target: app.ai-appointment.com ({domainStatus})</span>
          </div>
        </div>

        {/* 3. Payment Gateways */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <CreditCard color="var(--primary-start)" size={24} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>Azerbaijan Payment Gateways</h2>
          </div>
          
          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Payriff Merchant Secret Key</label>
            <input type="password" value="••••••••••••••••" className="form-control" readOnly />
          </div>

          <div className="form-group">
            <label className="form-label">EPoint Public Key</label>
            <input type="text" value={gateways.epoint_public_key} className="form-control" readOnly />
          </div>
        </div>

        {/* 4. WhatsApp Instance QR Code (Generated in-dashboard from internal Evolution API) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <QrCode color="var(--primary-start)" size={24} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>WhatsApp Pair via In-Dashboard QR</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Evolution API is 100% unexposed and secure inside internal backend network. Generate and scan your QR code right here.
          </p>
          <p style={{ color: 'var(--success)', fontWeight: 'bold', marginBottom: '1rem' }}>Status: CONNECTED (+994 50 123 45 67)</p>
          <button className="btn btn-primary" onClick={handleGenerateQr} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <QrCode size={18} />
            <span>Generate In-Dashboard WhatsApp QR Code</span>
          </button>
        </div>
      </div>

      {/* WhatsApp QR Modal */}
      {showQrModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999
        }}>
          <div className="glass-card" style={{ padding: '2rem', maxWidth: '420px', width: '100%', textAlign: 'center', position: 'relative' }}>
            <button onClick={() => setShowQrModal(false)} style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'none', border: 'none', color: '#fff', cursor: 'pointer' }}>
              <X size={24} />
            </button>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Pair WhatsApp Line</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Open WhatsApp on your phone ➔ Linked Devices ➔ Link a Device, and scan this QR code.
            </p>

            {isQrLoading ? (
              <div style={{ padding: '3rem 0' }}>
                <RefreshCw size={36} className="spin" color="var(--primary-start)" style={{ marginBottom: '1rem' }} />
                <p>Generating internal QR code via backend...</p>
              </div>
            ) : (
              <div>
                <img src={qrCodeDataUrl} alt="WhatsApp Pairing QR Code" style={{ width: '240px', height: '240px', borderRadius: '12px', padding: '1rem', background: '#fff', marginBottom: '1.5rem' }} />
                <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', color: 'var(--success)', fontSize: '0.9rem' }}>
                  <CheckCircle2 size={18} />
                  <span>Evolution API internal container connected securely</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;