import React, { useState, useEffect } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import Modal from '../components/common/Modal';
import { Check, X, MessageSquare, Instagram, Send, Clock } from 'lucide-react';

const ALL_PLAN_FEATURES = [
  {
    key: 'allows_whatsapp',
    defaultIncluded: true,
    az: 'WhatsApp Biznes AI Resepşn (Standart Paket)',
    en: 'WhatsApp Business AI Receptionist (Default Included)',
  },
  {
    key: 'allows_instagram',
    az: 'Instagram Direct AI Resepşn İnteqrasiyası',
    en: 'Instagram Direct AI Receptionist Integration',
  },
  {
    key: 'allows_telegram',
    az: 'Telegram Bot AI Resepşn İnteqrasiyası',
    en: 'Telegram Bot AI Receptionist Integration',
  },
  {
    key: 'allows_voice_messages',
    az: 'WhatsApp Səsli Mesajların Tanınması və Randevu Yazılması',
    en: 'WhatsApp Voice Note Transcription & Booking',
  },
  {
    key: 'allows_online_payments',
    az: 'Onlayn Ödəniş Şlüzləri (Payriff və EPoint)',
    en: 'Online Payment Gateways (Payriff & EPoint)',
  },
  {
    key: 'allows_no_show_deposits',
    az: 'AI Gəlməmə (No-Show) Qorunması və Dinamik Beh (Depozit)',
    en: 'AI No-Show Protection & Dynamic Deposits',
  },
  {
    key: 'allows_shift_management',
    az: 'Növbəli İş Qrafiki (Səhər/Axşam/Tam) və Əlavə İş Saatı (Overtime)',
    en: 'Shift-Aware Staff Scheduling & Overtime Management',
  },
  {
    key: 'allows_cadence_engine',
    az: 'Proqnozlaşdırıcı Təkrar Randevu Mühərriki (Cadence Engine)',
    en: 'Predictive Cadence Rebooking Engine',
  },
  {
    key: 'allows_flash_drops',
    az: 'Son Dəqiqə Endirimləri (Flash Drops) və Gözləmə Siyahısı',
    en: 'Last-Minute Flash Drops & Smart Waitlist',
  },
  {
    key: 'allows_gift_vouchers',
    az: 'Rəqəmsal Hədiyyə Kartları və Kupon Satışı',
    en: 'Digital Gift Vouchers & Gifting',
  },
  {
    key: 'allows_loyalty_program',
    az: 'VIP Müştəri Loyallıq Proqramı (Gümüş və Qızıl Statuslar)',
    en: 'VIP Customer Loyalty Program (Silver & Gold Tiers)',
  },
  {
    key: 'allows_combo_packages',
    az: 'Kombo Xidmət Paketləri (Multi-Service Packages)',
    en: 'Multi-Service Combo Packages',
  },
  {
    key: 'allows_group_bookings',
    az: 'Qrup və Ailəvi Randevu Qəbulu',
    en: 'Group & Family Bookings',
  },
  {
    key: 'allows_product_upsells',
    az: 'AI Məhsul və Kosmetika Əlavə Satışı (Upsell)',
    en: 'AI Retail Product Upsells',
  },
  {
    key: 'allows_dynamic_pricing',
    az: 'Dinamik Qiymətləndirmə (Sakit Saat Endirimləri və Pik Saatlar)',
    en: 'Dynamic Off-Peak & Surge Pricing',
  },
  {
    key: 'allows_winback_campaigns',
    az: 'Avtomatik İtirilmiş Müştəriləri Qaytarma (Win-Back) Kampaniyası',
    en: 'Automated Customer Win-Back Campaigns',
  },
  {
    key: 'allows_gcal_sync',
    az: 'Google Təqvim 2-Tərəfli Sinxronizasiya',
    en: 'Google Calendar 2-Way Sync',
  },
  {
    key: 'allows_apple_cal_sync',
    az: 'Apple iCloud Təqvim Sinxronizasiyası',
    en: 'Apple iCloud Calendar Sync',
  },
  {
    key: 'allows_geo_routing',
    az: 'WhatsApp Konum (Geo-Location) ilə Ən Yaxın Filiala Yönləndirmə',
    en: 'WhatsApp Geo-Location Nearest Branch Auto-Routing',
  },
  {
    key: 'allows_emergency_reassignment',
    az: 'Təcili Usta Əvəzləməsi (Xəstəlik / Məzuniyyət Transferi)',
    en: 'Emergency Staff Reassignment & Sick-Leave Swaps',
  },
  {
    key: 'allows_growth_advisor',
    az: 'Həftəlik AI Biznes və Gəlir Məsləhətçisi',
    en: 'Weekly AI Business & Revenue Growth Advisor',
  },
  {
    key: 'allows_branch_level_ai_tone',
    az: 'Hər Filial Üçün Fərdi AI Ünsiyyət Tonu',
    en: 'Branch-Level Custom AI Persona & Tone',
  },
  {
    key: 'allows_discovery',
    az: 'Müştəri Kəşfiyyat Kataloqunda (Marketplace) Görünmə',
    en: 'Public Marketplace & Business Discovery Listing',
  },
  {
    key: 'allows_custom_domain',
    az: 'Şəxsi Domen (White-Label CNAME: cname.randevu.vip)',
    en: 'White-Label Custom CNAME Domain (cname.randevu.vip)',
  },
];

