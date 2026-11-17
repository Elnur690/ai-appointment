import React, { useState, useEffect } from 'react';
import { useDataStore } from '../store/dataStore';
import Modal from '../components/common/Modal';
import { Check, MessageSquare, Instagram, Send, CreditCard, Mic, Globe } from 'lucide-react';

const Plans = () => {
  const { plans, fetchPlans, createPlan, updatePlan } = useDataStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);

  useEffect(() => {
    fetchPlans();
  }, [fetchPlans]);

  const defaultForm = {
    name: '',
    price: '',
    limits: '',
    allows_whatsapp: true,
    allows_instagram: false,
    allows_telegram: false,
    allows_voice_messages: false,
    allows_dynamic_pricing: false,
    allows_winback_campaigns: false,
    allows_discovery: false,
    allows_online_payments: false,
    allows_gcal_sync: false,
    allows_custom_domain: false,
    allows_no_show_deposits: false,
    allows_emergency_reassignment: false,
    allows_omnichannel_messaging: false,
    allows_growth_advisor: false,
    allows_geo_routing: false,
    allows_shift_management: false,
    allows_cadence_engine: false,
    allows_gift_vouchers: false,
    allows_flash_drops: false,
    features: '',
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
      allows_whatsapp: plan.allows_whatsapp !== false,
      allows_instagram: Boolean(plan.allows_instagram),
      allows_telegram: Boolean(plan.allows_telegram),
      allows_voice_messages: Boolean(plan.allows_voice_messages),
      allows_dynamic_pricing: Boolean(plan.allows_dynamic_pricing),
      allows_winback_campaigns: Boolean(plan.allows_winback_campaigns),
      allows_discovery: Boolean(plan.allows_discovery),
      allows_online_payments: Boolean(plan.allows_online_payments),
      allows_gcal_sync: Boolean(plan.allows_gcal_sync),
      allows_custom_domain: Boolean(plan.allows_custom_domain),
      allows_no_show_deposits: Boolean(plan.allows_no_show_deposits),
      allows_emergency_reassignment: Boolean(plan.allows_emergency_reassignment),
      allows_omnichannel_messaging: Boolean(plan.allows_omnichannel_messaging),
      allows_growth_advisor: Boolean(plan.allows_growth_advisor),
      allows_geo_routing: Boolean(plan.allows_geo_routing),
      allows_shift_management: Boolean(plan.allows_shift_management),
      allows_cadence_engine: Boolean(plan.allows_cadence_engine),
      allows_gift_vouchers: Boolean(plan.allows_gift_vouchers),
      allows_flash_drops: Boolean(plan.allows_flash_drops),
      features: plan.features || '',
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
        message_limit: parsedLimit,
        allows_whatsapp: newPlan.allows_whatsapp !== false,
        allows_instagram: Boolean(newPlan.allows_instagram),
        allows_telegram: Boolean(newPlan.allows_telegram),
        allows_omnichannel_messaging: Boolean(newPlan.allows_instagram || newPlan.allows_telegram),
        allows_voice_messages: Boolean(newPlan.allows_voice_messages),
        allows_dynamic_pricing: Boolean(newPlan.allows_dynamic_pricing),
        allows_winback_campaigns: Boolean(newPlan.allows_winback_campaigns),
        allows_discovery: Boolean(newPlan.allows_discovery),
        allows_online_payments: Boolean(newPlan.allows_online_payments),
        allows_gcal_sync: Boolean(newPlan.allows_gcal_sync),
        allows_custom_domain: Boolean(newPlan.allows_custom_domain),
        allows_no_show_deposits: Boolean(newPlan.allows_no_show_deposits),
        allows_emergency_reassignment: Boolean(newPlan.allows_emergency_reassignment),
        allows_growth_advisor: Boolean(newPlan.allows_growth_advisor),
        allows_geo_routing: Boolean(newPlan.allows_geo_routing),
        allows_shift_management: Boolean(newPlan.allows_shift_management),
        allows_cadence_engine: Boolean(newPlan.allows_cadence_engine),
        allows_gift_vouchers: Boolean(newPlan.allows_gift_vouchers),
        allows_flash_drops: Boolean(newPlan.allows_flash_drops),
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

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1>Subscription Plans & Channel Entitlements</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            WhatsApp is included in the default package. Enable or disable Instagram Direct, Telegram Bot, and Online Payment Gateways per plan.
          </p>
        </div>
        <button className="btn btn-primary" onClick={handleOpenCreate}>
          + Create Plan
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
        {plans.map((plan) => (
          <div key={plan.id} className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{plan.name}</h2>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary-start)', marginBottom: '1.5rem' }}>
              {plan.price}
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Check size={16} color="var(--success)" />
                <span style={{ color: 'var(--text-secondary)' }}>{plan.limits}</span>
              </div>

              {/* Channel 1: WhatsApp (Default Package) */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '8px',
                  background: 'rgba(16, 185, 129, 0.1)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <MessageSquare size={16} color="var(--success)" />
                  <span>WhatsApp Business</span>
                </div>
                <strong style={{ color: 'var(--success)', fontSize: '0.85rem' }}>Default (Included)</strong>
              </div>

              {/* Channel 2: Instagram Direct (Toggleable) */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.04)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Instagram size={16} color="var(--primary-start)" />
                  <span>Instagram Direct AI</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleQuickToggle(plan, 'allows_instagram')}
                  className={plan.allows_instagram ? 'btn btn-primary' : 'btn btn-secondary'}
                  style={{ padding: '0.25rem 0.65rem', fontSize: '0.78rem' }}
                >
                  {plan.allows_instagram ? 'Enabled (Click to Disable)' : 'Disabled (Click to Enable)'}
                </button>
              </div>

              {/* Channel 3: Telegram Bot (Toggleable) */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.04)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Send size={16} color="var(--primary-start)" />
                  <span>Telegram Bot AI</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleQuickToggle(plan, 'allows_telegram')}
                  className={plan.allows_telegram ? 'btn btn-primary' : 'btn btn-secondary'}
                  style={{ padding: '0.25rem 0.65rem', fontSize: '0.78rem' }}
                >
                  {plan.allows_telegram ? 'Enabled (Click to Disable)' : 'Disabled (Click to Enable)'}
                </button>
              </div>

              {/* Online Payment Gateways */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                <CreditCard size={16} color="var(--primary-start)" />
                <span>
                  Online Gateways (Payriff & Paymegate):{' '}
                  <strong>{plan.allows_online_payments ? 'Enabled' : 'Cash Only'}</strong>
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Mic size={16} color="var(--primary-start)" />
                <span>
                  Voice Notes: <strong>{plan.allows_voice_messages ? 'Included' : 'Disabled'}</strong>
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Globe size={16} color="var(--primary-start)" />
                <span>
                  Custom Domain (CNAME): <strong>{plan.allows_custom_domain ? 'Included' : 'Disabled'}</strong>
                </span>
              </div>
            </div>

            <div style={{ marginTop: '1.75rem', display: 'flex', gap: '1rem' }}>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => handleOpenEdit(plan)}>
                Edit Plan & Channels
              </button>
            </div>
          </div>
        ))}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingPlan ? `Edit Plan: ${editingPlan.name}` : 'Create SaaS Tier Plan'}
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Plan Name</label>
            <input
              type="text"
              className="form-control"
              value={newPlan.name}
              onChange={(e) => setNewPlan({ ...newPlan, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Monthly Price (AZN)</label>
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
            <label className="form-label">AI Message Quota / Month</label>
            <input
              type="text"
              className="form-control"
              placeholder="5000"
              value={newPlan.limits}
              onChange={(e) => setNewPlan({ ...newPlan, limits: e.target.value })}
              required
            />
          </div>

          <div style={{ margin: '1.5rem 0' }}>
            <label className="form-label" style={{ marginBottom: '0.75rem', display: 'block' }}>
              Messaging Channels & Payment Gateways
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_whatsapp}
                onChange={(e) => setNewPlan({ ...newPlan, allows_whatsapp: e.target.checked })}
              />
              <span>WhatsApp Business Line (Default Package)</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_instagram}
                onChange={(e) => setNewPlan({ ...newPlan, allows_instagram: e.target.checked })}
              />
              <span>Allow Instagram Direct AI Integration</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_telegram}
                onChange={(e) => setNewPlan({ ...newPlan, allows_telegram: e.target.checked })}
              />
              <span>Allow Telegram Bot AI Integration</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_online_payments}
                onChange={(e) => setNewPlan({ ...newPlan, allows_online_payments: e.target.checked })}
              />
              <span>Allow Online Payment Gateways (Payriff & Paymegate)</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_voice_messages}
                onChange={(e) => setNewPlan({ ...newPlan, allows_voice_messages: e.target.checked })}
              />
              <span>Allow WhatsApp Voice Notes Processing</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_custom_domain}
                onChange={(e) => setNewPlan({ ...newPlan, allows_custom_domain: e.target.checked })}
              />
              <span>Allow White-Label Custom CNAME Domain</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_no_show_deposits}
                onChange={(e) => setNewPlan({ ...newPlan, allows_no_show_deposits: e.target.checked })}
              />
              <span>Allow AI No-Show Protection & Dynamic Deposits</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_shift_management}
                onChange={(e) => setNewPlan({ ...newPlan, allows_shift_management: e.target.checked })}
              />
              <span>Allow Shift-Aware Scheduling & Overtime Management</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_cadence_engine}
                onChange={(e) => setNewPlan({ ...newPlan, allows_cadence_engine: e.target.checked })}
              />
              <span>Allow Predictive Cadence Rebooking</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_gift_vouchers}
                onChange={(e) => setNewPlan({ ...newPlan, allows_gift_vouchers: e.target.checked })}
              />
              <span>Allow Digital Gift Vouchers & VIP Loyalty</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={newPlan.allows_flash_drops}
                onChange={(e) => setNewPlan({ ...newPlan, allows_flash_drops: e.target.checked })}
              />
              <span>Allow Last-Minute Flash Drops & Waitlist</span>
            </label>
          </div>

          <div className="flex-between">
            <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {editingPlan ? 'Save Plan Changes' : 'Create Tier Plan'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Plans;
