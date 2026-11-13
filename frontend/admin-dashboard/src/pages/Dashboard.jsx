import React, { useEffect } from 'react';
import StatCard from '../components/common/StatCard';
import { Building2, CreditCard, DollarSign, MessageSquare } from 'lucide-react';
import { useDataStore } from '../store/dataStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';

const Dashboard = () => {
  const { analytics, businesses, fetchAnalytics, fetchBusinesses } = useDataStore();

  useEffect(() => {
    fetchAnalytics();
    fetchBusinesses();
  }, [fetchAnalytics, fetchBusinesses]);

  const recentColumns = [
    { header: 'Business Name', accessor: 'name', render: (row) => <span style={{ fontWeight: 500 }}>{row.name}</span> },
    { header: 'Owner', accessor: 'owner' },
    { header: 'Plan', accessor: 'plan' },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: 'Created', accessor: 'created' },
  ];

  return (
    <div className="page-container">
      <h1 style={{ marginBottom: '2rem' }}>Platform Overview</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <StatCard
          title="Total Businesses"
          value={Number(analytics?.total_businesses || 0).toLocaleString()}
          icon={Building2}
          trend="up"
          trendValue="Registered tenants"
        />
        <StatCard
          title="Active Subscriptions"
          value={Number(analytics?.active_subscriptions || 0).toLocaleString()}
          icon={CreditCard}
          trend="up"
          trendValue="Active billing accounts"
        />
        <StatCard
          title="Monthly Recurring Revenue"
          value={`${Number(analytics?.mrr_usd || 0).toLocaleString()} AZN`}
          icon={DollarSign}
          trend="up"
          trendValue="Current active MRR"
        />
        <StatCard
          title="Customer Conversations"
          value={Number(analytics?.total_messages_this_month || 0).toLocaleString()}
          icon={MessageSquare}
          trend="up"
          trendValue="Total AI conversations"
        />
      </div>

      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)' }}>Recently Onboarded Businesses</h3>
        {businesses.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', padding: '1rem 0', margin: 0 }}>
            No businesses registered yet. New registrations on randevu.vip will appear here automatically.
          </p>
        ) : (
          <DataTable columns={recentColumns} data={businesses.slice(0, 10)} />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
