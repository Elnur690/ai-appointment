import os

base_dir = "/Users/nargiznuriyeva/Documents/ai-appointment/frontend/business-dashboard/src"

files = {
    "styles/index.css": """
:root {
  --bg: #0b0d13;
  --surface: rgba(14, 17, 24, 0.9);
  --card: rgba(17, 20, 30, 0.7);
  --primary: linear-gradient(135deg, #0ea5e9, #06b6d4);
  --secondary: #8b5cf6;
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border: rgba(255, 255, 255, 0.08);
}

body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  background-color: var(--bg);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

.glass {
  background: var(--card);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.text-gradient {
  background: var(--primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Animations */
.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
""",

    "api/client.js": """
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
""",

    "store/authStore.js": """
import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: { name: 'Admin User', role: 'owner' },
  businessContext: { name: 'Glow Spa', id: 'b1' },
  isAuthenticated: true,
  login: (user) => set({ user, isAuthenticated: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));
""",

    "store/appointmentStore.js": """
import { create } from 'zustand';

export const useAppointmentStore = create((set) => ({
  appointments: [
    { id: 1, title: 'Haircut', status: 'confirmed', start: new Date(), staffId: 1, customer: 'John Doe' }
  ],
  filters: {},
  setFilters: (filters) => set({ filters }),
}));
""",

    "store/staffStore.js": """
import { create } from 'zustand';

export const useStaffStore = create((set) => ({
  staffList: [
    { id: 1, name: 'Alice Smith', role: 'Stylist' },
    { id: 2, name: 'Bob Jones', role: 'Massage Therapist' }
  ],
}));
""",

    "components/Layout/Sidebar.jsx": """
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Calendar, Users, Briefcase, Users2, MessageSquare, BookOpen, CreditCard, Settings } from 'lucide-react';
import './Layout.css';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/calendar', icon: Calendar, label: 'Calendar' },
  { path: '/appointments', icon: Users, label: 'Appointments' },
  { path: '/staff', icon: Users2, label: 'Staff' },
  { path: '/services', icon: Briefcase, label: 'Services' },
  { path: '/customers', icon: Users, label: 'Customers' },
  { path: '/conversations', icon: MessageSquare, label: 'Conversations' },
  { path: '/knowledge', icon: BookOpen, label: 'Knowledge Base' },
  { path: '/payments', icon: CreditCard, label: 'Payments' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const Sidebar = () => {
  const { businessContext } = useAuthStore();
  return (
    <div className="sidebar glass">
      <div className="sidebar-header">
        <h2 className="text-gradient">{businessContext.name}</h2>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <NavLink key={item.path} to={item.path} className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};
""",

    "components/Layout/Layout.css": """
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  border-right: 1px solid var(--border);
  border-radius: 0;
}

.sidebar-header {
  padding-bottom: 2rem;
  text-align: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s ease;
  margin-bottom: 0.5rem;
}

.nav-item:hover, .nav-item.active {
  background: rgba(255,255,255,0.05);
  color: var(--text-primary);
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(14,165,233,0.1) 0%, transparent 100%);
  border-left: 3px solid #0ea5e9;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  border-bottom: 1px solid var(--border);
}

.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}
""",

    "components/Layout/Layout.jsx": """
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Bell, Search, User } from 'lucide-react';
import './Layout.css';

export const Layout = () => {
  return (
    <div className="layout">
      <Sidebar />
      <div className="main-content">
        <header className="topbar glass" style={{borderRadius: 0}}>
          <div className="search-bar">
            <Search size={20} color="var(--text-secondary)" />
            <input type="text" placeholder="Search..." style={{background: 'transparent', border: 'none', color: 'var(--text-primary)', marginLeft: '0.5rem', outline: 'none'}} />
          </div>
          <div style={{display: 'flex', gap: '1.5rem', alignItems: 'center'}}>
            <Bell size={20} style={{cursor: 'pointer'}} />
            <User size={20} style={{cursor: 'pointer'}} />
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
""",

    "components/common/StatCard.jsx": """
import React from 'react';

export const StatCard = ({ title, value, icon: Icon, trend }) => (
  <div className="glass hover-lift" style={{ padding: '1.5rem', flex: 1, minWidth: '200px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
      <span style={{ color: 'var(--text-secondary)' }}>{title}</span>
      {Icon && <Icon size={24} style={{ color: '#0ea5e9' }} />}
    </div>
    <h3 style={{ margin: 0, fontSize: '2rem' }}>{value}</h3>
    {trend && (
      <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: trend.positive ? 'var(--success)' : 'var(--error)' }}>
        {trend.positive ? '+' : '-'}{trend.value}% from last month
      </div>
    )}
  </div>
);
""",

    "components/common/DataTable.jsx": """
import React from 'react';

export const DataTable = ({ columns, data }) => (
  <div className="glass" style={{ overflow: 'hidden' }}>
    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
      <thead style={{ backgroundColor: 'rgba(255,255,255,0.05)', borderBottom: '1px solid var(--border)' }}>
        <tr>
          {columns.map((col, i) => (
            <th key={i} style={{ padding: '1rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
            {columns.map((col, j) => (
              <td key={j} style={{ padding: '1rem' }}>{col.cell ? col.cell(row) : row[col.accessor]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
""",

    "components/common/StatusBadge.jsx": """
import React from 'react';

const colors = {
  confirmed: { bg: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' },
  pending: { bg: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' },
  completed: { bg: 'rgba(14, 165, 233, 0.1)', color: '#0ea5e9' },
  cancelled: { bg: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)' },
  no_show: { bg: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)' }
};

export const StatusBadge = ({ status }) => {
  const style = colors[status] || colors.pending;
  return (
    <span style={{
      padding: '0.25rem 0.75rem',
      borderRadius: '9999px',
      fontSize: '0.875rem',
      backgroundColor: style.bg,
      color: style.color,
      textTransform: 'capitalize'
    }}>
      {status.replace('_', ' ')}
    </span>
  );
};
""",

    "pages/Dashboard.jsx": """
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
export default Dashboard;
""",

    "pages/Calendar.jsx": """
import React from 'react';
const CalendarPage = () => <div><h2>Calendar</h2><div className="glass" style={{height:'600px', padding:'2rem', marginTop:'1rem'}}>Calendar View Component Placeholder</div></div>;
export default CalendarPage;
""",

    "pages/Appointments.jsx": """
import React from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';

const AppointmentsPage = () => {
  const cols = [
    { header: 'Customer', accessor: 'customer' },
    { header: 'Service', accessor: 'service' },
    { header: 'Date', accessor: 'date' },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> }
  ];
  const data = [
    { customer: 'Alice Wang', service: 'Haircut', date: '2023-10-01 10:00', status: 'confirmed' },
    { customer: 'Bob Smith', service: 'Massage', date: '2023-10-01 11:30', status: 'pending' },
    { customer: 'Carol Danvers', service: 'Facial', date: '2023-10-01 13:00', status: 'completed' },
  ];
  return (
    <div>
      <div style={{display:'flex', justifyContent:'space-between', marginBottom:'2rem'}}>
        <h2>Appointments</h2>
        <button className="glass" style={{padding:'0.5rem 1rem', cursor:'pointer', color:'white', background:'var(--primary)'}}>New Appointment</button>
      </div>
      <DataTable columns={cols} data={data} />
    </div>
  );
};
export default AppointmentsPage;
""",

    "pages/Staff.jsx": """import React from 'react'; export default () => <div><h2>Staff</h2></div>;""",
    "pages/Services.jsx": """import React from 'react'; export default () => <div><h2>Services</h2></div>;""",
    "pages/Customers.jsx": """import React from 'react'; export default () => <div><h2>Customers</h2></div>;""",
    "pages/Conversations.jsx": """import React from 'react'; export default () => <div><h2>Conversations</h2></div>;""",
    "pages/Knowledge.jsx": """import React from 'react'; export default () => <div><h2>Knowledge Base</h2></div>;""",
    "pages/Payments.jsx": """import React from 'react'; export default () => <div><h2>Payments</h2></div>;""",
    "pages/Settings.jsx": """import React from 'react'; export default () => <div><h2>Settings</h2></div>;""",
    "pages/Login.jsx": """import React from 'react'; export default () => <div><h2>Login</h2></div>;""",

    "App.jsx": """
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import CalendarPage from './pages/Calendar';
import AppointmentsPage from './pages/Appointments';
import Staff from './pages/Staff';
import Services from './pages/Services';
import Customers from './pages/Customers';
import Conversations from './pages/Conversations';
import Knowledge from './pages/Knowledge';
import Payments from './pages/Payments';
import Settings from './pages/Settings';
import Login from './pages/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="calendar" element={<CalendarPage />} />
          <Route path="appointments" element={<AppointmentsPage />} />
          <Route path="staff" element={<Staff />} />
          <Route path="services" element={<Services />} />
          <Route path="customers" element={<Customers />} />
          <Route path="conversations" element={<Conversations />} />
          <Route path="knowledge" element={<Knowledge />} />
          <Route path="payments" element={<Payments />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
export default App;
""",

    "main.jsx": """
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
}

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content.strip() + "\\n")

print("Files generated successfully.")
