import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Bot, CreditCard, Globe, QrCode, Sliders, CheckCircle2 } from 'lucide-react';

const Settings = () => {
  const { language } = useAuthStore();
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [customDomain, setCustomDomain] = useState('booking.beautystudio.az');
  const [domainStatus, setDomainStatus] = useState('Verified & Active');
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

  return (
    <div className="page-container" style={{ padding: '2rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Business Settings & Integration</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Configure AI Providers, Payment Gateways, Custom Domains, and WhatsApp Connection.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
        {/* 1. AI Engine Switcher */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Bot color="var(--primary-start)" size={24} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>AI Provider Engine Switcher</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>Choose active AI Model provider permitted by your subscription plan.</p>
          
          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Active Provider</label>
            <select className="form-control" value={selectedProvider} onChange={(e) => setSelectedProvider(e.target.value)}>
              <option value="gemini">Google Gemini 3.5 Flash (Included in Plan)</option>
              <option value="claude">Anthropic Claude 3.7 Sonnet (Pro/Enterprise Plan)</option>
              <option value="openai">OpenAI GPT-4o (Enterprise Plan)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">AI Language (Default: Azerbaijani)</label>
            <select className="form-control" value={aiTone.language} onChange={(e) => setAiTone({...aiTone, language: e.target.value})}>
              <option value="az">Azerbaijani (Süni İntellekt - Sİ)</option>
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

        {/* 4. WhatsApp Instance QR Code */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <QrCode color="var(--primary-start)" size={24} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>WhatsApp Instance Pairing</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>Status: <strong>CONNECTED</strong> (+994 50 123 45 67)</p>
          <button className="btn btn-secondary">Re-sync WhatsApp QR Code</button>
        </div>
      </div>
    </div>
  );
};

export default Settings;