import React, { useEffect } from 'react';
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
import LandingPage from './pages/LandingPage';

const isApexMarketingHost = () => {
  if (typeof window === 'undefined') return false;
  const h = window.location.hostname.toLowerCase();
  return h === 'randevu.vip' || h === 'www.randevu.vip';
};

const RedirectToAppHost = ({ path }) => {
  useEffect(() => {
    const search = window.location.search || '';
    window.location.replace(`https://app.randevu.vip${path}${search}`);
  }, [path]);
  return null;
};

function App() {
  const onMarketingDomain = isApexMarketingHost();

  if (onMarketingDomain) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<RedirectToAppHost path="/login" />} />
          <Route path="/register" element={<RedirectToAppHost path="/register" />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </BrowserRouter>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/welcome" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Login initialMode="register" />} />
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
