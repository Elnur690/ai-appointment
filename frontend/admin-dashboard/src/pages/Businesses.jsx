import React, { useState } from 'react';
import { useDataStore } from '../store/dataStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';
import Modal from '../components/common/Modal';

const Businesses = () => {
  const { businesses, updateBusinessStatus } = useDataStore();
  const [selectedBusiness, setSelectedBusiness] = useState(null);

  const columns = [
    { header: 'Business Name', accessor: 'name', render: (row) => <span style={{ fontWeight: 500 }}>{row.name}</span> },
    { header: 'Owner', accessor: 'owner' },
    { header: 'Plan', accessor: 'plan' },
    { header: 'Branches', accessor: 'branches' },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: 'Created', accessor: 'created' },
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h1>Businesses</h1>
        <div className="flex-center" style={{ gap: '1rem' }}>
          <input type="text" className="form-control" placeholder="Search businesses..." style={{ width: '250px' }} />
        </div>
      </div>

      <DataTable 
        columns={columns} 
        data={businesses} 
        onRowClick={(row) => setSelectedBusiness(row)} 
      />

      <Modal isOpen={!!selectedBusiness} onClose={() => setSelectedBusiness(null)} title="Business Details">
        {selectedBusiness && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
              <div>
                <p className="form-label">Name</p>
                <p>{selectedBusiness.name}</p>
              </div>
              <div>
                <p className="form-label">Owner</p>
                <p>{selectedBusiness.owner}</p>
              </div>
              <div>
                <p className="form-label">Status</p>
                <StatusBadge status={selectedBusiness.status} />
              </div>
              <div>
                <p className="form-label">Plan</p>
                <p>{selectedBusiness.plan}</p>
              </div>
            </div>
            
            <div className="flex-between" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
              {selectedBusiness.status !== 'active' ? (
                <button className="btn btn-primary" onClick={() => {
                  updateBusinessStatus(selectedBusiness.id, 'active');
                  setSelectedBusiness(null);
                }}>Approve / Activate</button>
              ) : (
                <button className="btn btn-secondary" onClick={() => {
                  updateBusinessStatus(selectedBusiness.id, 'suspended');
                  setSelectedBusiness(null);
                }} style={{ color: 'var(--error)' }}>Suspend Account</button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Businesses;
