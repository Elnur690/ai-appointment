import React, { useState, useEffect } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import Modal from '../components/common/Modal';
import { Globe, Clock } from 'lucide-react';

const TRIAL_FEATURE_OPTIONS = [
  { key: 'allows_instagram', az: 'Instagram Direct AI', en: 'Instagram Direct AI' },
  { key: 'allows_telegram', az: 'Telegram Bot AI', en: 'Telegram Bot AI' },
  { key: 'allows_voice_messages', az: 'WhatsApp Səsli Mesajlar', en: 'WhatsApp Voice Notes' },
  { key: 'allows_online_payments', az: 'Onlayn Ödənişlər (Payriff & Paymegate)', en: 'Online Gateways (Payriff & Paymegate)' },
  { key: 'allows_no_show_deposits', az: 'No-Show Depozit Qorunması', en: 'No-Show Deposit Protection' },
  { key: 'allows_shift_management', az: 'Növbəli İş Qrafiki (Overtime)', en: 'Shift & Overtime Scheduling' },
  { key: 'allows_cadence_engine', az: 'Avtomatik Təkrar Randevu (Cadence)', en: 'Predictive Cadence Rebooking' },
  { key: 'allows_flash_drops', az: 'Son Dəqiqə Endirimləri (Flash Drops)', en: 'Last-Minute Flash Drops' },
  { key: 'allows_gift_vouchers', az: 'Rəqəmsal Hədiyyə Kartları', en: 'Digital Gift Vouchers' },
  { key: 'allows_loyalty_program', az: 'VIP Loyallıq Proqramı', en: 'VIP Loyalty Program' },
  { key: 'allows_custom_domain', az: 'Şəxsi Domen (White-Label CNAME)', en: 'White-Label Custom CNAME Domain' },
];

