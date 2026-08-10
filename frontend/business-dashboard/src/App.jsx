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
export default App;\n