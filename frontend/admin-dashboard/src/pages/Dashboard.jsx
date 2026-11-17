import React, { useEffect } from 'react';
import StatCard from '../components/common/StatCard';
import { Building2, CreditCard, DollarSign, MessageSquare } from 'lucide-react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';

const Dashboard = () => {
  const { analytics, businesses, fetchAnalytics, fetchBusinesses } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';

  useEffect(() => {
    fetchAnalytics();
    fetchBusinesses();
  }, [fetchAnalytics, fetchBusinesses]);

  const recentColumns = [
    {
      header: isAz ? 'Biznes Adı' : 'Business Name',
      accessor: 'name',
      render: (row) => <span style={{ fontWeight: 500 }}>{row.name}</span>,
    },
    { header: isAz ? 'Sahibkar' : 'Owner', accessor: 'owner' },
    { header: isAz ? 'Paket' : 'Plan', accessor: 'plan' },
    { header: isAz ? 'Status' : 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: isAz ? 'Qeydiyyat Tarixi' : 'Created', accessor: 'created' },
  ];

  return (
    <div className="page-container">
      <h1 style={{ marginBottom: '2rem' }}>{isAz ? 'Platforma Xülasəsi' : 'Platform Overview'}</h1>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem',
        }}
      >
        <StatCard
          title={isAz ? 'Ümumi Bizneslər' : 'Total Businesses'}
          value={Number(analytics?.total_businesses || 0).toLocaleString()}
          icon={Building2}
          trend="up"
          trendValue={isAz ? 'Qeydiyyatdan keçmiş bizneslər' : 'Registered tenants'}
        />
        <StatCard
          title={isAz ? 'Aktiv Abunəliklər' : 'Active Subscriptions'}
          value={Number(analytics?.active_subscriptions || 0).toLocaleString()}
          icon={CreditCard}
          trend="up"
          trendValue={isAz ? 'Aktiv ödənişli hesablar' : 'Active billing accounts'}
        />
        <StatCard
          title={isAz ? 'Aylıq Təkrarlanan Gəlir (MRR)' : 'Monthly Recurring Revenue'}
          value={`${Number(analytics?.mrr_usd || 0).toLocaleString()} AZN`}
          icon={DollarSign}
          trend="up"
          trendValue={isAz ? 'Cari aktiv MRR' : 'Current active MRR'}
        />
        <StatCard
          title={isAz ? 'Müştəri Mesajları' : 'Customer Conversations'}
          value={Number(analytics?.total_messages_this_month || 0).toLocaleString()}
          icon={MessageSquare}
          trend="up"
          trendValue={isAz ? 'Ümumi AI yazışmaları' : 'Total AI conversations'}
        />
      </div>

      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ marginBottom: '1.25rem', color: 'var(--text-secondary)' }}>
          {isAz ? 'Son Qeydiyyatdan Keçmiş Bizneslər' : 'Recently Onboarded Businesses'}
        </h3>
        {businesses.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', padding: '1rem 0', margin: 0 }}>
            {isAz
              ? 'Hələ qeydiyyatdan keçmiş biznes yoxdur. randevu.vip üzərindən yeni qeydiyyatlar avtomatik burada görünəcək.'
              : 'No businesses registered yet. New registrations on randevu.vip will appear here automatically.'}
          </p>
        ) : (
          <DataTable columns={recentColumns} data={businesses.slice(0, 10)} />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
