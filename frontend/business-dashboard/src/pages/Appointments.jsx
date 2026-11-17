import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Plus } from 'lucide-react';

const AppointmentsPage = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [appointments, setAppointments] = useState([]);
  const [services, setServices] = useState([]);
  const [staffList, setStaffList] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({
    customer_id: '',
    service_id: '',
    staff_id: '',
    start_time: '',
  });

  const loadAll = async () => {
    const [apptRes, srvRes, stfRes, custRes] = await Promise.all([
      api.get('/appointments/').catch(() => ({ data: [] })),
      api.get('/services/').catch(() => ({ data: [] })),
      api.get('/staff/').catch(() => ({ data: [] })),
      api.get('/customers/').catch(() => ({ data: [] })),
    ]);
    setAppointments(apptRes.data || []);
    setServices(srvRes.data || []);
    setStaffList(stfRes.data || []);
    setCustomers(custRes.data || []);
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/appointments/', {
      customer_id: form.customer_id || null,
      service_id: form.service_id || null,
      staff_id: form.staff_id || null,
      start_time: new Date(form.start_time).toISOString(),
    });
    setIsModalOpen(false);
    setForm({ customer_id: '', service_id: '', staff_id: '', start_time: '' });
    await loadAll();
  };

  const handleStatusChange = async (id, status) => {
    await api.put(`/appointments/${id}/status`, { status });
    await loadAll();
  };

  const cols = [
    { header: isAz ? 'Müştəri' : 'Customer', accessor: 'customer_name' },
    { header: isAz ? 'Xidmət' : 'Service', accessor: 'service_name' },
    { header: isAz ? 'Usta' : 'Staff', accessor: 'staff_name' },
    {
      header: isAz ? 'Tarix və Saat' : 'Date & Time',
      cell: (row) => (row.start_time ? new Date(row.start_time).toLocaleString() : '—'),
    },
    { header: isAz ? 'Status' : 'Status', cell: (row) => <StatusBadge status={row.status} /> },
    {
      header: isAz ? 'Əməliyyatlar' : 'Actions',
      cell: (row) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {row.status !== 'completed' && (
            <button
              type="button"
              className="btn btn-secondary"
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => handleStatusChange(row.id, 'completed')}
            >
              {isAz ? 'Tamamla' : 'Complete'}
            </button>
          )}
          {row.status !== 'cancelled' && (
            <button
              type="button"
              className="btn btn-danger"
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => handleStatusChange(row.id, 'cancelled')}
            >
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>{isAz ? 'Randevular' : 'Appointments'}</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {isAz
              ? 'WhatsApp, Instagram, Telegram və birbaşa müraciətlərdən gələn bütün randevuları idarə edin.'
              : 'View and manage all customer bookings across WhatsApp, Instagram, Telegram, and walk-ins.'}
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} />
          {isAz ? 'Yeni Randevu' : 'New Appointment'}
        </button>
      </div>

      <DataTable
        columns={cols}
        data={appointments}
        emptyMessage={
          isAz
            ? "Hələ randevu yoxdur. Yeni randevu yaratmaq üçün 'Yeni Randevu' düyməsinə klikləyin."
            : "No appointments booked yet. Click 'New Appointment' to schedule one."
        }
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isAz ? 'Yeni Randevu Yarat' : 'Create New Appointment'}
      >
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Müştəri' : 'Customer'}</label>
            <select
              className="form-control"
              value={form.customer_id}
              onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
            >
              <option value="">{isAz ? 'Müştəri seçin (və ya birbaşa qonaq)' : 'Select customer (or create walk-in)'}</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.phone})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Xidmət' : 'Service'}</label>
            <select
              className="form-control"
              value={form.service_id}
              onChange={(e) => setForm({ ...form, service_id: e.target.value })}
            >
              <option value="">{isAz ? 'Xidmət seçin' : 'Select service'}</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.duration_minutes} dəq — {s.price} {s.currency})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Usta / Mütəxəssis' : 'Staff Member'}</label>
            <select
              className="form-control"
              value={form.staff_id}
              onChange={(e) => setForm({ ...form, staff_id: e.target.value })}
            >
              <option value="">{isAz ? 'Usta seçin' : 'Select staff member'}</option>
              {staffList.map((st) => (
                <option key={st.id} value={st.id}>
                  {st.name} ({st.role_title})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">{isAz ? 'Başlama Tarixi və Saatı' : 'Start Date & Time'}</label>
            <input
              type="datetime-local"
              className="form-control"
              required
              value={form.start_time}
              onChange={(e) => setForm({ ...form, start_time: e.target.value })}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary">
              {isAz ? 'Randevunu Təsdiqlə' : 'Schedule Appointment'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
export default AppointmentsPage;
