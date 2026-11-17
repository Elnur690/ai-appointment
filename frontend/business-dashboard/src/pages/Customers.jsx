import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { Modal } from '../components/common/Modal';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Award, Plus } from 'lucide-react';

const Customers = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [customers, setCustomers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ name: '', phone: '', email: '' });

  const loadCustomers = async () => {
    try {
      const res = await api.get('/customers/');
      setCustomers(res.data || []);
    } catch {
      setCustomers([]);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/customers/', {
      name: form.name,
      phone: form.phone,
      email: form.email || null,
    });
    setIsModalOpen(false);
    setForm({ name: '', phone: '', email: '' });
    await loadCustomers();
  };

  const columns = [
    { header: isAz ? 'Müştəri Adı' : 'Customer Name', accessor: 'name' },
    { header: isAz ? 'Telefon / WhatsApp' : 'WhatsApp Phone', accessor: 'phone' },
    { header: isAz ? 'E-poçt' : 'Email', cell: (row) => row.email || '—' },
    { header: isAz ? 'Gəliş Sayı' : 'Total Visits', accessor: 'visits' },
    {
      header: isAz ? 'Loyallıq Statusu' : 'Loyalty Tier',
      cell: (row) => (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--warning)' }}>
          <Award size={14} /> {row.tier || 'Standard'}
        </span>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>{isAz ? 'Müştərilər və Loyallıq Bazası' : 'Customers & Loyalty Profiles'}</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {isAz
              ? 'WhatsApp, Instagram və ya Telegram-dan yazan müştərilər avtomatik qeydə alınır, həmçinin əllə əlavə edə bilərsiniz.'
              : 'Customer profiles are created automatically when they message on WhatsApp/Instagram/Telegram, or you can add them manually.'}
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} />
          {isAz ? 'Müştəri Əlavə Et' : 'Add Customer'}
        </button>
      </div>

      <DataTable
        columns={columns}
        data={customers}
        emptyMessage={
          isAz
            ? 'Hələ müştəri yoxdur. İlk müştərinizi əlavə edin və ya Tənzimləmələrdən WhatsApp qoşun.'
            : 'No customers yet. Add your first customer or connect WhatsApp in Settings.'
        }
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isAz ? 'Yeni Müştəri Əlavə Et' : 'Add Customer'}
      >
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Tam Adı' : 'Full Name'}</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder={isAz ? 'Müştərinin adı və soyadı' : 'Customer full name'}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{isAz ? 'WhatsApp Telefon Nömrəsi' : 'WhatsApp Phone Number'}</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="+994 50 000 00 00"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">{isAz ? 'E-poçt Ünvanı (İstəyə bağlı)' : 'Email Address (Optional)'}</label>
            <input
              type="email"
              className="form-control"
              placeholder="customer@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary">
              {isAz ? 'Yadda Saxla' : 'Save Customer'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Customers;
