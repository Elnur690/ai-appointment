import React, { useEffect } from 'react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';

const Subscriptions = () => {
  const { subscriptions, fetchSubscriptions } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';

  useEffect(() => {
    fetchSubscriptions();
  }, [fetchSubscriptions]);

  const columns = [
    {
      header: isAz ? 'Biznes' : 'Business',
      accessor: 'business',
      render: (row) => <span style={{ fontWeight: 500 }}>{row.business}</span>,
    },
    { header: isAz ? 'Paket' : 'Plan', accessor: 'plan' },
    { header: isAz ? 'Status' : 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: isAz ? 'Ödəniş Dövrü' : 'Billing Period', accessor: 'period' },
    { header: isAz ? 'İstifadə Edilən Mesajlar' : 'Messages Used', accessor: 'messagesUsed' },
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h1>{isAz ? 'Abunəliklər Xülasəsi' : 'Subscriptions Overview'}</h1>
      </div>

      <DataTable columns={columns} data={subscriptions} />
    </div>
  );
};

export default Subscriptions;
