import React, { useState, useEffect } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import StatCard from '../components/common/StatCard';
import Modal from '../components/common/Modal';
import { Users, DollarSign, Percent, Globe, Copy, Plus, CheckCircle2 } from 'lucide-react';

const Resellers = () => {
  const { resellers, fetchResellers, createReseller, updateResellerStatus, recordResellerPayout } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createError, setCreateError] = useState('');
  const [createSubmitting, setCreateSubmitting] = useState(false);
  const [selectedReseller, setSelectedReseller] = useState(null);
  const [copiedCode, setCopiedCode] = useState('');

  useEffect(() => {
    fetchResellers();
  }, [fetchResellers]);

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

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setCreateError('');
    setCreateSubmitting(true);
    try {
      await createReseller(form);
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
    } catch (err) {
      setCreateError(
        err.response?.data?.detail ||
          err.message ||
          (isAz ? 'Partnyor yaradıla bilmədi.' : 'Could not create reseller.')
      );
    } finally {
      setCreateSubmitting(false);
    }
  };

  const columns = [
    {
      header: isAz ? 'Partnyor / Agentlik' : 'Partner / Agency',
      accessor: 'name',
      render: (row) => (
        <div>
          <div style={{ fontWeight: 600 }}>{row.name}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{row.company_name}</div>
        </div>
      ),
    },
    {
      header: isAz ? 'Referal Link (randevu.vip)' : 'Referral Link (randevu.vip)',
      accessor: 'referral_code',
      render: (row) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <code
            style={{
              background: 'rgba(255,255,255,0.06)',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              color: 'var(--primary-start)',
            }}
          >
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
      header: isAz ? 'Komissiya %' : 'Commission %',
      accessor: 'commission_rate_percent',
      render: (row) => <span style={{ fontWeight: 600 }}>{row.commission_rate_percent}%</span>,
    },
    {
      header: isAz ? 'Aktiv Salonlar' : 'Active Salons',
      accessor: 'active_businesses_count',
      render: (row) => `${row.active_businesses_count} / ${row.referred_businesses_count}`,
    },
    {
      header: isAz ? 'Yaradılan MRR' : 'Generated MRR',
      accessor: 'total_mrr_generated_azn',
      render: (row) => `${Number(row.total_mrr_generated_azn).toFixed(2)} AZN`,
    },
    {
      header: isAz ? 'Gözləyən Ödəniş' : 'Pending Payout',
      accessor: 'pending_payout_azn',
      render: (row) => (
        <span style={{ color: row.pending_payout_azn > 0 ? 'var(--warning)' : 'var(--success)', fontWeight: 600 }}>
          {Number(row.pending_payout_azn).toFixed(2)} AZN
        </span>
      ),
    },
    {
      header: isAz ? 'Status' : 'Status',
      accessor: 'is_active',
      render: (row) => <StatusBadge status={row.is_active ? 'active' : 'pending'} />,
    },
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>{isAz ? 'Partnyorlar və Satış Agentlikləri (Resellers)' : 'Resellers & Agency Partners'}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz ? (
              <>
                <strong>randevu.vip</strong> üzərində rəqəmsal agentlikləri və regional satış partnyorlarını davamlı komissiya ilə qoşun.
              </>
            ) : (
              <>
                Onboard digital agencies & regional sales partners on <strong>randevu.vip</strong> with recurring revenue share and white-label portals.
              </>
            )}
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => {
            setCreateError('');
            setIsCreateOpen(true);
          }}
        >
          <Plus size={18} />
          {isAz ? 'Yeni Partnyor Əlavə Et' : 'Add Reseller Partner'}
        </button>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        <StatCard
          title={isAz ? 'Aktiv Partnyorlar' : 'Active Reseller Partners'}
          value={resellers.length}
          icon={Users}
        />
        <StatCard
          title={isAz ? 'Partnyor Salonları' : 'Partner-Driven Salons'}
          value={totalReferredTenants}
          icon={Globe}
        />
        <StatCard
          title={isAz ? 'Partnyor MRR Gəliri' : 'Partner-Generated MRR'}
          value={`${totalPartnerMrr.toFixed(0)} AZN`}
          icon={DollarSign}
        />
        <StatCard
          title={isAz ? 'Gözləyən Komissiya' : 'Pending Partner Payouts'}
          value={`${totalPendingPayouts.toFixed(2)} AZN`}
          icon={Percent}
        />
      </div>

      <DataTable columns={columns} data={resellers} onRowClick={(row) => setSelectedReseller(row)} />

      {/* Create Reseller Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => {
          setCreateError('');
          setIsCreateOpen(false);
        }}
        title={isAz ? 'Yeni Partnyor / Agentlik Qeydiyyatı' : 'Register New Reseller / Agency Partner'}
      >
        <form onSubmit={handleCreateSubmit}>
          {createError && (
            <div
              style={{
                padding: '0.65rem 0.9rem',
                background: 'rgba(239, 68, 68, 0.14)',
                border: '1px solid var(--error)',
                borderRadius: '8px',
                color: '#fca5a5',
                fontSize: '0.85rem',
                marginBottom: '1rem',
              }}
            >
              {createError}
            </div>
          )}
          <div className="form-group">
            <label className="form-label">{isAz ? 'Partnyorun Adı və Soyadı' : 'Partner Full Name'}</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="məs: Kamran Əliyev"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Agentlik / Şirkət Adı' : 'Agency / Company Name'}</label>
            <input
              type="text"
              className="form-control"
              placeholder="məs: Baku Digital Agency MMC"
              value={form.company_name}
              onChange={(e) => setForm({ ...form, company_name: e.target.value })}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">{isAz ? 'E-poçt Ünvanı' : 'Email Address'}</label>
              <input
                type="email"
                className="form-control"
                required
                placeholder="partner@agency.az"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">{isAz ? 'WhatsApp / Telefon' : 'WhatsApp / Phone'}</label>
              <input
                type="text"
                className="form-control"
                placeholder="+994 50 000 00 00"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">{isAz ? 'Referal Kodu' : 'Referral Code'}</label>
              <input
                type="text"
                className="form-control"
                required
                placeholder="PARTNER-BAKU"
                value={form.referral_code}
                onChange={(e) => setForm({ ...form, referral_code: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">{isAz ? 'Davamlı Komissiya (%)' : 'Recurring Commission (%)'}</label>
              <input
                type="number"
                min="5"
                max="80"
                className="form-control"
                required
                value={form.commission_rate_percent}
                onChange={(e) => setForm({ ...form, commission_rate_percent: e.target.value })}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">
              {isAz
                ? 'İstəyə Bağlı Agentlik Domeni (CNAME ➔ cname.randevu.vip)'
                : 'Optional Agency White-Label Domain (CNAME ➔ cname.randevu.vip)'}
            </label>
            <input
              type="text"
              className="form-control"
              placeholder="booking.bakudigital.az"
              value={form.white_label_domain}
              onChange={(e) => setForm({ ...form, white_label_domain: e.target.value })}
            />
          </div>

          <div className="flex-between" style={{ marginTop: '1.5rem' }}>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => {
                setCreateError('');
                setIsCreateOpen(false);
              }}
            >
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary" disabled={createSubmitting}>
              {createSubmitting
                ? isAz
                  ? 'Yaradılır...'
                  : 'Creating...'
                : isAz
                ? 'Partnyoru Yarat'
                : 'Create Reseller Partner'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Reseller Details & Payout Modal */}
      <Modal
        isOpen={!!selectedReseller}
        onClose={() => setSelectedReseller(null)}
        title={isAz ? 'Partnyor Portfeli və Komissiya Ödənişi' : 'Reseller Portfolio & Commission Settlement'}
      >
        {selectedReseller && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <p className="form-label">{isAz ? 'Partnyor / Agentlik' : 'Partner / Agency'}</p>
                <p style={{ fontWeight: 600 }}>
                  {selectedReseller.name} ({selectedReseller.company_name})
                </p>
              </div>
              <div>
                <p className="form-label">{isAz ? 'Komissiya Payı' : 'Commission Share'}</p>
                <p style={{ fontWeight: 600, color: 'var(--primary-start)' }}>
                  {selectedReseller.commission_rate_percent}%
                </p>
              </div>
              <div>
                <p className="form-label">{isAz ? 'Referal Linki' : 'Partner Referral Link'}</p>
                <p style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{selectedReseller.referral_url}</p>
              </div>
              <div>
                <p className="form-label">White-Label CNAME</p>
                <p style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                  {selectedReseller.white_label_domain || 'randevu.vip standard'}
                </p>
              </div>
            </div>

            <div
              style={{
                padding: '1rem',
                background: 'rgba(255,255,255,0.03)',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                marginBottom: '1.5rem',
              }}
            >
              <div className="flex-between">
                <div>
                  <p className="form-label" style={{ marginBottom: '0.25rem' }}>
                    {isAz ? 'Gözləyən Komissiya Məbləği' : 'Pending Commission Payout'}
                  </p>
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
                    {isAz ? 'Ödənişi Təsdiqlə' : 'Mark Payout Settled'}
                  </button>
                )}
              </div>
            </div>

            <div className="flex-between">
              <button className="btn btn-ghost" onClick={() => setSelectedReseller(null)}>
                {isAz ? 'Bağla' : 'Close'}
              </button>
              {!selectedReseller.is_active ? (
                <button
                  className="btn btn-primary"
                  onClick={async () => {
                    await updateResellerStatus(selectedReseller.id, true);
                    setSelectedReseller(null);
                  }}
                >
                  {isAz ? 'Partnyoru Təsdiqlə və Aktivləşdir' : 'Approve & Activate Partner'}
                </button>
              ) : (
                <button
                  className="btn btn-secondary"
                  style={{ color: 'var(--error)' }}
                  onClick={async () => {
                    await updateResellerStatus(selectedReseller.id, false);
                    setSelectedReseller(null);
                  }}
                >
                  {isAz ? 'Partnyoru Dayandır' : 'Suspend Partner'}
                </button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Resellers;
