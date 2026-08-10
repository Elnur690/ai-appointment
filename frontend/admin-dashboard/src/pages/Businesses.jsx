import React, { useState } from 'react';
import { useDataStore } from '../store/dataStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import Modal from '../components/common/Modal';
import { Globe, Shield, Bot, CheckCircle } from 'lucide-react';

const Businesses = () => {
  const { businesses, plans, updateBusinessStatus } = useDataStore();
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [customDomainInput, setCustomDomainInput] = useState('');
  const [selectedPlanInput, setSelectedPlanInput] = useState('');

  const handleRowClick = (row) => {
    setSelectedBusiness(row);
    setCustomDomainInput(row.customDomain || 'booking.mysalon.az');
    setSelectedPlanInput(row.plan || 'Enterprise Tier');
  };

  const columns = [
    { header: 'Business Name', accessor: 'name', render: (row) => <span style={{ fontWeight: 500 }}>{row.name}</span> },
    { header: 'Owner', accessor: 'owner' },
    { header: 'Plan', accessor: 'plan' },
    { header: 'White-Label Domain', accessor: 'customDomain', render: (row) => <span style={{ fontFamily: 'monospace', color: 'var(--primary-start)' }}>{row.customDomain || 'Standard Subdomain'}</span> },
    { header: 'Branches', accessor: 'branches' },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1>Tenant Businesses</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage business tenants, white-label custom domain assignments, and subscription plans.</p>
        </div>
        <div className="flex-center" style={{ gap: '1rem' }}>
          <input type="text" className="form-control" placeholder="Search businesses..." style={{ width: '250px' }} />
        </div>
      </div>

      <DataTable 
        columns={columns} 
        data={businesses} 
        onRowClick={handleRowClick} 
      />

      <Modal isOpen={!!selectedBusiness} onClose={() => setSelectedBusiness(null)} title="Manage Business Tenant & White-Label Setup">
        {selectedBusiness && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
              <div>
                <p className="form-label">Business Name</p>
                <p style={{ fontWeight: 600 }}>{selectedBusiness.name}</p>
              </div>
              <div>
                <p className="form-label">Owner Contact</p>
                <p>{selectedBusiness.owner}</p>
              </div>
              <div>
                <p className="form-label">Current Status</p>
                <StatusBadge status={selectedBusiness.status} />
              </div>
              <div>
                <p className="form-label">Active Plan</p>
                <select className="form-control" value={selectedPlanInput} onChange={(e) => setSelectedPlanInput(e.target.value)}>
                  {plans.map(p => <option key={p.id} value={p.name}>{p.name}</option>)}
                </select>
              </div>
            </div>

            {/* White-Label Domain Assignment Section */}
            <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Globe size={18} color="var(--primary-start)" />
                <span style={{ fontWeight: 600 }}>Assign White-Label Custom CNAME Domain</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                Enables custom branded booking portal (`booking.mysalon.az`). Requires Enterprise Plan (`allows_custom_domain`).
              </p>
              <div className="flex-between" style={{ gap: '0.5rem' }}>
                <input type="text" className="form-control" placeholder="booking.mysalon.az" value={customDomainInput} onChange={(e) => setCustomDomainInput(e.target.value)} />
                <button className="btn btn-secondary" onClick={() => alert(`White-label domain '${customDomainInput}' verified and assigned!`)}>Verify & Assign</button>
              </div>
            </div>

            <div className="flex-between" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
              {selectedBusiness.status !== 'active' ? (
                <button className="btn btn-primary" onClick={() => {
                  updateBusinessStatus(selectedBusiness.id, 'active');
                  setSelectedBusiness(null);
                }}>Approve & Activate</button>
              ) : (
                <button className="btn btn-secondary" onClick={() => {
                  updateBusinessStatus(selectedBusiness.id, 'suspended');
                  setSelectedBusiness(null);
                }} style={{ color: 'var(--error)' }}>Suspend Tenant</button>
              )}
              <button className="btn btn-primary" onClick={() => {
                alert("Tenant settings saved successfully!");
                setSelectedBusiness(null);
              }}>Save Tenant Setup</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Businesses;
