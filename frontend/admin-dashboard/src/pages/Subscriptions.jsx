import React from 'react';
import { useDataStore } from '../store/dataStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';

const Subscriptions = () => {
  const { subscriptions } = useDataStore();

  const columns = [
    { header: 'Business', accessor: 'business', render: (row) => <span style={{ fontWeight: 500 }}>{row.business}</span> },
    { header: 'Plan', accessor: 'plan' },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: 'Billing Period', accessor: 'period' },
    { header: 'Messages Used', accessor: 'messagesUsed' },
    { header: 'Actions', accessor: 'id', render: () => (
      <button className="btn btn-ghost" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>Manage</button>
    )}
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h1>Subscriptions Overview</h1>
      </div>

      <DataTable columns={columns} data={subscriptions} />
    </div>
  );
};

export default Subscriptions;
