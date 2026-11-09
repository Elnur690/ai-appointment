import React, { useState } from 'react';
import { useDataStore } from '../store/dataStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import StatCard from '../components/common/StatCard';
import Modal from '../components/common/Modal';
import { Users, DollarSign, Percent, Globe, Copy, Plus, CheckCircle2 } from 'lucide-react';

const Resellers = () => {
  const { resellers, createReseller, recordResellerPayout } = useDataStore();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedReseller, setSelectedReseller] = useState(null);
  const [copiedCode, setCopiedCode] = useState('');
  const [form, setForm] = useState({
    name: '',
    company_name: '',
    email: '',
    phone: '',
    referral_code: '',
    commission_rate_percent: 20,
    white_label_domain: '',
  });

  const totalPartnerMrr = resellers.reduce((acc, r) => acc + Number(r.total_mrr_generated_azn || 0), 0);
  const totalPendingPayouts = resellers.reduce((acc, r) => acc + Number(r.pending_payout_azn || 0), 0);
  const totalReferredTenants = resellers.reduce((acc, r) => acc + Number(r.active_businesses_count || 0), 0);

  const handleCopyUrl = (e, url, code) => {
    e.stopPropagation();
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url);
    }
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(''), 2000);
  };

  const handleCreateSubmit = (e) => {
    e.preventDefault();
    createReseller(form);
    setIsCreateOpen(false);
    setForm({
      name: '',
      company_name: '',
      email: '',
      phone: '',
      referral_code: '',
      commission_rate_percent: 20,
      white_label_domain: '',
    });
  };

  const columns = [
    {
      header: 'Partner / Agency',
      accessor: 'name',
      render: (row) => (
        <div>
          <div style={{ fontWeight: 600 }}>{row.name}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{row.company_name}</div>
        </div>
      ),
    },
    {
      header: 'Referral Link (randevu.vip)',
      accessor: 'referral_code',
      render: (row) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <code style={{ background: 'rgba(255,255,255,0.06)', padding: '0.2rem 0.5rem', borderRadius: '4px', color: 'var(--primary-start)' }}>
            {row.referral_code}
          </code>
          <button
            className="btn btn-ghost"
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
            onClick={(e) => handleCopyUrl(e, row.referral_url, row.referral_code)}
          >
            {copiedCode === row.referral_code ? <CheckCircle2 size={14} color="var(--success)" /> : <Copy size={14} />}
          </button>
        </div>
      ),
    },
    {
      header: 'Commission %',
      accessor: 'commission_rate_percent',
      render: (row) => <span style={{ fontWeight: 600 }}>{row.commission_rate_percent}% recurring</span>,
    },
    {
      header: 'Active Salons',
      accessor: 'active_businesses_count',
      render: (row) => `${row.active_businesses_count} / ${row.referred_businesses_count}`,
    },
    {
      header: 'Generated MRR',
      accessor: 'total_mrr_generated_azn',
      render: (row) => `${Number(row.total_mrr_generated_azn).toFixed(2)} AZN`,
    },
    {
      header: 'Pending Payout',
      accessor: 'pending_payout_azn',
      render: (row) => (
        <span style={{ color: row.pending_payout_azn > 0 ? 'var(--warning)' : 'var(--success)', fontWeight: 600 }}>
          {Number(row.pending_payout_azn).toFixed(2)} AZN
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (row) => <StatusBadge status={row.status || 'active'} />,
    },
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1>Resellers & Agency Partners</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Onboard digital agencies & regional sales partners on <strong>randevu.vip</strong> with recurring revenue share and white-label portals.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsCreateOpen(true)}>
          <Plus size={18} />
          Add Reseller Partner
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <StatCard title="Active Reseller Partners" value={resellers.length} icon={Users} trend="+2 this month" isPositive={true} />
        <StatCard title="Partner-Driven Salons" value={totalReferredTenants} icon={Globe} trend="100% attributed" isPositive={true} />
        <StatCard title="Partner-Generated MRR" value={`${totalPartnerMrr.toFixed(0)} AZN`} icon={DollarSign} trend="+24% growth" isPositive={true} />
        <StatCard title="Pending Partner Payouts" value={`${totalPendingPayouts.toFixed(2)} AZN`} icon={Percent} trend="Monthly settlement" isPositive={true} />
      </div>

      <DataTable columns={columns} data={resellers} onRowClick={(row) => setSelectedReseller(row)} />

      {/* Create Reseller Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Register New Reseller / Agency Partner">
        <form onSubmit={handleCreateSubmit}>
          <div className="form-group">
            <label className="form-label">Partner Full Name</label>
            <input type="text" className="form-control" required placeholder="e.g. Kamran Əliyev" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Agency / Company Name</label>
            <input type="text" className="form-control" placeholder="e.g. Baku Digital Agency MMC" value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input type="email" className="form-control" required placeholder="partner@agency.az" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">WhatsApp / Phone</label>
              <input type="text" className="form-control" placeholder="+994 50 000 00 00" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Referral Code</label>
              <input type="text" className="form-control" required placeholder="PARTNER-BAKU" value={form.referral_code} onChange={(e) => setForm({ ...form, referral_code: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Recurring Commission (%)</label>
              <input type="number" min="5" max="80" className="form-control" required value={form.commission_rate_percent} onChange={(e) => setForm({ ...form, commission_rate_percent: e.target.value })} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Optional Agency White-Label Domain (CNAME ➔ cname.randevu.vip)</label>
            <input type="text" className="form-control" placeholder="booking.bakudigital.az" value={form.white_label_domain} onChange={(e) => setForm({ ...form, white_label_domain: e.target.value })} />
          </div>

          <div className="flex-between" style={{ marginTop: '1.5rem' }}>
            <button type="button" className="btn btn-ghost" onClick={() => setIsCreateOpen(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary">Create Reseller Partner</button>
          </div>
        </form>
      </Modal>

      {/* Reseller Details & Payout Modal */}
      <Modal isOpen={!!selectedReseller} onClose={() => setSelectedReseller(null)} title="Reseller Portfolio & Commission Settlement">
        {selectedReseller && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <p className="form-label">Partner / Agency</p>
                <p style={{ fontWeight: 600 }}>{selectedReseller.name} ({selectedReseller.company_name})</p>
              </div>
              <div>
                <p className="form-label">Commission Share</p>
                <p style={{ fontWeight: 600, color: 'var(--primary-start)' }}>{selectedReseller.commission_rate_percent}% Recurring</p>
              </div>
              <div>
                <p className="form-label">Partner Referral Link</p>
                <p style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{selectedReseller.referral_url}</p>
              </div>
              <div>
                <p className="form-label">White-Label CNAME</p>
                <p style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{selectedReseller.white_label_domain || 'randevu.vip standard'}</p>
              </div>
            </div>

            <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1.5rem' }}>
              <div className="flex-between">
                <div>
                  <p className="form-label" style={{ marginBottom: '0.25rem' }}>Pending Commission Payout</p>
                  <p style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--warning)', margin: 0 }}>
                    {Number(selectedReseller.pending_payout_azn).toFixed(2)} AZN
                  </p>
                </div>
                {Number(selectedReseller.pending_payout_azn) > 0 && (
                  <button
                    className="btn btn-primary"
                    onClick={() => {
                      recordResellerPayout(selectedReseller.id, selectedReseller.pending_payout_azn);
                      setSelectedReseller(null);
                    }}
                  >
                    Mark Payout Settled
                  </button>
                )}
              </div>
            </div>

            <div className="flex-between">
              <button className="btn btn-ghost" onClick={() => setSelectedReseller(null)}>Close</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Resellers;
