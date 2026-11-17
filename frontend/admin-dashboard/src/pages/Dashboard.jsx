import React, { useEffect } from 'react';
import StatCard from '../components/common/StatCard';
import {
  Building2,
  CreditCard,
  DollarSign,
  MessageSquare,
  Cpu,
  Calendar,
  TrendingUp,
  Users,
  RefreshCw,
} from 'lucide-react';
import { useDataStore } from '../store/dataStore';
import { useAuthStore } from '../store/authStore';
import DataTable from '../components/common/DataTable';
import StatusBadge from '../components/common/StatusBadge';

const Dashboard = () => {
  const { analytics, fetchAnalytics, fetchBusinesses } = useDataStore();
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';

  useEffect(() => {
    fetchAnalytics();
    fetchBusinesses();
  }, [fetchAnalytics, fetchBusinesses]);

  const spendRows = analytics?.ai_spend_per_business || [];

  const aiSpendColumns = [
    {
      header: isAz ? 'Biznes / Sahibkar' : 'Business / Owner',
      accessor: 'business_name',
      render: (row) => (
        <div>
          <div style={{ fontWeight: 600 }}>{row.business_name}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{row.owner_email}</div>
        </div>
      ),
    },
    {
      header: isAz ? 'Paket / Sınaq' : 'Plan / Trial',
      accessor: 'plan_name',
      render: (row) => (
        <div>
          <div style={{ fontWeight: 600 }}>{row.plan_name} ({row.plan_price_azn} AZN)</div>
          {row.status === 'trial' && (
            <div style={{ fontSize: '0.75rem', color: 'var(--primary-start)' }}>
              {isAz ? `Sınaq: ${row.trial_days_remaining} gün qalıb` : `Trial: ${row.trial_days_remaining}d left`}
            </div>
          )}
        </div>
      ),
    },
    {
      header: isAz ? 'AI Model Mühərriki' : 'AI Model Engine',
      accessor: 'assigned_model',
      render: (row) => (
        <code style={{ fontSize: '0.8rem', color: 'var(--primary-start)' }}>{row.assigned_model}</code>
      ),
    },
    {
      header: isAz ? 'Mesajlar (Gələn / AI Cavab)' : 'Messages (In / AI Out)',
      accessor: 'total_messages',
      render: (row) => (
        <span>
          <strong>{row.total_messages}</strong> ({row.inbound_messages} / {row.ai_replies})
        </span>
      ),
    },
    {
      header: isAz ? 'İstifadə Edilən Tokenlər' : 'Tokens Used',
      accessor: 'tokens_used',
      render: (row) => Number(row.tokens_used || 0).toLocaleString(),
    },
    {
      header: isAz ? 'AI Xərci (USD / AZN)' : 'AI Spend (USD / AZN)',
      accessor: 'ai_spend_azn',
      render: (row) => (
        <div>
          <div style={{ fontWeight: 700, color: 'var(--warning)' }}>
            ${Number(row.ai_spend_usd || 0).toFixed(4)} USD
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            {Number(row.ai_spend_azn || 0).toFixed(4)} AZN
          </div>
        </div>
      ),
    },
    {
      header: isAz ? 'Randevular / Dövriyyə' : 'Bookings / Venue Rev',
      accessor: 'appointments_count',
      render: (row) => (
        <span>
          {row.appointments_count} • {Number(row.revenue_azn || 0).toFixed(2)} AZN
        </span>
      ),
    },
    {
      header: isAz ? 'Xalis Mənfəət (Net Margin)' : 'Net Margin (AZN)',
      accessor: 'net_margin_azn',
      render: (row) => (
        <span style={{ fontWeight: 700, color: 'var(--success)' }}>
          +{Number(row.net_margin_azn || 0).toFixed(2)} AZN
        </span>
      ),
    },
    {
      header: isAz ? 'Status' : 'Status',
      accessor: 'status',
      render: (row) => <StatusBadge status={row.status} />,
    },
  ];

  return (
    <div className="page-container">
      <div className="flex-between" style={{ marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>
            {isAz
              ? 'Dəqiq Platforma Analitikası və Bizneslər Üzrə AI Xərcləri'
              : 'Precise Platform Analytics & AI Spend Per Business'}
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            {isAz
              ? 'Bütün qeydiyyatdan keçmiş bizneslərin canlı MRR gəliri, token sərfiyyatı, AI model xərcləri və xalis mənfəət cədvəli.'
              : 'Real-time MRR, token consumption, AI model expenditure, and net margin across every tenant business.'}
          </p>
        </div>
        <button className="btn btn-secondary" onClick={fetchAnalytics}>
          <RefreshCw size={16} />
          {isAz ? 'Analitikanı Yenilə' : 'Refresh Analytics'}
        </button>
      </div>

      {/* Row 1: Financial & AI Spend Precision KPIs */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.25rem',
          marginBottom: '1.25rem',
        }}
      >
        <StatCard
          title={isAz ? 'Ümumi Bizneslər' : 'Total Businesses'}
          value={Number(analytics?.total_businesses || 0).toLocaleString()}
          icon={Building2}
          trend="up"
          trendValue={
            isAz
              ? `${analytics?.active_subscriptions || 0} aktiv • ${analytics?.trial_businesses || 0} sınaq (trial)`
              : `${analytics?.active_subscriptions || 0} active • ${analytics?.trial_businesses || 0} trial`
          }
        />
        <StatCard
          title={isAz ? 'Aylıq Abunə Gəliri (MRR)' : 'Monthly Recurring Revenue (MRR)'}
          value={`${Number(analytics?.mrr_azn ?? analytics?.mrr_usd ?? 0).toFixed(2)} AZN`}
          icon={DollarSign}
          trend="up"
          trendValue={`ARR: ${Number(analytics?.arr_azn || 0).toFixed(2)} AZN/${isAz ? 'il' : 'yr'}`}
        />
        <StatCard
          title={isAz ? 'Ümumi AI Xərci (Total AI Spend)' : 'Total Platform AI Spend'}
          value={`$${Number(analytics?.total_ai_spend_usd || 0).toFixed(4)} (${Number(analytics?.total_ai_spend_azn || 0).toFixed(4)} AZN)`}
          icon={Cpu}
          trend="up"
          trendValue={`${Number(analytics?.total_ai_tokens_used || 0).toLocaleString()} ${isAz ? 'token işlənib' : 'tokens processed'}`}
        />
        <StatCard
          title={isAz ? 'Xalis Platforma Mənfəəti' : 'Net Platform Margin'}
          value={`${Number(analytics?.net_platform_margin_azn || 0).toFixed(2)} AZN`}
          icon={TrendingUp}
          trend="up"
          trendValue={isAz ? 'MRR çıxılsın AI Xərci' : 'MRR minus Total AI Spend'}
        />
      </div>

      {/* Row 2: Operational & Volume Precision KPIs */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.25rem',
          marginBottom: '2rem',
        }}
      >
        <StatCard
          title={isAz ? 'Ümumi Randevular' : 'Total Appointments'}
          value={Number(analytics?.total_appointments || 0).toLocaleString()}
          icon={Calendar}
          trend="up"
          trendValue={
            isAz
              ? `${analytics?.completed_appointments || 0} tamamlanıb • ${analytics?.pending_appointments || 0} gözləyir • ${analytics?.cancelled_appointments || 0} ləğv`
              : `${analytics?.completed_appointments || 0} done • ${analytics?.pending_appointments || 0} pending • ${analytics?.cancelled_appointments || 0} cancelled`
          }
        />
        <StatCard
          title={isAz ? 'Ümumi AI Mesajlaşma' : 'Total AI Messages'}
          value={Number(analytics?.total_messages || 0).toLocaleString()}
          icon={MessageSquare}
          trend="up"
          trendValue={
            isAz
              ? `${analytics?.inbound_messages || 0} müştəri • ${analytics?.outbound_ai_messages || 0} AI cavab`
              : `${analytics?.inbound_messages || 0} inbound • ${analytics?.outbound_ai_messages || 0} AI replies`
          }
        />
        <StatCard
          title={isAz ? 'Salonların Ümumi Dövriyyəsi' : 'Total Venue Settled Revenue'}
          value={`${Number(analytics?.total_settled_revenue_azn || 0).toFixed(2)} AZN`}
          icon={CreditCard}
          trend="up"
          trendValue={isAz ? 'Nağd, Payriff və Paymegate' : 'Cash, Payriff & Paymegate'}
        />
        <StatCard
          title={isAz ? 'Son Müştərilər və Partnyorlar' : 'End Customers & Resellers'}
          value={Number(analytics?.total_customers || 0).toLocaleString()}
          icon={Users}
          trend="up"
          trendValue={`${analytics?.total_resellers || 0} ${isAz ? 'rəsmi partnyor' : 'agency partners'}`}
        />
      </div>

      {/* Per-Business AI Spend & Profitability Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ marginBottom: '1.25rem', color: 'var(--text-primary)' }}>
          {isAz
            ? 'Bizneslər Üzrə Dəqiq AI Xərci, Token Sərfiyyatı və Rentabellik Cədvəli'
            : 'Per-Business AI Spend, Token Consumption & Profitability Breakdown'}
        </h3>
        {spendRows.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', padding: '1rem 0', margin: 0 }}>
            {isAz
              ? 'Hələ qeydiyyatdan keçmiş biznes yoxdur. Yeni qeydiyyatlar və AI mesaj xərcləri avtomatik burada görünəcək.'
              : 'No businesses registered yet. New registrations and per-business AI spend will appear here automatically.'}
          </p>
        ) : (
          <DataTable columns={aiSpendColumns} data={spendRows} />
        )}
      </div>
    </div>
  );
};

export default Dashboard;
