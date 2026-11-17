import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { Modal } from '../components/common/Modal';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Plus, RefreshCw } from 'lucide-react';

const Services = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [services, setServices] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({
    name: '',
    description: '',
    duration_minutes: 45,
    price: 30,
    currency: 'AZN',
    recommended_rebooking_days: 21,
  });

  const loadServices = async () => {
    try {
      const res = await api.get('/services/');
      setServices(res.data || []);
    } catch {
      setServices([]);
    }
  };

  useEffect(() => {
    loadServices();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/services/', {
      ...form,
      duration_minutes: Number(form.duration_minutes),
      price: Number(form.price),
      recommended_rebooking_days: form.recommended_rebooking_days ? Number(form.recommended_rebooking_days) : null,
    });
    setIsModalOpen(false);
    setForm({ name: '', description: '', duration_minutes: 45, price: 30, currency: 'AZN', recommended_rebooking_days: 21 });
    await loadServices();
  };

  const columns = [
    { header: isAz ? 'Xidmət / Paket' : 'Service / Package', accessor: 'name' },
    { header: isAz ? 'Müddət' : 'Duration', cell: (row) => `${row.duration_minutes} ${isAz ? 'dəq' : 'mins'}` },
    { header: isAz ? 'Qiymət' : 'Price', cell: (row) => `${Number(row.price).toFixed(2)} ${row.currency || 'AZN'}` },
    {
      header: isAz ? 'Avtomatik Təkrar Dövrü' : 'Predictive Cadence Cycle',
      cell: (row) => (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--primary)' }}>
          <RefreshCw size={14} />
          {row.recommended_rebooking_days
            ? isAz
              ? `Hər ${row.recommended_rebooking_days} gündən bir`
              : `Every ${row.recommended_rebooking_days} days`
            : isAz
            ? 'Tələbə görə'
            : 'On demand'}
        </span>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>{isAz ? 'Xidmətlər və Avtomatik Təkrar Randevu' : 'Services & Predictive Rebooking Cycles'}</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {isAz
              ? 'Xidmət menyunuzu, müddətləri, qiymətləri və avtomatik xatırlatma intervallarını idarə edin.'
              : 'Manage your service menu, durations, pricing, and automated rebooking intervals.'}
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} />
          {isAz ? 'Xidmət Əlavə Et' : 'Add Service'}
        </button>
      </div>

      <DataTable
        columns={columns}
        data={services}
        emptyMessage={
          isAz
            ? "Hələ xidmət əlavə edilməyib. Kataloqunuzu yaratmaq üçün 'Xidmət Əlavə Et' düyməsinə klikləyin."
            : "No services configured yet. Click 'Add Service' to build your catalog."
        }
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isAz ? 'Yeni Xidmət Əlavə Et' : 'Add Service'}
      >
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Xidmətin Adı' : 'Service Name'}</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder={isAz ? 'məs: Saç kəsimi və fen' : 'e.g. Haircut & Styling'}
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Təsvir (AI Köməkçi üçün)' : 'Description (for AI Assistant)'}</label>
            <input
              type="text"
              className="form-control"
              placeholder={isAz ? 'Xidmət haqqında əlavə məlumat' : 'Optional details about this service'}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">{isAz ? 'Müddət (dəqiqə)' : 'Duration (minutes)'}</label>
              <input
                type="number"
                min="5"
                className="form-control"
                required
                value={form.duration_minutes}
                onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">{isAz ? 'Qiymət (AZN)' : 'Price (AZN)'}</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-control"
                required
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
              />
            </div>
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">
              {isAz ? 'Tövsiyə Olunan Təkrar Randevu Müddəti (Gün)' : 'Recommended Rebooking Interval (Days)'}
            </label>
            <input
              type="number"
              min="1"
              className="form-control"
              value={form.recommended_rebooking_days}
              onChange={(e) => setForm({ ...form, recommended_rebooking_days: e.target.value })}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary">
              {isAz ? 'Xidməti Yarat' : 'Create Service'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Services;