const Businesses = () => {
  const { businesses, plans, fetchBusinesses, fetchPlans, updateBusinessStatus } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [customDomainInput, setCustomDomainInput] = useState('');
  const [selectedPlanInput, setSelectedPlanInput] = useState('');
  const [trialDaysInput, setTrialDaysInput] = useState(14);
  const [trialFeaturesOverride, setTrialFeaturesOverride] = useState({});
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchBusinesses();
    fetchPlans();
  }, [fetchBusinesses, fetchPlans]);

  const handleRowClick = (row) => {
    setSelectedBusiness(row);
    setCustomDomainInput(row.customDomain || '');
    setSelectedPlanInput(row.plan || (plans[0]?.name ?? ''));
    setTrialDaysInput(row.trialDaysRemaining || 14);
    setTrialFeaturesOverride(row.trialFeaturesOverride || {});
  };

  const toggleOverrideFeature = (key) => {
    setTrialFeaturesOverride((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const filteredBusinesses = businesses.filter(
    (b) =>
      b.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.owner?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const columns = [
    {
      header: isAz ? 'Biznes Adı' : 'Business Name',
      accessor: 'name',
      render: (row) => <span style={{ fontWeight: 500 }}>{row.name}</span>,
    },
    { header: isAz ? 'Sahibkar' : 'Owner', accessor: 'owner' },
    { header: isAz ? 'Paket' : 'Plan', accessor: 'plan' },
    {
      header: isAz ? 'Pulsuz Sınaq (Trial)' : 'Free Trial',
      accessor: 'trialDaysRemaining',
      render: (row) =>
        row.status === 'trial' ? (
          <span style={{ color: 'var(--primary-start)', fontWeight: 600 }}>
            {row.trialDaysRemaining} {isAz ? 'gün qalıb' : 'days left'}
          </span>
        ) : (
          <span style={{ color: 'var(--text-secondary)' }}>—</span>
        ),
    },
    {
      header: isAz ? 'Şəxsi Domen (White-Label)' : 'White-Label Domain',
      accessor: 'customDomain',
      render: (row) => (
        <span style={{ fontFamily: 'monospace', color: 'var(--primary-start)' }}>
          {row.customDomain || (isAz ? 'Standart Subdomen' : 'Standard Subdomain')}
        </span>
      ),
    },
    { header: isAz ? 'Filiallar' : 'Branches', accessor: 'branches' },
    { header: isAz ? 'Status' : 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>{isAz ? 'Qeydiyyatdan Keçmiş Bizneslər və Pulsuz Sınaq İdarəetməsi' : 'Tenant Businesses & Dynamic Free Trial'}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz
              ? 'Biznes hesablarını, fərdi Pulsuz Sınaq (Free Trial) müddətini və xüsusiyyətlərini, şəxsi domenləri və paketləri idarə edin.'
              : 'Manage business tenants, dynamic Free Trial duration & features, white-label domains, and subscription plans.'}
          </p>
        </div>
        <div className="flex-center" style={{ gap: '1rem' }}>
          <input
            type="text"
            className="form-control"
            placeholder={isAz ? 'Biznes axtar...' : 'Search businesses...'}
            style={{ width: '250px' }}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <DataTable columns={columns} data={filteredBusinesses} onRowClick={handleRowClick} />

      <Modal
        isOpen={!!selectedBusiness}
        onClose={() => setSelectedBusiness(null)}
        title={isAz ? 'Biznesi, Pulsuz Sınağı və Domeni İdarə Et' : 'Manage Business, Dynamic Free Trial & Domain'}
      >
        {selectedBusiness && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <p className="form-label">{isAz ? 'Biznes Adı' : 'Business Name'}</p>
                <p style={{ fontWeight: 600 }}>{selectedBusiness.name}</p>
              </div>
              <div>
                <p className="form-label">{isAz ? 'Sahibkar Əlaqə' : 'Owner Contact'}</p>
                <p>{selectedBusiness.owner}</p>
              </div>
              <div>
                <p className="form-label">{isAz ? 'Cari Status' : 'Current Status'}</p>
                <StatusBadge status={selectedBusiness.status} />
              </div>
              <div>
                <p className="form-label">{isAz ? 'Aktiv Paket' : 'Active Plan'}</p>
                <select
                  className="form-control"
                  value={selectedPlanInput}
                  onChange={(e) => setSelectedPlanInput(e.target.value)}
                >
                  {plans.map((p) => (
                    <option key={p.id} value={p.name}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Dynamic Free Trial Duration & Features Section */}
            <div
              style={{
                padding: '1rem',
                background: 'rgba(6, 182, 212, 0.08)',
                borderRadius: '8px',
                border: '1px solid rgba(6, 182, 212, 0.3)',
                marginBottom: '1.25rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Clock size={18} color="var(--primary-start)" />
                  <span style={{ fontWeight: 600 }}>
                    {isAz ? 'Dinamik Pulsuz Sınaq (Free Trial) Tənzimləməsi' : 'Dynamic Free Trial Duration & Features'}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem' }}>{isAz ? 'Sınaq Günləri:' : 'Trial Days:'}</span>
                  <input
                    type="number"
                    min="0"
                    max="365"
                    className="form-control"
                    style={{ width: '85px', padding: '0.3rem 0.5rem' }}
                    value={trialDaysInput}
                    onChange={(e) => setTrialDaysInput(Number(e.target.value))}
                  />
                </div>
              </div>
              <div style={{ maxHeight: '130px', overflowY: 'auto', fontSize: '0.82rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
                {TRIAL_FEATURE_OPTIONS.map((opt) => (
                  <label key={opt.key} style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={Boolean(trialFeaturesOverride[opt.key])}
                      onChange={() => toggleOverrideFeature(opt.key)}
                    />
                    <span>{isAz ? opt.az : opt.en}</span>
                  </label>
                ))}
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
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Globe size={18} color="var(--primary-start)" />
                <span style={{ fontWeight: 600 }}>
                  {isAz ? 'Şəxsi CNAME Domen Təyin Et' : 'Assign White-Label Custom CNAME Domain'}
                </span>
              </div>
              <div className="flex-between" style={{ gap: '0.5rem' }}>
                <input
                  type="text"
                  className="form-control"
                  placeholder="booking.yourdomain.az"
                  value={customDomainInput}
                  onChange={(e) => setCustomDomainInput(e.target.value)}
                />
              </div>
            </div>

            <div className="flex-between" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
              {selectedBusiness.status !== 'active' ? (
                <button
                  className="btn btn-primary"
                  onClick={async () => {
                    await updateBusinessStatus(selectedBusiness.id, 'active', {
                      custom_domain: customDomainInput,
                      plan: selectedPlanInput,
                      trial_days: Number(trialDaysInput),
                      trial_features_override: trialFeaturesOverride,
                    });
                    setSelectedBusiness(null);
                  }}
                >
                  {isAz ? 'Təsdiqlə və Aktivləşdir' : 'Approve & Activate'}
                </button>
              ) : (
                <button
                  className="btn btn-secondary"
                  onClick={async () => {
                    await updateBusinessStatus(selectedBusiness.id, 'suspended');
                    setSelectedBusiness(null);
                  }}
                  style={{ color: 'var(--error)' }}
                >
                  {isAz ? 'Biznesi Dayandır' : 'Suspend Tenant'}
                </button>
              )}
              <button
                className="btn btn-primary"
                onClick={async () => {
                  await updateBusinessStatus(selectedBusiness.id, selectedBusiness.status, {
                    custom_domain: customDomainInput,
                    plan: selectedPlanInput,
                    trial_days: Number(trialDaysInput),
                    trial_features_override: trialFeaturesOverride,
                  });
                  setSelectedBusiness(null);
                }}
              >
                {isAz ? 'Dəyişiklikləri Yadda Saxla' : 'Save Tenant & Trial Setup'}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Businesses;
