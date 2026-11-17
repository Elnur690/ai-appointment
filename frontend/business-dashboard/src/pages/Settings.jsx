import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import {
  Bot,
  CreditCard,
  Globe,
  QrCode,
  Instagram,
  Send,
  CheckCircle2,
  RefreshCw,
  X,
  Save,
  Lock,
} from 'lucide-react';

const Settings = () => {
  const { fetchBusinessProfile, language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [businessId, setBusinessId] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [planName, setPlanName] = useState('Starter');
  const [entitlements, setEntitlements] = useState({
    allows_whatsapp: true,
    allows_instagram: false,
    allows_telegram: false,
    allows_online_payments: true,
    allows_custom_domain: false,
  });
  const [webhookUrls, setWebhookUrls] = useState({
    whatsapp: 'https://api.randevu.vip/api/v1/webhooks/whatsapp',
    instagram: 'https://api.randevu.vip/api/v1/webhooks/instagram',
    telegram: 'https://api.randevu.vip/api/v1/webhooks/telegram',
  });
  const [platformGateways, setPlatformGateways] = useState([
    { provider: 'cash', name: 'Cash Payment', enabled: true },
    { provider: 'payriff', name: 'Payriff Payment Gateway', enabled: true },
    { provider: 'paymegate', name: 'Paymegate Payment Gateway', enabled: true },
  ]);

  const [customDomain, setCustomDomain] = useState('');
  const [domainVerifyResult, setDomainVerifyResult] = useState(null);
  const [showQrModal, setShowQrModal] = useState(false);
  const [isQrLoading, setIsQrLoading] = useState(false);
  const [whatsappState, setWhatsappState] = useState({
    status: 'not_checked',
    qr_code_data_url: null,
    instance_name: '',
  });
  const [saveMessage, setSaveMessage] = useState('');
  const [channelStatusMsg, setChannelStatusMsg] = useState('');

  const [aiTone, setAiTone] = useState({
    language: 'az',
    tone: 'professional',
    custom_instructions: '',
    payriff_merchant_id: '',
    payriff_secret_key: '',
    paymegate_api_key: '',
    paymegate_webhook_secret: '',
    instagram_page_id: '',
    instagram_access_token: '',
    instagram_verify_token: 'randevu_ig_verify',
    instagram_connected: false,
    telegram_bot_token: '',
    telegram_bot_username: '',
    telegram_connected: false,
  });

  useEffect(() => {
    api
      .get('/payments/gateways')
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setPlatformGateways(res.data);
        }
      })
      .catch(() => {});

    api
      .get('/businesses/')
      .then((res) => {
        const b = res.data;
        setBusinessId(b.id || '');
        setBusinessName(b.name || '');
        setPlanName(b.plan_name || 'Starter');
        if (b.entitlements) setEntitlements(b.entitlements);
        if (b.webhook_urls) setWebhookUrls(b.webhook_urls);
        setCustomDomain(b.custom_domain || '');
        const s = b.settings || {};
        setAiTone({
          language: s.language || 'az',
          tone: s.tone || 'professional',
          custom_instructions: s.custom_instructions || '',
          payriff_merchant_id: s.payriff_merchant_id || '',
          payriff_secret_key: s.payriff_secret_key || '',
          paymegate_api_key: s.paymegate_api_key || s.paymengate_api_key || '',
          paymegate_webhook_secret: s.paymegate_webhook_secret || s.paymengate_secret_key || '',
          instagram_page_id: s.instagram_page_id || '',
          instagram_access_token: s.instagram_access_token || '',
          instagram_verify_token: s.instagram_verify_token || 'randevu_ig_verify',
          instagram_connected: Boolean(s.instagram_connected),
          telegram_bot_token: s.telegram_bot_token || '',
          telegram_bot_username: s.telegram_bot_username || '',
          telegram_connected: Boolean(s.telegram_connected),
        });
      })
      .catch(() => {});
  }, []);

  const isGatewayEnabled = (provider) => {
    const found = platformGateways.find(
      (g) => g.provider === provider || (provider === 'paymegate' && g.provider === 'paymengate')
    );
    return found ? Boolean(found.enabled) : true;
  };

  const handleSaveSettings = async (e) => {
    if (e) e.preventDefault();
    setSaveMessage('');
    await api.put('/businesses/', {
      name: businessName,
      custom_domain: customDomain || null,
      settings: aiTone,
    });
    await fetchBusinessProfile();
    setSaveMessage(
      isAz
        ? 'Tənzimləmələr və ödəniş şlüzü məlumatları uğurla yadda saxlanıldı.'
        : 'Settings & payment gateway credentials saved successfully.'
    );
    setTimeout(() => setSaveMessage(''), 3500);
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

  const handleConnectInstagram = async () => {
    setChannelStatusMsg('');
    try {
      const res = await api.post('/businesses/instagram/connect', {
        instagram_page_id: aiTone.instagram_page_id,
        instagram_access_token: aiTone.instagram_access_token,
        instagram_verify_token: aiTone.instagram_verify_token,
      });
      setAiTone((prev) => ({ ...prev, instagram_connected: res.data?.status === 'connected' }));
      setChannelStatusMsg(
        isAz
          ? 'Instagram Direct məlumatları yadda saxlanıldı! Aşağıdakı Webhook URL-i Meta App Dashboard-a əlavə edin.'
          : 'Instagram Direct credentials saved! Configure the Webhook URL below in Meta App Dashboard.'
      );
    } catch (err) {
      setChannelStatusMsg(err.response?.data?.detail || 'Could not save Instagram credentials.');
    }
  };

  const handleConnectTelegram = async () => {
    setChannelStatusMsg('');
    try {
      const res = await api.post('/businesses/telegram/connect', {
        bot_token: aiTone.telegram_bot_token,
      });
      setAiTone((prev) => ({
        ...prev,
        telegram_connected: true,
        telegram_bot_username: res.data?.bot_username || prev.telegram_bot_username,
      }));
      setChannelStatusMsg(
        isAz
          ? `Telegram Bot @${res.data?.bot_username || 'bot'} qoşuldu və Webhook avtomatik qeydiyyatdan keçirildi!`
          : `Telegram Bot @${res.data?.bot_username || 'bot'} connected and webhook automatically registered!`
      );
    } catch (err) {
      setChannelStatusMsg(err.response?.data?.detail || 'Telegram Bot connection failed.');
    }
  };

  return (
    <div style={{ padding: '1rem 0' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
            {isAz
              ? 'Biznes Tənzimləmələri, Kanallar və Ödəniş Şlüzləri'
              : 'Business Settings, Channels & Payment Gateways'}
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz ? 'Aktiv Paket:' : 'Active Plan:'} <strong>{planName}</strong> •{' '}
            {isAz
              ? 'WhatsApp, Instagram Direct, Telegram Bot və Ödəniş Şlüzlərini (Nağd, Payriff, Paymegate) tənzimləyin.'
              : 'Configure WhatsApp, Instagram Direct, Telegram Bot, and Payment Gateways (Cash, Payriff, Paymegate).'}
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={handleSaveSettings}>
          <Save size={16} />
          {isAz ? 'Bütün Dəyişiklikləri Yadda Saxla' : 'Save All Changes'}
        </button>
      </div>

      {saveMessage && (
        <div
          style={{
            padding: '0.75rem 1rem',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid var(--success)',
            borderRadius: '8px',
            color: 'var(--success)',
            marginBottom: '1.5rem',
          }}
        >
          {saveMessage}
        </div>
      )}

      {channelStatusMsg && (
        <div
          style={{
            padding: '0.75rem 1rem',
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid var(--primary)',
            borderRadius: '8px',
            color: 'var(--text-primary)',
            marginBottom: '1.5rem',
          }}
        >
          {channelStatusMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '1.5rem' }}>
        {/* 1. Business Profile & AI Language */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Bot color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
              {isAz ? 'Biznes Profili və AI Resepşn' : 'Business Profile & AI Receptionist'}
            </h2>
          </div>

          <div className="form-group">
            <label className="form-label">{isAz ? 'Biznesin Adı' : 'Business Name'}</label>
            <input
              type="text"
              className="form-control"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">{isAz ? 'Əsas AI Ünsiyyət Dili' : 'Default AI Language'}</label>
            <select
              className="form-control"
              value={aiTone.language}
              onChange={(e) => setAiTone({ ...aiTone, language: e.target.value })}
            >
              <option value="az">Azərbaycan dili (Azerbaijani)</option>
              <option value="en">English</option>
              <option value="ru">Русский (Russian)</option>
              <option value="tr">Türkçe (Turkish)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              {isAz ? 'Xüsusi AI Təlimatları və Salamlama' : 'Custom AI Instructions / Greeting'}
            </label>
            <textarea
              className="form-control"
              rows={3}
              placeholder={
                isAz
                  ? 'AI köməkçinin müştəriləri necə qarşılaması və cavablandırması üçün əlavə təlimatlar...'
                  : 'Optional instructions for how the AI should greet and assist customers...'
              }
              value={aiTone.custom_instructions}
              onChange={(e) => setAiTone({ ...aiTone, custom_instructions: e.target.value })}
            />
          </div>
        </div>

        {/* 2. Payment Gateways (Cash, Payriff, Paymegate) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <CreditCard color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
              {isAz ? 'Ödəniş Şlüzləri (Payment Gateways)' : 'Payment Gateways'}
            </h2>
          </div>

          <div
            style={{
              padding: '0.6rem 0.85rem',
              borderRadius: '8px',
              background: isGatewayEnabled('cash') ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
              marginBottom: '1rem',
              fontSize: '0.88rem',
              display: 'flex',
              justifyContent: 'space-between',
            }}
          >
            <span>{isAz ? '1. Nağd Ödəniş (Salonda)' : '1. Cash Payment (At Venue)'}</span>
            <strong style={{ color: isGatewayEnabled('cash') ? 'var(--success)' : 'var(--error)' }}>
              {isGatewayEnabled('cash')
                ? isAz
                  ? 'Aktiv'
                  : 'Active'
                : isAz
                ? 'Admin tərəfindən deaktiv edilib'
                : 'Disabled by Admin'}
            </strong>
          </div>

          {isGatewayEnabled('payriff') ? (
            <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '0.5rem' }}>
                2. Payriff Payment Gateway
              </div>
              <div className="form-group" style={{ marginBottom: '0.6rem' }}>
                <label className="form-label">Payriff Merchant ID</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Payriff Merchant ID"
                  value={aiTone.payriff_merchant_id}
                  onChange={(e) => setAiTone({ ...aiTone, payriff_merchant_id: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Payriff Secret Key</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="Payriff Secret Key"
                  value={aiTone.payriff_secret_key}
                  onChange={(e) => setAiTone({ ...aiTone, payriff_secret_key: e.target.value })}
                />
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              {isAz
                ? '2. Payriff şlüzü hazırda Platforma Admini tərəfindən deaktiv edilib.'
                : '2. Payriff Gateway is currently disabled by Platform Admin.'}
            </div>
          )}

          {isGatewayEnabled('paymegate') ? (
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '0.35rem' }}>
                3. Paymegate Payment Gateway (paymegate.com)
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
                {isAz ? (
                  <>
                    Rəsmi <code>https://api.paymegate.com/v1/orders</code> üzərindən <code>X-API-Key</code> ilə işləyir və{' '}
                    <code>order.paid</code> webhook-unu avtomatik qeydiyyata alır.
                  </>
                ) : (
                  <>
                    Uses tenant-isolated <code>X-API-Key</code> authentication via{' '}
                    <code>https://api.paymegate.com/v1/orders</code> and auto-registers your <code>order.paid</code> webhook.
                  </>
                )}
              </p>
              <div className="form-group" style={{ marginBottom: '0.6rem' }}>
                <label className="form-label">Paymegate Merchant API Key (X-API-Key)</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="Paymegate X-API-Key"
                  value={aiTone.paymegate_api_key}
                  onChange={(e) => setAiTone({ ...aiTone, paymegate_api_key: e.target.value })}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">
                  {isAz ? 'Paymegate Webhook Secret (İstəyə bağlı)' : 'Paymegate Webhook Secret (Optional)'}
                </label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="HMAC webhook secret"
                  value={aiTone.paymegate_webhook_secret}
                  onChange={(e) => setAiTone({ ...aiTone, paymegate_webhook_secret: e.target.value })}
                />
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              {isAz
                ? '3. Paymegate şlüzü hazırda Platforma Admini tərəfindən deaktiv edilib.'
                : '3. Paymegate Gateway is currently disabled by Platform Admin.'}
            </div>
          )}
        </div>

        {/* 3. WhatsApp Onboarding (Default Package) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <QrCode color="var(--success)" size={24} />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                {isAz ? '1. WhatsApp Qoşulması' : '1. WhatsApp Onboarding'}
              </h2>
            </div>
            <span className="badge badge-success">{isAz ? 'Standart Paket' : 'Default Package'}</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            {isAz
              ? 'Bütün paketlərə daxildir. Biznes WhatsApp nömrənizi 1 QR skanla birbaşa AI resepşnə qoşun.'
              : 'Included in all plans. Pair your business WhatsApp number in 1 scan via our internal Evolution API engine.'}
          </p>
          <ol
            style={{
              color: 'var(--text-secondary)',
              fontSize: '0.85rem',
              paddingLeft: '1.2rem',
              marginBottom: '1.25rem',
              lineHeight: 1.6,
            }}
          >
            <li>{isAz ? 'Aşağıdakı düyməyə klikləyərək canlı QR kodu yaradın.' : 'Click the button below to generate your live pairing QR code.'}</li>
            <li>
              {isAz ? (
                <>
                  Telefonunuzda WhatsApp-ı açın ➔ <strong>Bağlı Cihazlar (Linked Devices)</strong> ➔{' '}
                  <strong>Cihaz Əlavə Et</strong>.
                </>
              ) : (
                <>
                  Open WhatsApp on your phone ➔ <strong>Linked Devices</strong> ➔ <strong>Link a Device</strong>.
                </>
              )}
            </li>
            <li>
              {isAz
                ? 'QR kodu skan edin — AI köməkçiniz dərhal mətn və səsli mesajlara cavab verməyə başlayacaq.'
                : 'Scan the QR code — your AI receptionist immediately starts answering texts & voice notes.'}
            </li>
          </ol>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleGenerateQr}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', justifyContent: 'center' }}
          >
            <QrCode size={18} />
            <span>
              {isAz ? 'Statusu Yoxla / WhatsApp QR Kodu Yarat' : 'Check Status / Generate WhatsApp QR Code'}
            </span>
          </button>
        </div>

        {/* 4. Instagram Direct Onboarding (Plan Gated) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Instagram color="var(--primary)" size={24} />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                {isAz ? '2. Instagram Direct Qoşulması' : '2. Instagram Direct Onboarding'}
              </h2>
            </div>
            <span className={entitlements.allows_instagram ? 'badge badge-success' : 'badge badge-warning'}>
              {entitlements.allows_instagram
                ? isAz
                  ? 'Paketdə Aktivdir'
                  : 'Enabled on Plan'
                : isAz
                ? 'Paketdə Deaktivdir'
                : 'Disabled on Plan'}
            </span>
          </div>

          {!entitlements.allows_instagram ? (
            <div
              style={{
                padding: '1rem',
                borderRadius: '8px',
                background: 'rgba(255,255,255,0.03)',
                color: 'var(--text-secondary)',
                fontSize: '0.9rem',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '0.5rem',
                  color: 'var(--warning)',
                  fontWeight: 600,
                }}
              >
                <Lock size={16} />{' '}
                {isAz
                  ? `Instagram Direct cari (${planName}) paketinizdə aktiv deyil.`
                  : `Instagram Direct is disabled on your current (${planName}) plan.`}
              </div>
              {isAz
                ? 'Pro/Enterprise paketinə keçin və ya Admin Panel ➔ Paketlər və Kanallar bölməsindən Instagram Direct-i aktivləşdirin.'
                : 'Upgrade to Pro/Enterprise or enable Instagram Direct in the Admin Dashboard ➔ Plans & Channels.'}
            </div>
          ) : (
            <>
              <div className="form-group">
                <label className="form-label">
                  {isAz ? 'Instagram Səhifə / Biznes Hesab ID' : 'Instagram Page / Business Account ID'}
                </label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. 17841405793187218"
                  value={aiTone.instagram_page_id}
                  onChange={(e) => setAiTone({ ...aiTone, instagram_page_id: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Meta Page Access Token</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="EAABsbCS1iHgBO..."
                  value={aiTone.instagram_access_token}
                  onChange={(e) => setAiTone({ ...aiTone, instagram_access_token: e.target.value })}
                />
              </div>
              <div
                style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                  marginBottom: '0.85rem',
                  wordBreak: 'break-all',
                }}
              >
                <div>
                  <strong>Meta Webhook URL:</strong> <code>{webhookUrls.instagram}</code>
                </div>
                <div>
                  <strong>Verify Token:</strong> <code>{aiTone.instagram_verify_token}</code>
                </div>
              </div>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleConnectInstagram}
                style={{ width: '100%', justifyContent: 'center' }}
              >
                <Instagram size={16} />
                {aiTone.instagram_connected
                  ? isAz
                    ? 'Instagram Direct Bağlantısını Yenilə'
                    : 'Update Instagram Direct Connection'
                  : isAz
                  ? 'Instagram Direct-i Qoş'
                  : 'Connect Instagram Direct'}
              </button>
            </>
          )}
        </div>

        {/* 5. Telegram Bot Onboarding (Plan Gated) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Send color="var(--secondary)" size={24} />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                {isAz ? '3. Telegram Bot Qoşulması' : '3. Telegram Bot Onboarding'}
              </h2>
            </div>
            <span className={entitlements.allows_telegram ? 'badge badge-success' : 'badge badge-warning'}>
              {entitlements.allows_telegram
                ? isAz
                  ? 'Paketdə Aktivdir'
                  : 'Enabled on Plan'
                : isAz
                ? 'Paketdə Deaktivdir'
                : 'Disabled on Plan'}
            </span>
          </div>

          {!entitlements.allows_telegram ? (
            <div
              style={{
                padding: '1rem',
                borderRadius: '8px',
                background: 'rgba(255,255,255,0.03)',
                color: 'var(--text-secondary)',
                fontSize: '0.9rem',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginBottom: '0.5rem',
                  color: 'var(--warning)',
                  fontWeight: 600,
                }}
              >
                <Lock size={16} />{' '}
                {isAz
                  ? `Telegram Bot cari (${planName}) paketinizdə aktiv deyil.`
                  : `Telegram Bot is disabled on your current (${planName}) plan.`}
              </div>
              {isAz
                ? 'Pro/Enterprise paketinə keçin və ya Admin Panel ➔ Paketlər və Kanallar bölməsindən Telegram Botu aktivləşdirin.'
                : 'Upgrade to Pro/Enterprise or enable Telegram Bot in the Admin Dashboard ➔ Plans & Channels.'}
            </div>
          ) : (
            <>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '0.75rem' }}>
                {isAz ? (
                  <>
                    Telegram-da <strong>@BotFather</strong> açın, <code>/newbot</code> göndərin və aldığınız HTTP API Tokeni aşağıya yapışdırın. Sistem Webhook-u avtomatik qeydiyyata alır.
                  </>
                ) : (
                  <>
                    Open <strong>@BotFather</strong> on Telegram, send <code>/newbot</code>, and paste the HTTP API Token below. We automatically register the webhook for you.
                  </>
                )}
              </p>
              <div className="form-group">
                <label className="form-label">Telegram Bot Token (@BotFather)</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                  value={aiTone.telegram_bot_token}
                  onChange={(e) => setAiTone({ ...aiTone, telegram_bot_token: e.target.value })}
                />
              </div>
              {aiTone.telegram_bot_username && (
                <div style={{ fontSize: '0.85rem', color: 'var(--success)', marginBottom: '0.6rem' }}>
                  {isAz ? 'Qoşulmuş Bot:' : 'Connected Bot:'} <strong>@{aiTone.telegram_bot_username}</strong>
                </div>
              )}
              <div
                style={{
                  fontSize: '0.78rem',
                  color: 'var(--text-secondary)',
                  marginBottom: '0.85rem',
                  wordBreak: 'break-all',
                }}
              >
                <strong>Webhook:</strong>{' '}
                <code>{webhookUrls.telegram || `https://api.randevu.vip/api/v1/webhooks/telegram/${businessId}`}</code>
              </div>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleConnectTelegram}
                style={{ width: '100%', justifyContent: 'center' }}
              >
                <Send size={16} />
                {aiTone.telegram_connected
                  ? isAz
                    ? 'Telegram Webhook-u Yenilə'
                    : 'Reconnect & Refresh Telegram Webhook'
                  : isAz
                  ? 'Telegram Botu Qoş və Webhook-u Aktivləşdir'
                  : 'Connect & Register Telegram Webhook'}
              </button>
            </>
          )}
        </div>

        {/* 6. White-Label Custom Domain */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <Globe color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
              {isAz ? 'Şəxsi Domen (White-Label CNAME)' : 'White-Label Custom Domain'}
            </h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            {isAz ? (
              <>
                Şəxsi domeninizi və ya subdomeninizi DNS CNAME vasitəsilə <code>cname.randevu.vip</code> ünvanına yönləndirin.
              </>
            ) : (
              <>
                Point your custom domain or subdomain via CNAME to <code>cname.randevu.vip</code>.
              </>
            )}
          </p>

          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">{isAz ? 'Şəxsi Domen' : 'Custom Domain'}</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="form-control"
                value={customDomain}
                onChange={(e) => setCustomDomain(e.target.value)}
                placeholder="booking.yourdomain.az"
              />
              <button type="button" className="btn btn-secondary" onClick={handleVerifyDomain}>
                {isAz ? 'DNS Yoxla' : 'Verify DNS'}
              </button>
            </div>
          </div>

          {domainVerifyResult && (
            <div
              style={{
                fontSize: '0.85rem',
                color: domainVerifyResult.cname_verified ? 'var(--success)' : 'var(--warning)',
              }}
            >
              {domainVerifyResult.error ||
                (domainVerifyResult.cname_verified
                  ? `Verified CNAME -> ${domainVerifyResult.expected_target}`
                  : `Pending DNS CNAME -> ${domainVerifyResult.expected_target || 'cname.randevu.vip'}`)}
            </div>
          )}
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
          <div
            className="glass-card"
            style={{ padding: '2rem', maxWidth: '420px', width: '100%', textAlign: 'center', position: 'relative' }}
          >
            <button
              type="button"
              onClick={() => setShowQrModal(false)}
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                background: 'none',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
              }}
            >
              <X size={24} />
            </button>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
              {isAz ? 'WhatsApp Bağlantısı' : 'WhatsApp Connection'}
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              {isAz
                ? 'Telefonunuzda WhatsApp-ı açın ➔ Bağlı Cihazlar ➔ Cihaz Əlavə Et.'
                : 'Open WhatsApp on your phone ➔ Linked Devices ➔ Link a Device.'}
            </p>

            {isQrLoading ? (
              <div style={{ padding: '2.5rem 0' }}>
                <RefreshCw size={32} color="var(--primary)" style={{ marginBottom: '1rem' }} />
                <p>{isAz ? 'Evolution API ilə əlaqə qurulur...' : 'Connecting to Evolution API...'}</p>
              </div>
            ) : whatsappState.status === 'connected' ? (
              <div style={{ padding: '2rem 0', color: 'var(--success)' }}>
                <CheckCircle2 size={42} style={{ marginBottom: '0.75rem' }} />
                <div style={{ fontWeight: 600 }}>
                  {isAz ? 'WhatsApp Nömrəsi Qoşulub' : 'WhatsApp Instance Connected'}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Instance: {whatsappState.instance_name}
                </div>
              </div>
            ) : whatsappState.qr_code_data_url ? (
              <div>
                <img
                  src={whatsappState.qr_code_data_url}
                  alt="WhatsApp Pairing QR Code"
                  style={{
                    width: '240px',
                    height: '240px',
                    borderRadius: '12px',
                    padding: '0.75rem',
                    background: '#fff',
                    marginBottom: '1rem',
                  }}
                />
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {isAz
                    ? `WhatsApp ilə skan edin (${whatsappState.instance_name})`
                    : `Scan with WhatsApp to pair (${whatsappState.instance_name})`}
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
