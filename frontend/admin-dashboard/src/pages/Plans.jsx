import React, { useState } from 'react';
import { useDataStore } from '../store/dataStore';
import Modal from '../components/common/Modal';
import { Check, Sparkles, Mic, TrendingUp, Megaphone, Search, CreditCard, Calendar, Globe } from 'lucide-react';

const Plans = () => {
  const { plans, createPlan } = useDataStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newPlan, setNewPlan] = useState({
    name: '',
    price: '',
    limits: '',
    allows_voice_messages: false,
    allows_dynamic_pricing: false,
    allows_winback_campaigns: false,
    allows_discovery: false,
    allows_online_payments: false,
    allows_gcal_sync: false,
    allows_custom_domain: false,
    allows_branch_level_ai_tone: false,
    features: ''
  });

  const handleCreate = (e) => {
    e.preventDefault();
    createPlan(newPlan);
    setIsModalOpen(false);
  };

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1>Subscription Plans</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Configure tier pricing and feature entitlement flags for SaaS businesses.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>+ Create Plan</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {plans.map((plan) => (
          <div key={plan.id} className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{plan.name}</h2>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary-start)', marginBottom: '1.5rem' }}>
              {plan.price}
            </div>
            
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <Check size={16} color="var(--success)" />
                <span style={{ color: 'var(--text-secondary)' }}>{plan.limits}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Mic size={16} color="var(--primary-start)" />
                <span>Voice Notes: <strong>Included</strong></span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <TrendingUp size={16} color="var(--primary-start)" />
                <span>Dynamic Off-Peak Pricing: <strong>Included</strong></span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Megaphone size={16} color="var(--primary-start)" />
                <span>Win-Back Campaigns: <strong>Included</strong></span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Search size={16} color="var(--primary-start)" />
                <span>Business Discovery: <strong>Included</strong></span>
              </div>
            </div>

            <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
              <button className="btn btn-secondary" style={{ flex: 1 }}>Edit Plan Features</button>
              <button className="btn btn-ghost" style={{ color: 'var(--error)' }}>Deactivate</button>
            </div>
          </div>
        ))}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create SaaS Tier Plan">
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">Plan Name</label>
            <input type="text" className="form-control" value={newPlan.name} onChange={(e) => setNewPlan({...newPlan, name: e.target.value})} required />
          </div>
          <div className="form-group">
            <label className="form-label">Monthly Price (AZN)</label>
            <input type="text" className="form-control" placeholder="79 AZN/mo" value={newPlan.price} onChange={(e) => setNewPlan({...newPlan, price: e.target.value})} required />
          </div>
          <div className="form-group">
            <label className="form-label">AI Message Quota</label>
            <input type="text" className="form-control" placeholder="1000 messages/mo" value={newPlan.limits} onChange={(e) => setNewPlan({...newPlan, limits: e.target.value})} required />
          </div>

          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Assigned AI Model Engine (SaaS Owner Control)</label>
            <select className="form-control" value={newPlan.assigned_ai_model || 'gemini-3.5-flash'} onChange={(e) => setNewPlan({...newPlan, assigned_ai_model: e.target.value})}>
              <option value="gemini-3.5-flash">Google Gemini 3.5 Flash (Default Tier Model)</option>
              <option value="claude-3-7-sonnet">Anthropic Claude 3.7 Sonnet (Pro Tier Model)</option>
              <option value="gpt-4o">OpenAI GPT-4o (Enterprise Tier Model)</option>
            </select>
          </div>
          
          <div style={{ margin: '1.5rem 0' }}>
            <label className="form-label" style={{ marginBottom: '1rem', display: 'block' }}>Feature Entitlements (Plan Gating Switches)</label>
            
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_voice_messages} onChange={(e) => setNewPlan({...newPlan, allows_voice_messages: e.target.checked})} />
              <span>Allow WhatsApp Voice Notes Processing</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_dynamic_pricing} onChange={(e) => setNewPlan({...newPlan, allows_dynamic_pricing: e.target.checked})} />
              <span>Allow Dynamic Off-Peak Pricing & Surge Hours</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_winback_campaigns} onChange={(e) => setNewPlan({...newPlan, allows_winback_campaigns: e.target.checked})} />
              <span>Allow Automated WhatsApp Win-Back Campaigns</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_discovery} onChange={(e) => setNewPlan({...newPlan, allows_discovery: e.target.checked})} />
              <span>Allow Business Discovery in Customer App</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_online_payments} onChange={(e) => setNewPlan({...newPlan, allows_online_payments: e.target.checked})} />
              <span>Allow Payriff & EPoint Online Gateways</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_gcal_sync} onChange={(e) => setNewPlan({...newPlan, allows_gcal_sync: e.target.checked})} />
              <span>Allow Google & Apple Calendar 2-Way Sync</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_no_show_deposits} onChange={(e) => setNewPlan({...newPlan, allows_no_show_deposits: e.target.checked})} />
              <span>Allow AI No-Show Protection & Dynamic Deposits</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_emergency_reassignment} onChange={(e) => setNewPlan({...newPlan, allows_emergency_reassignment: e.target.checked})} />
              <span>Allow Emergency Staff Replacement & Sick Leave Swaps</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_omnichannel_messaging} onChange={(e) => setNewPlan({...newPlan, allows_omnichannel_messaging: e.target.checked})} />
              <span>Allow Omnichannel IG Direct & Facebook DMs</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_growth_advisor} onChange={(e) => setNewPlan({...newPlan, allows_growth_advisor: e.target.checked})} />
              <span>Allow Weekly AI Growth & Revenue Advisor</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={newPlan.allows_custom_domain} onChange={(e) => setNewPlan({...newPlan, allows_custom_domain: e.target.checked})} />
              <span>Allow White-Label Custom CNAME Domain</span>
            </label>
          </div>

          <div className="flex-between">
            <button type="button" className="btn btn-ghost" onClick={() => setIsModalOpen(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary">Create Tier Plan</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Plans;
