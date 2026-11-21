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
  const { fetchBusinessProfile, logout, language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [cancelReason, setCancelReason] = useState('');
  const [cancelWithRefund, setCancelWithRefund] = useState(false);
  const [cancelConfirmOpen, setCancelConfirmOpen] = useState(false);
  const [businessId, setBusinessId] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [planName, setPlanName] = useState('Starter');
  const [entitlements, setEntitlements] = useState({
    allows_whatsapp: true,
    allows_instagram: false,
    allows_telegram: false,
    allows_online_payments: true,
    allowed_payment_providers: ['cash', 'payriff', 'epoint'],
    allows_no_show_deposits: false,
    allows_custom_domain: false,
  });
  const [services, setServices] = useState([]);
  const [webhookUrls, setWebhookUrls] = useState({
    whatsapp: 'https://api.randevu.vip/api/v1/webhooks/whatsapp',
    instagram: 'https://api.randevu.vip/api/v1/webhooks/instagram',
    telegram: 'https://api.randevu.vip/api/v1/webhooks/telegram',
    payriff: '',
    epoint: '',
  });

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
  const [waGroups, setWaGroups] = useState([]);
  const [selectedGroupJid, setSelectedGroupJid] = useState('');
  const [manualGroupJid, setManualGroupJid] = useState('');

  const [aiTone, setAiTone] = useState({
    language: 'az',
    tone: 'professional',
    greeting_message: '',
    excluded_phone_numbers: '',
    custom_instructions: '',
    instagram_page_id: '',
    instagram_access_token: '',
    instagram_verify_token: 'randevu_ig_verify',
    instagram_connected: false,
    telegram_bot_token: '',
    telegram_bot_username: '',
    telegram_connected: false,
    deposit_rule_mode: 'high_risk_only',
    deposit_min_service_price: 50,
    deposit_service_ids: [],
    deposit_calc_type: 'percentage',
    deposit_percentage: 20,
    deposit_fixed_amount: 10,
    deposit_skip_regular_customers: true,
    deposit_regular_min_visits: 2,
    deposit_no_show_threshold: 2,
    payriff_merchant_id: '',
    payriff_secret_key: '',
    epoint_public_key: '',
    epoint_private_key: '',
  });

  useEffect(() => {
    api
      .get('/services/')
      .then((res) => {
        if (Array.isArray(res.data)) setServices(res.data);
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
          greeting_message: s.greeting_message || '',
          excluded_phone_numbers: s.excluded_phone_numbers || '',
          custom_instructions: s.custom_instructions || '',
          instagram_page_id: s.instagram_page_id || '',
          instagram_access_token: s.instagram_access_token || '',
          instagram_verify_token: s.instagram_verify_token || 'randevu_ig_verify',
          instagram_connected: Boolean(s.instagram_connected),
          telegram_bot_token: s.telegram_bot_token || '',
          telegram_bot_username: s.telegram_bot_username || '',
          telegram_connected: Boolean(s.telegram_connected),
          deposit_rule_mode: s.deposit_rule_mode || 'high_risk_only',
          deposit_min_service_price: s.deposit_min_service_price ?? 50,
          deposit_service_ids: Array.isArray(s.deposit_service_ids) ? s.deposit_service_ids : [],
          deposit_calc_type: s.deposit_calc_type || 'percentage',
          deposit_percentage: s.deposit_percentage ?? 20,
          deposit_fixed_amount: s.deposit_fixed_amount ?? 10,
          deposit_skip_regular_customers: s.deposit_skip_regular_customers !== false,
          deposit_regular_min_visits: s.deposit_regular_min_visits ?? 2,
          deposit_no_show_threshold: s.deposit_no_show_threshold ?? 2,
          payriff_merchant_id: s.payriff_merchant_id || '',
          payriff_secret_key: s.payriff_secret_key || '',
          epoint_public_key: s.epoint_public_key || '',
          epoint_private_key: s.epoint_private_key || '',
        });
      })
      .catch(() => {});

    api
      .get('/businesses/whatsapp/groups')
      .then((res) => {
        setWaGroups(Array.isArray(res.data?.groups) ? res.data.groups : []);
        if (res.data?.selected_group_jid) {
          setSelectedGroupJid(res.data.selected_group_jid);
          setManualGroupJid(res.data.selected_group_jid);
        }
      })
      .catch(() => {});
  }, []);

  const handleRefreshGroups = async () => {
    try {
      const res = await api.get('/businesses/whatsapp/groups');
      setWaGroups(Array.isArray(res.data?.groups) ? res.data.groups : []);
      if (res.data?.selected_group_jid) {
        setSelectedGroupJid(res.data.selected_group_jid);
      }
    } catch {
      setWaGroups([]);
    }
  };

  const handleSelectDedicatedGroup = async (jidToSave, groupName) => {
    if (!jidToSave) return;
    setChannelStatusMsg('');
    try {
      const res = await api.post('/businesses/whatsapp/groups/select', {
        group_jid: jidToSave,
        group_name: groupName || null,
      });
      setSelectedGroupJid(res.data.group_jid);
      setManualGroupJid(res.data.group_jid);
      setChannelStatusMsg(
        isAz
          ? `Xüsusi WhatsApp idarəetmə qrupu təyin edildi: ${res.data.group_name || res.data.group_jid}`
          : `Dedicated WhatsApp management group set: ${res.data.group_name || res.data.group_jid}`
      );
    } catch (err) {
      setChannelStatusMsg(err.response?.data?.detail || 'Could not set dedicated group.');
    }
  };

  const toggleDepositService = (svcId) => {
    setAiTone((prev) => {
      const current = prev.deposit_service_ids || [];
      const exists = current.includes(svcId);
      return {
        ...prev,
        deposit_service_ids: exists ? current.filter((id) => id !== svcId) : [...current, svcId],
      };
    });
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
        ? 'Biznes tənzimləmələri uğurla yadda saxlanıldı.'
        : 'Business settings saved successfully.'
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
              ? 'Biznes Tənzimləmələri, Kanallar və Ödəniş Üsulları'
              : 'Business Settings, Channels & Payment Methods'}
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz ? 'Aktiv Paket:' : 'Active Plan:'} <strong>{planName}</strong> •{' '}
            {isAz
              ? 'WhatsApp, Instagram Direct, Telegram Bot və Nağd / Onlayn Kart ödənişlərini tənzimləyin.'
              : 'Configure WhatsApp, Instagram Direct, Telegram Bot, and Cash / Online Card payments.'}
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
            background: 'rgba(212, 175, 55, 0.14)',
            border: '1px solid var(--primary)',
            borderRadius: '8px',
            color: 'var(--text-primary)',
            marginBottom: '1.5rem',
          }}
        >
          {channelStatusMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 380px), 1fr))', gap: '1.5rem' }}>
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
              {isAz ? 'Salamlama Mesajı (İlk Mesaj Üçün)' : 'Custom Greeting Message'}
            </label>
            <input
              type="text"
              className="form-control"
              placeholder={
                isAz
                  ? 'məs: Salam! Xoş gəlmisiniz, sizə necə kömək edə bilərəm?'
                  : 'e.g. Hello! Welcome to our studio, how can I help you today?'
              }
              value={aiTone.greeting_message}
              onChange={(e) => setAiTone({ ...aiTone, greeting_message: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              {isAz ? 'Xüsusi AI Təlimatları' : 'Custom AI Instructions'}
            </label>
            <textarea
              className="form-control"
              rows={3}
              placeholder={
                isAz
                  ? 'AI köməkçinin müştəriləri necə cavablandırması üçün əlavə təlimatlar...'
                  : 'Optional instructions for how the AI should assist customers...'
              }
              value={aiTone.custom_instructions}
              onChange={(e) => setAiTone({ ...aiTone, custom_instructions: e.target.value })}
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">
              {isAz
                ? 'AI Botun Cavab Verməyəcəyi Nömrələr (İstisnalar)'
                : 'Excluded Phone Numbers (AI Bot Will Not Reply)'}
            </label>
            <textarea
              className="form-control"
              rows={2}
              placeholder="+994501112233, +994559998877"
              value={aiTone.excluded_phone_numbers}
              onChange={(e) => setAiTone({ ...aiTone, excluded_phone_numbers: e.target.value })}
            />
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              {isAz
                ? 'Vergül və ya yeni sətirlə ayırın. Digər bütün nömrələrə AI bot cavab verəcək.'
                : 'Separate by comma or new line. All other numbers are handled by the AI bot.'}
            </div>
          </div>
        </div>

        {/* 2. Payment Methods (Direct Business Payouts: Cash, Payriff, EPoint) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <CreditCard color="var(--primary)" size={24} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
              {isAz ? 'Ödəniş Üsulları və Birbaşa Beh Qəbulu' : 'Payment Methods & Direct Deposits'}
            </h2>
          </div>

          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            {isAz
              ? 'Müştərilərin ödədiyi beh (depozit) və onlayn ödənişlər vasitəçisiz olaraq birbaşa sizin öz Payriff və ya EPoint hesabınıza köçürülür. Aşağıdakı açarlar şifrələnmiş şəkildə saxlanılır.'
              : 'Customer deposits ("Beh") and online payments go directly to your own Payriff or EPoint merchant account with no platform middleman. Credentials below are stored encrypted at rest.'}
          </p>

          {(entitlements.allowed_payment_providers || ['cash', 'payriff', 'epoint']).includes('cash') && (
            <div
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                background: 'rgba(16, 185, 129, 0.12)',
                marginBottom: '0.75rem',
                fontSize: '0.9rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span>{isAz ? 'Nağd Ödəniş (Yerində / Kassada)' : 'Cash Payment (On-Site / Register)'}</span>
              <strong style={{ color: 'var(--success)' }}>{isAz ? 'Aktiv' : 'Active'}</strong>
            </div>
          )}

          {(entitlements.allowed_payment_providers || ['cash', 'payriff', 'epoint']).includes('payriff') && (
            <div
              style={{
                padding: '1rem',
                borderRadius: '10px',
                border: '1px solid var(--border)',
                background: 'rgba(255,255,255,0.02)',
                marginBottom: '0.85rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
                <strong style={{ fontSize: '0.95rem' }}>Payriff (AZN)</strong>
                <span style={{ fontSize: '0.78rem', color: aiTone.payriff_merchant_id ? 'var(--success)' : 'var(--text-secondary)' }}>
                  {aiTone.payriff_merchant_id
                    ? isAz ? 'Qoşulub' : 'Configured'
                    : isAz ? 'Məlumat tələb olunur' : 'Not configured'}
                </span>
              </div>

              <div className="form-group" style={{ marginBottom: '0.6rem' }}>
                <label className="form-label" style={{ fontSize: '0.82rem' }}>Payriff Merchant ID</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="ES1234567"
                  value={aiTone.payriff_merchant_id}
                  onChange={(e) => setAiTone({ ...aiTone, payriff_merchant_id: e.target.value })}
                />
              </div>

              <div className="form-group" style={{ marginBottom: '0.65rem' }}>
                <label className="form-label" style={{ fontSize: '0.82rem' }}>Payriff Secret Key</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder={isAz ? 'Payriff gizli açarınız (dəyişmirsinizsə toxunmayın)' : 'Your Payriff secret key'}
                  value={aiTone.payriff_secret_key}
                  onChange={(e) => setAiTone({ ...aiTone, payriff_secret_key: e.target.value })}
                />
              </div>

              {webhookUrls.payriff && (
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  <div style={{ marginBottom: '0.25rem' }}>
                    {isAz ? 'Payriff kabinetində daxil ediləcək Callback / Webhook URL:' : 'Callback / Webhook URL to enter in Payriff dashboard:'}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <code style={{ flex: 1, padding: '0.35rem 0.5rem', borderRadius: '6px', background: 'rgba(0,0,0,0.25)', wordBreak: 'break-all' }}>
                      {webhookUrls.payriff}
                    </code>
                    <button
                      type="button"
                      className="btn-secondary"
                      style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                      onClick={() => navigator.clipboard?.writeText(webhookUrls.payriff)}
                    >
                      {isAz ? 'Kopyala' : 'Copy'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {(entitlements.allowed_payment_providers || ['cash', 'payriff', 'epoint']).includes('epoint') && (
            <div
              style={{
                padding: '1rem',
                borderRadius: '10px',
                border: '1px solid var(--border)',
                background: 'rgba(255,255,255,0.02)',
                marginBottom: '0.85rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
                <strong style={{ fontSize: '0.95rem' }}>EPoint (AZN)</strong>
                <span style={{ fontSize: '0.78rem', color: aiTone.epoint_public_key ? 'var(--success)' : 'var(--text-secondary)' }}>
                  {aiTone.epoint_public_key
                    ? isAz ? 'Qoşulub' : 'Configured'
                    : isAz ? 'Məlumat tələb olunur' : 'Not configured'}
                </span>
              </div>

              <div className="form-group" style={{ marginBottom: '0.6rem' }}>
                <label className="form-label" style={{ fontSize: '0.82rem' }}>EPoint Public Key</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="i000000001"
                  value={aiTone.epoint_public_key}
                  onChange={(e) => setAiTone({ ...aiTone, epoint_public_key: e.target.value })}
                />
              </div>

              <div className="form-group" style={{ marginBottom: '0.65rem' }}>
                <label className="form-label" style={{ fontSize: '0.82rem' }}>EPoint Private Key</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder={isAz ? 'EPoint private açarınız (dəyişmirsinizsə toxunmayın)' : 'Your EPoint private key'}
                  value={aiTone.epoint_private_key}
                  onChange={(e) => setAiTone({ ...aiTone, epoint_private_key: e.target.value })}
                />
              </div>

              {webhookUrls.epoint && (
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  <div style={{ marginBottom: '0.25rem' }}>
                    {isAz ? 'EPoint kabinetində Result / Callback URL olaraq daxil edin:' : 'Result / Callback URL to enter in EPoint dashboard:'}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <code style={{ flex: 1, padding: '0.35rem 0.5rem', borderRadius: '6px', background: 'rgba(0,0,0,0.25)', wordBreak: 'break-all' }}>
                      {webhookUrls.epoint}
                    </code>
                    <button
                      type="button"
                      className="btn-secondary"
                      style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                      onClick={() => navigator.clipboard?.writeText(webhookUrls.epoint)}
                    >
                      {isAz ? 'Kopyala' : 'Copy'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            {isAz
              ? 'Bütün nağd və onlayn kart əməliyyatları avtomatik olaraq "Ödənişlər və Gəlir" jurnalında qeydə alınır.'
              : 'All cash and online card transactions are automatically recorded in your Payments & Revenue ledger.'}
          </div>
        </div>

        {/* 2b. Beh (Pre-Payment / Deposit) Rules — Master toggle stays with Admin */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', gap: '0.5rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <CreditCard color="var(--primary)" size={24} />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold', margin: 0 }}>
                {isAz ? 'Beh (Ön Ödəniş) Qaydaları' : 'Deposit (Beh) Rules'}
              </h2>
            </div>
            <span className={entitlements.allows_no_show_deposits ? 'badge badge-success' : 'badge badge-warning'}>
              {entitlements.allows_no_show_deposits
                ? isAz
                  ? 'Admin tərəfindən Aktivdir'
                  : 'Enabled by Admin'
                : isAz
                ? 'Admin tərəfindən Deaktivdir'
                : 'Disabled by Admin'}
            </span>
          </div>

          {!entitlements.allows_no_show_deposits ? (
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
                <Lock size={16} />
                {isAz
                  ? `Beh (ön ödəniş) funksiyası hazırda (${planName}) paketinizdə və ya Admin tərəfindən aktiv edilməyib.`
                  : `Deposit (Beh) collection is currently disabled by Platform Admin for your (${planName}) plan.`}
              </div>
              {isAz
                ? 'Beh funksiyası aktivləşdirildikdə kimlərdən və hansı xidmətlərdən ön ödəniş alınacağını burada tənzimləyə biləcəksiniz.'
                : 'Once enabled by the platform administrator, you can configure which bookings and services require a deposit here.'}
            </div>
          ) : (
            <>
              <div className="form-group">
                <label className="form-label">
                  {isAz ? 'Kimlərdən Beh Tələb Olunsun?' : 'Who Should Pay a Deposit (Beh)?'}
                </label>
                <select
                  className="form-control"
                  value={aiTone.deposit_rule_mode}
                  onChange={(e) => setAiTone({ ...aiTone, deposit_rule_mode: e.target.value })}
                >
                  <option value="high_risk_only">
                    {isAz
                      ? 'Yalnız əvvəl gəlməyən (No-Show) müştərilər'
                      : 'Only customers with past no-shows'}
                  </option>
                  <option value="above_amount">
                    {isAz
                      ? 'Müəyyən məbləğdən yuxarı xidmətlər'
                      : 'Services above a minimum price'}
                  </option>
                  <option value="selected_services">
                    {isAz
                      ? 'Yalnız seçilmiş yüksək dəyərli xidmətlər'
                      : 'Selected high-value services only'}
                  </option>
                  <option value="all">
                    {isAz ? 'Bütün randevular' : 'All bookings'}
                  </option>
                </select>
              </div>

              {aiTone.deposit_rule_mode === 'above_amount' && (
                <div className="form-group">
                  <label className="form-label">
                    {isAz ? 'Minimum Xidmət Məbləği (AZN)' : 'Minimum Service Price (AZN)'}
                  </label>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    className="form-control"
                    value={aiTone.deposit_min_service_price}
                    onChange={(e) =>
                      setAiTone({ ...aiTone, deposit_min_service_price: Number(e.target.value) || 0 })
                    }
                  />
                </div>
              )}

              {aiTone.deposit_rule_mode === 'selected_services' && (
                <div className="form-group">
                  <label className="form-label">
                    {isAz ? 'Beh Tələb Olunan Xidmətlər' : 'Services Requiring Deposit'}
                  </label>
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.45rem',
                      maxHeight: '150px',
                      overflowY: 'auto',
                      padding: '0.65rem',
                      borderRadius: '8px',
                      border: '1px solid var(--border)',
                      background: 'rgba(255,255,255,0.02)',
                    }}
                  >
                    {services.length === 0 ? (
                      <span style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                        {isAz ? 'Hələ xidmət əlavə edilməyib.' : 'No services created yet.'}
                      </span>
                    ) : (
                      services.map((svc) => (
                        <label
                          key={svc.id}
                          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.86rem', cursor: 'pointer' }}
                        >
                          <input
                            type="checkbox"
                            checked={(aiTone.deposit_service_ids || []).includes(svc.id)}
                            onChange={() => toggleDepositService(svc.id)}
                          />
                          <span>
                            {svc.name} ({Number(svc.price).toFixed(2)} {svc.currency || 'AZN'})
                          </span>
                        </label>
                      ))
                    )}
                  </div>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div className="form-group">
                  <label className="form-label">{isAz ? 'Beh Hesablanması' : 'Deposit Type'}</label>
                  <select
                    className="form-control"
                    value={aiTone.deposit_calc_type}
                    onChange={(e) => setAiTone({ ...aiTone, deposit_calc_type: e.target.value })}
                  >
                    <option value="percentage">{isAz ? 'Xidmət qiymətinin %' : 'Percentage (%)'}</option>
                    <option value="fixed">{isAz ? 'Sabit məbləğ (AZN)' : 'Fixed amount (AZN)'}</option>
                  </select>
                </div>

                {aiTone.deposit_calc_type === 'fixed' ? (
                  <div className="form-group">
                    <label className="form-label">{isAz ? 'Sabit Beh (AZN)' : 'Fixed Deposit (AZN)'}</label>
                    <input
                      type="number"
                      min="1"
                      step="0.5"
                      className="form-control"
                      value={aiTone.deposit_fixed_amount}
                      onChange={(e) =>
                        setAiTone({ ...aiTone, deposit_fixed_amount: Number(e.target.value) || 0 })
                      }
                    />
                  </div>
                ) : (
                  <div className="form-group">
                    <label className="form-label">{isAz ? 'Beh Faizi (%)' : 'Deposit Percentage (%)'}</label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      step="1"
                      className="form-control"
                      value={aiTone.deposit_percentage}
                      onChange={(e) =>
                        setAiTone({ ...aiTone, deposit_percentage: Number(e.target.value) || 0 })
                      }
                    />
                  </div>
                )}
              </div>

              <div
                style={{
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border)',
                  background: 'rgba(16, 185, 129, 0.06)',
                  marginTop: '0.25rem',
                }}
              >
                <label
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.88rem', fontWeight: 600 }}
                >
                  <input
                    type="checkbox"
                    checked={Boolean(aiTone.deposit_skip_regular_customers)}
                    onChange={(e) =>
                      setAiTone({ ...aiTone, deposit_skip_regular_customers: e.target.checked })
                    }
                  />
                  <span>
                    {isAz
                      ? 'Daimi müştəriləri behdən azad et (Qaydaları keç)'
                      : 'Skip deposit rules for regular customers'}
                  </span>
                </label>
                {aiTone.deposit_skip_regular_customers && (
                  <div style={{ marginTop: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      {isAz ? 'Minimum tamamlanmış ziyarət:' : 'Min completed visits:'}
                    </span>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      className="form-control"
                      style={{ width: '84px', padding: '0.3rem 0.5rem' }}
                      value={aiTone.deposit_regular_min_visits}
                      onChange={(e) =>
                        setAiTone({
                          ...aiTone,
                          deposit_regular_min_visits: Math.max(1, Number(e.target.value) || 1),
                        })
                      }
                    />
                  </div>
                )}
              </div>
            </>
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
              : 'Included in all plans. Pair your business WhatsApp number in 1 QR scan directly to your AI receptionist.'}
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
            <li>
              {isAz
                ? 'Biznes nömrənizi şəxsi nömrənizlə bir WhatsApp qrupuna əlavə edin: qrupda növbəti müştərini, gəliri və abunəliyi soruşa, həmçinin #Q-XXX kodu ilə cavab yazıb AI-a öyrədə bilərsiniz.'
                : 'Add your business number and personal number to a WhatsApp group: ask about your next customer, revenue, or subscription, and reply with #Q-XXX to answer customers and train your AI.'}
            </li>
          </ol>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleGenerateQr}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', justifyContent: 'center', marginBottom: '1.25rem' }}
          >
            <QrCode size={18} />
            <span>
              {isAz ? 'Statusu Yoxla / WhatsApp QR Kodu Yarat' : 'Check Status / Generate WhatsApp QR Code'}
            </span>
          </button>

          <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label" style={{ marginBottom: 0 }}>
                {isAz ? 'Xüsusi İdarəetmə Qrupu (Yalnız bu qrupda işləyir)' : 'Dedicated Management Group'}
              </label>
              <button type="button" className="btn btn-secondary" style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }} onClick={handleRefreshGroups}>
                {isAz ? 'Qrupları Yenilə' : 'Refresh'}
              </button>
            </div>
            {waGroups.length > 0 ? (
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.6rem' }}>
                <select
                  className="form-control"
                  value={selectedGroupJid}
                  onChange={(e) => {
                    const jid = e.target.value;
                    const found = waGroups.find((g) => g.id === jid);
                    handleSelectDedicatedGroup(jid, found?.subject);
                  }}
                >
                  <option value="">{isAz ? 'Qrup seçin...' : 'Select a WhatsApp group...'}</option>
                  {waGroups.map((g) => (
                    <option key={g.id} value={g.id}>
                      {g.subject}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.6rem' }}>
                <input
                  type="text"
                  className="form-control"
                  placeholder="12036302...@g.us"
                  value={manualGroupJid}
                  onChange={(e) => setManualGroupJid(e.target.value)}
                />
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => handleSelectDedicatedGroup(manualGroupJid, 'Dedicated Management Group')}
                >
                  {isAz ? 'Təyin Et' : 'Save'}
                </button>
              </div>
            )}
            {selectedGroupJid && (
              <div style={{ fontSize: '0.78rem', color: 'var(--success)' }}>
                {isAz ? 'Aktiv İdarəetmə Qrupu:' : 'Active Group:'} <code>{selectedGroupJid}</code>
              </div>
            )}
          </div>
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
                {isAz
                  ? 'Telegram botunuzun giriş açarını (Bot Token) aşağıya daxil edin. Sistem botunuzu avtomatik olaraq canlı randevu rejiminə qoşur.'
                  : 'Paste your Telegram Bot token below. We automatically connect and activate your live booking bot.'}
              </p>
              <div className="form-group">
                <label className="form-label">{isAz ? 'Telegram Bot Giriş Açarı (Token)' : 'Telegram Bot Token'}</label>
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

        {/* 7. Google & Apple Calendar Sync (.ics Subscription) */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', gap: '0.5rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Globe color="var(--primary)" size={24} />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold', margin: 0 }}>
                {isAz ? 'Google & Apple Təqvim Sinxronizasiyası' : 'Google & Apple Calendar Sync'}
              </h2>
            </div>
            <span
              className={
                entitlements.allows_gcal_sync || entitlements.allows_apple_cal_sync
                  ? 'badge badge-success'
                  : 'badge badge-warning'
              }
            >
              {entitlements.allows_gcal_sync || entitlements.allows_apple_cal_sync
                ? isAz
                  ? 'Paketdə Aktivdir'
                  : 'Enabled on Plan'
                : isAz
                ? 'Paketdə Deaktivdir'
                : 'Disabled on Plan'}
            </span>
          </div>

          {!(entitlements.allows_gcal_sync || entitlements.allows_apple_cal_sync) ? (
            <div
              style={{
                padding: '1rem',
                borderRadius: '8px',
                background: 'rgba(255,255,255,0.03)',
                color: 'var(--text-secondary)',
                fontSize: '0.9rem',
              }}
            >
              <Lock size={15} style={{ marginRight: '0.4rem', verticalAlign: 'middle' }} />
              {isAz
                ? `Təqvim sinxronizasiyası (${planName}) paketinizdə aktiv deyil. Pro/Enterprise paketinə keçin.`
                : `Calendar sync is disabled on your (${planName}) plan. Upgrade to Pro or Enterprise.`}
            </div>
          ) : (
            <>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '0.85rem' }}>
                {isAz
                  ? 'Aşağıdakı canlı .ics linkini Google Calendar ("Add by URL") və ya Apple Calendar ("New Calendar Subscription") bölməsinə əlavə edin:'
                  : 'Subscribe to your live .ics feed in Google Calendar ("Add by URL") or Apple Calendar ("New Calendar Subscription"):'}
              </p>
              <div
                style={{
                  padding: '0.7rem 0.85rem',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid var(--border)',
                  fontFamily: 'monospace',
                  fontSize: '0.78rem',
                  wordBreak: 'break-all',
                  marginBottom: '0.85rem',
                }}
              >
                {`https://api.randevu.vip/api/v1/appointments/ical-feed?business_id=${businessId}`}
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  const url = `https://api.randevu.vip/api/v1/appointments/ical-feed?business_id=${businessId}`;
                  if (navigator.clipboard) navigator.clipboard.writeText(url);
                  setChannelStatusMsg(
                    isAz ? 'Təqvim (.ics) linki kopyalandı!' : 'Calendar (.ics) feed URL copied!'
                  );
                }}
                style={{ width: '100%', justifyContent: 'center' }}
              >
                {isAz ? 'Təqvim Linkini (.ics) Kopyala' : 'Copy Calendar Feed URL (.ics)'}
              </button>
            </>
          )}
        </div>

        {/* 8. Cancel Business Account (Danger Zone) */}
        <div
          className="glass-card"
          style={{ padding: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.35)' }}
        >
          <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--error)', marginBottom: '0.5rem' }}>
            {isAz ? 'Hesabı Ləğv Et' : 'Cancel Account'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1rem' }}>
            {isAz
              ? 'Hesabınızı ləğv etdikdə aktiv abunəliyiniz dayandırılır və istəsəniz son ödəniş üçün geri ödəniş (refund) tələbi göndərə bilərsiniz.'
              : 'Cancelling your account stops any active recurring subscription and optionally submits a refund request for your latest payment.'}
          </p>
          {!cancelConfirmOpen ? (
            <button
              type="button"
              className="btn btn-secondary"
              style={{ color: 'var(--error)', borderColor: 'rgba(239, 68, 68, 0.45)' }}
              onClick={() => setCancelConfirmOpen(true)}
            >
              {isAz ? 'Hesabımı Ləğv Etmək İstəyirəm' : 'Cancel My Account'}
            </button>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <textarea
                className="form-control"
                rows={2}
                placeholder={isAz ? 'Ləğv etmə səbəbiniz (istəyə bağlı)...' : 'Reason for cancelling (optional)...'}
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
              />
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.86rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={cancelWithRefund}
                  onChange={(e) => setCancelWithRefund(e.target.checked)}
                />
                <span>
                  {isAz
                    ? 'Son ödənişim üçün geri ödəniş (refund) də tələb et'
                    : 'Also request a refund for my latest completed payment'}
                </span>
              </label>
              <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setCancelConfirmOpen(false)}
                >
                  {isAz ? 'Vazgeç' : 'Keep Account'}
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={async () => {
                    try {
                      await api.post('/businesses/cancel-account', {
                        reason: cancelReason,
                        request_refund: cancelWithRefund,
                      });
                      logout();
                      window.location.href = '/login';
                    } catch (err) {
                      setChannelStatusMsg(err.response?.data?.detail || 'Could not cancel account.');
                    }
                  }}
                >
                  {isAz ? 'Bəli, Hesabı Ləğv Et' : 'Confirm Account Cancellation'}
                </button>
              </div>
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
                <p>{isAz ? 'WhatsApp bağlantısı yoxlanılır...' : 'Checking WhatsApp connection...'}</p>
              </div>
            ) : whatsappState.status === 'connected' ? (
              <div style={{ padding: '2rem 0', color: 'var(--success)' }}>
                <CheckCircle2 size={42} style={{ marginBottom: '0.75rem' }} />
                <div style={{ fontWeight: 600 }}>
                  {isAz ? 'WhatsApp Nömrəsi Qoşulub' : 'WhatsApp Number Connected'}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  {whatsappState.instance_name}
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
                  {isAz ? 'WhatsApp statusu:' : 'WhatsApp status:'} <strong>{whatsappState.status}</strong>
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