const Plans = () => {
  const { plans, fetchPlans, createPlan, updatePlan } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);

  useEffect(() => {
    fetchPlans();
  }, [fetchPlans]);

  const defaultForm = {
    name: '',
    price: '',
    limits: '1000',
    max_branches: 1,
    max_whatsapp_numbers: 1,
    assigned_ai_model: 'gemini-3.5-flash',
    allows_free_trial: true,
    trial_days: 14,
    trial_features: {},
    allows_whatsapp: true,
    allows_instagram: false,
    allows_telegram: false,
    allows_voice_messages: false,
    allows_dynamic_pricing: false,
    allows_winback_campaigns: false,
    allows_discovery: false,
    allows_online_payments: false,
    allowed_payment_providers: ['cash', 'payriff', 'epoint'],
    allows_gcal_sync: false,
    allows_apple_cal_sync: false,
    allows_custom_domain: false,
    allows_no_show_deposits: false,
    allows_emergency_reassignment: false,
    allows_omnichannel_messaging: false,
    allows_growth_advisor: false,
    allows_loyalty_program: false,
    allows_combo_packages: false,
    allows_group_bookings: false,
    allows_product_upsells: false,
    allows_branch_level_ai_tone: false,
    allows_geo_routing: false,
    allows_shift_management: false,
    allows_cadence_engine: false,
    allows_gift_vouchers: false,
    allows_flash_drops: false,
  };

  const [newPlan, setNewPlan] = useState(defaultForm);

  const handleOpenCreate = () => {
    setEditingPlan(null);
    setNewPlan(defaultForm);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (plan) => {
    setEditingPlan(plan);
    setNewPlan({
      name: plan.name || '',
      price: String(plan.price_num || plan.price || ''),
      limits: String(plan.message_limit || 1000),
      max_branches: Number(plan.max_branches || 1),
      max_whatsapp_numbers: Number(plan.max_whatsapp_numbers || 1),
      assigned_ai_model: plan.features?.assigned_model || 'gemini-3.5-flash',
      allows_free_trial: plan.allows_free_trial !== false,
      trial_days: Number(plan.trial_days ?? 14),
      trial_features: plan.trial_features || {},
      allows_whatsapp: plan.allows_whatsapp !== false,
      allows_instagram: Boolean(plan.allows_instagram),
      allows_telegram: Boolean(plan.allows_telegram),
      allows_voice_messages: Boolean(plan.allows_voice_messages),
      allows_dynamic_pricing: Boolean(plan.allows_dynamic_pricing),
      allows_winback_campaigns: Boolean(plan.allows_winback_campaigns),
      allows_discovery: Boolean(plan.allows_discovery),
      allows_online_payments: Boolean(plan.allows_online_payments),
      allowed_payment_providers: Array.isArray(plan.allowed_payment_providers)
        ? plan.allowed_payment_providers
        : ['cash', 'payriff', 'epoint'],
      allows_gcal_sync: Boolean(plan.allows_gcal_sync),
      allows_apple_cal_sync: Boolean(plan.allows_apple_cal_sync),
      allows_custom_domain: Boolean(plan.allows_custom_domain),
      allows_no_show_deposits: Boolean(plan.allows_no_show_deposits),
      allows_emergency_reassignment: Boolean(plan.allows_emergency_reassignment),
      allows_omnichannel_messaging: Boolean(plan.allows_omnichannel_messaging),
      allows_growth_advisor: Boolean(plan.allows_growth_advisor),
      allows_loyalty_program: Boolean(plan.allows_loyalty_program),
      allows_combo_packages: Boolean(plan.allows_combo_packages),
      allows_group_bookings: Boolean(plan.allows_group_bookings),
      allows_product_upsells: Boolean(plan.allows_product_upsells),
      allows_branch_level_ai_tone: Boolean(plan.allows_branch_level_ai_tone),
      allows_geo_routing: Boolean(plan.allows_geo_routing),
      allows_shift_management: Boolean(plan.allows_shift_management),
      allows_cadence_engine: Boolean(plan.allows_cadence_engine),
      allows_gift_vouchers: Boolean(plan.allows_gift_vouchers),
      allows_flash_drops: Boolean(plan.allows_flash_drops),
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (editingPlan) {
      const parsedPrice = parseFloat(String(newPlan.price).replace(/[^0-9.]/g, '')) || editingPlan.price_num;
      const parsedLimit = parseInt(String(newPlan.limits).replace(/[^0-9]/g, ''), 10) || editingPlan.message_limit;
      await updatePlan(editingPlan.id, {
        name: newPlan.name,
        price: parsedPrice,
        max_branches: Number(newPlan.max_branches || 1),
        max_whatsapp_numbers: Number(newPlan.max_whatsapp_numbers || 1),
        message_limit: parsedLimit,
        allows_free_trial: Boolean(newPlan.allows_free_trial),
        trial_days: Number(newPlan.trial_days ?? 14),
        trial_features: newPlan.trial_features || {},
        allows_whatsapp: newPlan.allows_whatsapp !== false,
        allows_instagram: Boolean(newPlan.allows_instagram),
        allows_telegram: Boolean(newPlan.allows_telegram),
        allows_omnichannel_messaging: Boolean(newPlan.allows_instagram || newPlan.allows_telegram),
        allows_voice_messages: Boolean(newPlan.allows_voice_messages),
        allows_dynamic_pricing: Boolean(newPlan.allows_dynamic_pricing),
        allows_winback_campaigns: Boolean(newPlan.allows_winback_campaigns),
        allows_discovery: Boolean(newPlan.allows_discovery),
        allows_online_payments: Boolean(newPlan.allows_online_payments),
        allowed_payment_providers: Array.isArray(newPlan.allowed_payment_providers)
          ? newPlan.allowed_payment_providers
          : ['cash', 'payriff', 'epoint'],
        allows_gcal_sync: Boolean(newPlan.allows_gcal_sync),
        allows_apple_cal_sync: Boolean(newPlan.allows_apple_cal_sync),
        allows_custom_domain: Boolean(newPlan.allows_custom_domain),
        allows_no_show_deposits: Boolean(newPlan.allows_no_show_deposits),
        allows_emergency_reassignment: Boolean(newPlan.allows_emergency_reassignment),
        allows_growth_advisor: Boolean(newPlan.allows_growth_advisor),
        allows_loyalty_program: Boolean(newPlan.allows_loyalty_program),
        allows_combo_packages: Boolean(newPlan.allows_combo_packages),
        allows_group_bookings: Boolean(newPlan.allows_group_bookings),
        allows_product_upsells: Boolean(newPlan.allows_product_upsells),
        allows_branch_level_ai_tone: Boolean(newPlan.allows_branch_level_ai_tone),
        allows_geo_routing: Boolean(newPlan.allows_geo_routing),
        allows_shift_management: Boolean(newPlan.allows_shift_management),
        allows_cadence_engine: Boolean(newPlan.allows_cadence_engine),
        allows_gift_vouchers: Boolean(newPlan.allows_gift_vouchers),
        allows_flash_drops: Boolean(newPlan.allows_flash_drops),
        features: { assigned_model: newPlan.assigned_ai_model || 'gemini-3.5-flash' },
      });
    } else {
      await createPlan(newPlan);
    }
    setIsModalOpen(false);
  };

  const handleQuickToggle = async (plan, field) => {
    const nextVal = !plan[field];
    await updatePlan(plan.id, {
      [field]: nextVal,
      ...(field === 'allows_instagram' || field === 'allows_telegram'
        ? {
            allows_omnichannel_messaging:
              (field === 'allows_instagram' ? nextVal : plan.allows_instagram) ||
              (field === 'allows_telegram' ? nextVal : plan.allows_telegram),
          }
        : {}),
    });
  };

  const toggleTrialFeature = (key) => {
    setNewPlan((prev) => {
      const nextTrialFeats = { ...(prev.trial_features || {}) };
      nextTrialFeats[key] = !nextTrialFeats[key];
      return { ...prev, trial_features: nextTrialFeats };
    });
  };

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>{isAz ? 'Abunəlik Paketləri, Pulsuz Sınaq (Free Trial) və Xüsusiyyətlər' : 'Subscription Plans, Dynamic Free Trial & All Features'}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz
              ? 'Hər paket üçün Pulsuz Sınaq müddətini (gün), sınaq xüsusiyyətlərini, kanalları (WhatsApp, Instagram, Telegram) və 24+ funksiyanı dinamik tənzimləyin.'
              : 'Dynamically configure Free Trial duration (days), trial feature unlocks, channels (WhatsApp, Instagram, Telegram), and all 24+ features per plan.'}
          </p>
        </div>
        <button className="btn btn-primary" onClick={handleOpenCreate}>
          {isAz ? '+ Yeni Paket Yarat' : '+ Create Plan'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem' }}>
        {plans.map((plan) => (
          <div key={plan.id} className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
              <h2 style={{ fontSize: '1.5rem', margin: 0 }}>{plan.name}</h2>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '999px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  background: plan.allows_free_trial && plan.trial_days > 0 ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.06)',
                  color: plan.allows_free_trial && plan.trial_days > 0 ? 'var(--primary-start)' : 'var(--text-secondary)',
                }}
              >
                <Clock size={13} />
                {plan.allows_free_trial && plan.trial_days > 0
                  ? isAz
                    ? `${plan.trial_days} Gün Pulsuz Sınaq`
                    : `${plan.trial_days}-Day Free Trial`
                  : isAz
                  ? 'Pulsuz Sınaq Yoxdur'
                  : 'No Free Trial'}
              </span>
            </div>

            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary-start)', marginBottom: '1.25rem' }}>
              {plan.price_num} AZN/{isAz ? 'ay' : 'mo'}
            </div>

            {/* Channel Quick Toggles */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.45rem 0.75rem',
                  borderRadius: '8px',
                  background: 'rgba(16, 185, 129, 0.1)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.88rem' }}>
                  <MessageSquare size={15} color="var(--success)" />
                  <span>WhatsApp Business</span>
                </div>
                <strong style={{ color: 'var(--success)', fontSize: '0.8rem' }}>
                  {isAz ? 'Standart (Daxildir)' : 'Default (Included)'}
                </strong>
              </div>

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.45rem 0.75rem',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.04)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.88rem' }}>
                  <Instagram size={15} color="var(--primary-start)" />
                  <span>Instagram Direct AI</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleQuickToggle(plan, 'allows_instagram')}
                  className={plan.allows_instagram ? 'btn btn-primary' : 'btn btn-secondary'}
                  style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}
                >
                  {plan.allows_instagram
                    ? isAz
                      ? 'Aktivdir (Söndür)'
                      : 'Enabled (Disable)'
                    : isAz
                    ? 'Deaktivdir (Qoş)'
                    : 'Disabled (Enable)'}
                </button>
              </div>

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.45rem 0.75rem',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.04)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.88rem' }}>
                  <Send size={15} color="var(--primary-start)" />
                  <span>Telegram Bot AI</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleQuickToggle(plan, 'allows_telegram')}
                  className={plan.allows_telegram ? 'btn btn-primary' : 'btn btn-secondary'}
                  style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}
                >
                  {plan.allows_telegram
                    ? isAz
                      ? 'Aktivdir (Söndür)'
                      : 'Enabled (Disable)'
                    : isAz
                    ? 'Deaktivdir (Qoş)'
                    : 'Disabled (Enable)'}
                </button>
              </div>
            </div>

            {/* Complete List of All Platform Features */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.48rem', fontSize: '0.84rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Check size={15} color="var(--success)" />
                <span>
                  {isAz
                    ? `Ayda ${Number(plan.message_limit || 1000).toLocaleString()} AI mesaj • ${plan.max_branches || 1} filial • ${plan.max_whatsapp_numbers || 1} WhatsApp`
                    : `${Number(plan.message_limit || 1000).toLocaleString()} AI msgs/mo • ${plan.max_branches || 1} branch(es) • ${plan.max_whatsapp_numbers || 1} WhatsApp`}
                </span>
              </div>
              {ALL_PLAN_FEATURES.map((feat) => {
                const included =
                  feat.key === 'allows_whatsapp'
                    ? plan.allows_whatsapp !== false
                    : Boolean(plan[feat.key]);
                return (
                  <div
                    key={feat.key}
                    onClick={() => handleQuickToggle(plan, feat.key)}
                    title={isAz ? 'Dəyişmək üçün klikləyin' : 'Click to toggle'}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.5rem',
                      opacity: included ? 1 : 0.45,
                      cursor: 'pointer',
                    }}
                  >
                    {included ? (
                      <Check size={15} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    ) : (
                      <X size={15} color="var(--text-secondary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    )}
                    <span>{isAz ? feat.az : feat.en}</span>
                  </div>
                );
              })}
            </div>

            <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => handleOpenEdit(plan)}>
                {isAz ? 'Paketi və Pulsuz Sınağı Redaktə Et' : 'Edit Plan & Free Trial'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={
          editingPlan
            ? isAz
              ? `Paketi Redaktə Et: ${editingPlan.name}`
              : `Edit Plan: ${editingPlan.name}`
            : isAz
            ? 'Yeni Paket Yarat'
            : 'Create SaaS Tier Plan'
        }
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Paketin Adı' : 'Plan Name'}</label>
            <input
              type="text"
              className="form-control"
              value={newPlan.name}
              onChange={(e) => setNewPlan({ ...newPlan, name: e.target.value })}
              required
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">{isAz ? 'Aylıq Qiymət (AZN)' : 'Monthly Price (AZN)'}</label>
              <input
                type="text"
                className="form-control"
                placeholder="79"
                value={newPlan.price}
                onChange={(e) => setNewPlan({ ...newPlan, price: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">{isAz ? 'AI Mesaj Limiti / Ay' : 'AI Message Quota / Month'}</label>
              <input
                type="text"
                className="form-control"
                placeholder="5000"
                value={newPlan.limits}
                onChange={(e) => setNewPlan({ ...newPlan, limits: e.target.value })}
                required
              />
            </div>
          </div>

          {/* Dynamic Free Trial Configuration Section */}
          <div
            style={{
              padding: '1rem',
              background: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: '8px',
              marginBottom: '1.25rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontWeight: 600 }}>
                <input
                  type="checkbox"
                  checked={Boolean(newPlan.allows_free_trial)}
                  onChange={(e) => setNewPlan({ ...newPlan, allows_free_trial: e.target.checked })}
                />
                <span>{isAz ? 'Pulsuz Sınaq (Free Trial) Aktivdir' : 'Enable Free Trial on This Plan'}</span>
              </label>
              {newPlan.allows_free_trial && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem' }}>{isAz ? 'Müddət (Gün):' : 'Duration (Days):'}</span>
                  <input
                    type="number"
                    min="1"
                    max="365"
                    className="form-control"
                    style={{ width: '85px', padding: '0.35rem 0.5rem' }}
                    value={newPlan.trial_days}
                    onChange={(e) => setNewPlan({ ...newPlan, trial_days: Number(e.target.value) })}
                  />
                </div>
              )}
            </div>
            {newPlan.allows_free_trial && (
              <div style={{ maxHeight: '130px', overflowY: 'auto', fontSize: '0.82rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                <div style={{ color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                  {isAz
                    ? 'Pulsuz sınaq müddətində əlavə olaraq aktiv ediləcək xüsusiyyətləri seçin:'
                    : 'Select additional features to unlock dynamically during the Free Trial:'}
                </div>
                {ALL_PLAN_FEATURES.map((feat) => (
                  <label
                    key={`trial_${feat.key}`}
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem', cursor: 'pointer' }}
                  >
                    <input
                      type="checkbox"
                      checked={Boolean(newPlan.trial_features?.[feat.key] ?? newPlan[feat.key])}
                      onChange={() => toggleTrialFeature(feat.key)}
                    />
                    <span>{isAz ? feat.az : feat.en}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">{isAz ? 'Maksimum Filial Sayı' : 'Max Branches'}</label>
              <input
                type="number"
                min="1"
                className="form-control"
                value={newPlan.max_branches}
                onChange={(e) => setNewPlan({ ...newPlan, max_branches: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">{isAz ? 'Maksimum WhatsApp Nömrəsi' : 'Max WhatsApp Numbers'}</label>
              <input
                type="number"
                min="1"
                className="form-control"
                value={newPlan.max_whatsapp_numbers}
                onChange={(e) => setNewPlan({ ...newPlan, max_whatsapp_numbers: e.target.value })}
              />
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '1.25rem' }}>
            <label className="form-label">
              {isAz ? 'İcazə Verilən Ödəniş Provayderləri (Beh / Depozit)' : 'Allowed Payment Providers (Customer Deposits)'}
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', marginTop: '0.35rem' }}>
              {[
                { key: 'cash', label: isAz ? 'Nağd (Yerində)' : 'Cash (On-Site)' },
                { key: 'payriff', label: 'Payriff (AZ)' },
                { key: 'epoint', label: 'EPoint (AZ)' },
              ].map((prov) => {
                const selected = (newPlan.allowed_payment_providers || []).includes(prov.key);
                return (
                  <label
                    key={prov.key}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.45rem',
                      padding: '0.45rem 0.75rem',
                      borderRadius: '8px',
                      border: `1px solid ${selected ? 'var(--primary)' : 'var(--border)'}`,
                      background: selected ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => {
                        const curr = Array.isArray(newPlan.allowed_payment_providers)
                          ? newPlan.allowed_payment_providers
                          : [];
                        const next = curr.includes(prov.key)
                          ? curr.filter((k) => k !== prov.key)
                          : [...curr, prov.key];
                        setNewPlan({ ...newPlan, allowed_payment_providers: next });
                      }}
                    />
                    <span>{prov.label}</span>
                  </label>
                );
              })}
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '1.25rem' }}>
            <label className="form-label">{isAz ? 'Təyin Edilmiş AI Modeli' : 'Assigned AI Model Engine'}</label>
            <select
              className="form-control"
              value={newPlan.assigned_ai_model}
              onChange={(e) => setNewPlan({ ...newPlan, assigned_ai_model: e.target.value })}
            >
              <option value="gemini-3.5-flash">Google Gemini 3.5 Flash ($0.45 / 1M tokens)</option>
              <option value="claude-3-7-sonnet">Anthropic Claude 3.7 Sonnet ($9.00 / 1M tokens)</option>
              <option value="gpt-4o">OpenAI GPT-4o ($6.25 / 1M tokens)</option>
            </select>
          </div>

          <div style={{ margin: '1.25rem 0', maxHeight: '240px', overflowY: 'auto', paddingRight: '0.5rem' }}>
            <label className="form-label" style={{ marginBottom: '0.75rem', display: 'block' }}>
              {isAz ? 'Bütün Platforma Xüsusiyyətləri (24 Xüsusiyyət)' : 'All Platform Feature Entitlements (24 Features)'}
            </label>

            {ALL_PLAN_FEATURES.map((feat) => (
              <label
                key={feat.key}
                style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.65rem', cursor: 'pointer' }}
              >
                <input
                  type="checkbox"
                  checked={Boolean(newPlan[feat.key])}
                  onChange={(e) => setNewPlan({ ...newPlan, [feat.key]: e.target.checked })}
                />
                <span>{isAz ? feat.az : feat.en}</span>
              </label>
            ))}
          </div>

          <div className="flex-between">
            <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary">
              {editingPlan
                ? isAz
                  ? 'Dəyişiklikləri Yadda Saxla'
                  : 'Save Plan Changes'
                : isAz
                ? 'Paketi Yarat'
                : 'Create Tier Plan'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Plans;
