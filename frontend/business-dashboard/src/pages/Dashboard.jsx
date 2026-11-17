import React, { useEffect, useState } from 'react';
import { Users, Calendar, DollarSign, MessageSquare, Cpu, Clock } from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';

const Dashboard = () => {
  const { language, businessContext } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [analytics, setAnalytics] = useState({
    appointments_this_month: 0,
    revenue_this_month: 0,
    total_messages: 0,
    ai_tokens_used: 0,
    ai_spend_usd: 0,
    ai_spend_azn: 0,
  });
  const [appointments, setAppointments] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [conversations, setConversations] = useState([]);

  useEffect(() => {
    api.get('/businesses/analytics').then((r) => setAnalytics(r.data)).catch(() => {});
    api.get('/appointments/').then((r) => setAppointments(r.data || [])).catch(() => {});
    api.get('/customers/').then((r) => setCustomers(r.data || [])).catch(() => {});
    api.get('/conversations/').then((r) => setConversations(r.data || [])).catch(() => {});
  }, []);

  const cols = [
    { header: isAz ? 'Müştəri' : 'Customer', accessor: 'customer_name' },
    { header: isAz ? 'Xidmət' : 'Service', accessor: 'service_name' },
    { header: isAz ? 'Usta' : 'Staff', accessor: 'staff_name' },
    {
      header: isAz ? 'Randevu Vaxtı' : 'Scheduled Time',
      cell: (row) => (row.start_time ? new Date(row.start_time).toLocaleString() : '—'),
    },
    { header: isAz ? 'Status' : 'Status', cell: (row) => <StatusBadge status={row.status} /> },
  ];

  const isTrial = businessContext?.subscription_status === 'trial';
  const trialDaysLeft = businessContext?.trial_days_remaining ?? 14;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h1 style={{ margin: 0 }}>{isAz ? 'İdarə Paneli və Analitika Xülasəsi' : 'Workspace & Analytics Overview'}</h1>
        {isTrial && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              borderRadius: '999px',
              background: 'rgba(6, 182, 212, 0.15)',
              border: '1px solid rgba(6, 182, 212, 0.35)',
              color: 'var(--primary)',
              fontSize: '0.88rem',
              fontWeight: 600,
            }}
          >
            <Clock size={16} />
            {isAz
              ? `Pulsuz Sınaq Aktivdir: ${trialDaysLeft} gün qalıb (${businessContext?.plan_name || 'Starter'})`
              : `Free Trial Active: ${trialDaysLeft} days remaining (${businessContext?.plan_name || 'Starter'})`}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        <StatCard
          title={isAz ? 'Randevular (Bu Ay)' : 'Appointments (Month)'}
          value={Number(analytics.appointments_this_month || appointments.length).toLocaleString()}
          icon={Calendar}
        />
        <StatCard
          title={isAz ? 'Aktiv Söhbətlər' : 'Active Conversations'}
          value={Number(conversations.length).toLocaleString()}
          icon={MessageSquare}
        />
        <StatCard
          title={isAz ? 'Ümumi Müştərilər' : 'Total Customers'}
          value={Number(customers.length).toLocaleString()}
          icon={Users}
        />
        <StatCard
          title={isAz ? 'Gəlir (Bu Ay)' : 'Revenue (Month)'}
          value={`${Number(analytics.revenue_this_month || 0).toFixed(2)} AZN`}
          icon={DollarSign}
        />
        <StatCard
          title={isAz ? 'AI İstifadəsi və Xərci' : 'AI Token Usage & Spend'}
          value={`${Number(analytics.ai_spend_azn || 0).toFixed(4)} AZN`}
          icon={Cpu}
        />
      </div>

      <div className="glass" style={{ padding: '1.5rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>{isAz ? 'Son Randevular' : 'Recent Appointments'}</h2>
        <DataTable
          columns={cols}
          data={appointments.slice(0, 10)}
          emptyMessage={
            isAz
              ? 'Hələ randevu yoxdur. İlk randevunu yaradın və ya Tənzimləmələrdən WhatsApp/Instagram/Telegram qoşun.'
              : 'No appointments scheduled yet. Create your first appointment or pair WhatsApp in Settings.'
          }
        />
      </div>
    </div>
  );
};
export default Dashboard;
