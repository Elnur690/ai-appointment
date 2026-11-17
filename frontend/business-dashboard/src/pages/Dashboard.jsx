import React, { useEffect, useState } from 'react';
import { Users, Calendar, DollarSign, MessageSquare } from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';

const Dashboard = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [analytics, setAnalytics] = useState({ appointments_this_month: 0, revenue_this_month: 0 });
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

  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>{isAz ? 'İdarə Paneli Xülasəsi' : 'Workspace Overview'}</h1>
      <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
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
