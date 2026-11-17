import React, { useState, useEffect } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import Modal from '../components/common/Modal';
import { Globe } from 'lucide-react';

const Businesses = () => {
  const { businesses, plans, fetchBusinesses, fetchPlans, updateBusinessStatus } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [customDomainInput, setCustomDomainInput] = useState('');
  const [selectedPlanInput, setSelectedPlanInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchBusinesses();
    fetchPlans();
  }, [fetchBusinesses, fetchPlans]);

  const handleRowClick = (row) => {
    setSelectedBusiness(row);
    setCustomDomainInput(row.customDomain || '');
    setSelectedPlanInput(row.plan || (plans[0]?.name ?? ''));
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
          <h1>{isAz ? 'Qeydiyyatdan Keçmiş Bizneslər' : 'Tenant Businesses'}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz
              ? 'Biznes hesablarını, şəxsi domen (CNAME) təyinatlarını və abunəlik paketlərini idarə edin.'
              : 'Manage business tenants, white-label custom domain assignments, and subscription plans.'}
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
        title={isAz ? 'Biznesi və Şəxsi Domeni İdarə Et' : 'Manage Business Tenant & White-Label Setup'}
      >
        {selectedBusiness && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
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
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                {isAz
                  ? 'Fərdi brendləşdirilmiş randevu portalını (`booking.mysalon.az`) aktivləşdirir.'
                  : 'Enables custom branded booking portal (`booking.mysalon.az`).'}
              </p>
              <div className="flex-between" style={{ gap: '0.5rem' }}>
                <input
                  type="text"
                  className="form-control"
                  placeholder="booking.yourdomain.az"
                  value={customDomainInput}
                  onChange={(e) => setCustomDomainInput(e.target.value)}
                />
                <button
                  className="btn btn-secondary"
                  onClick={async () => {
                    await updateBusinessStatus(selectedBusiness.id, selectedBusiness.status, {
                      custom_domain: customDomainInput,
                      plan: selectedPlanInput,
                    });
                    setSelectedBusiness(null);
                  }}
                >
                  {isAz ? 'Təsdiqlə' : 'Verify & Assign'}
                </button>
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
                  });
                  setSelectedBusiness(null);
                }}
              >
                {isAz ? 'Dəyişiklikləri Yadda Saxla' : 'Save Tenant Setup'}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Businesses;
