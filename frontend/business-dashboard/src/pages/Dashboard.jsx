import React from 'react';
import { Users, Calendar, DollarSign, Activity } from 'lucide-react';
import { StatCard } from '../components/common/StatCard';

const Dashboard = () => {
  return (
    <div>
      <h1 style={{ marginBottom: '2rem' }}>Overview</h1>
      <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        <StatCard title="Today's Appointments" value="24" icon={Calendar} trend={{ positive: true, value: 12 }} />
        <StatCard title="Pending Review" value="5" icon={Activity} trend={{ positive: false, value: 2 }} />
        <StatCard title="Total Customers" value="1,204" icon={Users} trend={{ positive: true, value: 5 }} />
        <StatCard title="Revenue Today" value="$840" icon={DollarSign} trend={{ positive: true, value: 8 }} />
      </div>
      <div className="glass" style={{ padding: '2rem' }}>
        <h2>AI Conversation Activity</h2>
        <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
          Chart Area (Recharts)
        </div>
      </div>
    </div>
  );
};
export default Dashboard;\n