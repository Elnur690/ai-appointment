import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { Modal } from '../components/common/Modal';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Plus, Trash2 } from 'lucide-react';

const Knowledge = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [entries, setEntries] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ title: '', type: 'faq', content: '' });

  const loadKnowledge = async () => {
    try {
      const res = await api.get('/knowledge/');
      setEntries(res.data || []);
    } catch {
      setEntries([]);
    }
  };

  useEffect(() => {
    loadKnowledge();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/knowledge/', form);
    setIsModalOpen(false);
    setForm({ title: '', type: 'faq', content: '' });
    await loadKnowledge();
  };

  const handleDelete = async (id) => {
    await api.delete(`/knowledge/${id}`);
    await loadKnowledge();
  };

  const columns = [
    { header: isAz ? 'Mövzu / Başlıq' : 'Knowledge Title', accessor: 'title' },
    { header: isAz ? 'Kateqoriya' : 'Type', accessor: 'type' },
    { header: isAz ? 'Məzmun / Cavab' : 'Knowledge Content', accessor: 'content' },
    { header: isAz ? 'Status' : 'Status', accessor: 'status' },
    {
      header: isAz ? 'Sil' : 'Actions',
      cell: (row) => (
        <button
          type="button"
          className="btn btn-danger"
          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
          onClick={() => handleDelete(row.id)}
        >
          <Trash2 size={14} />
        </button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>
            {isAz
              ? 'Biznes Məlumat Bazası və AI Təlimatları'
              : 'Business Knowledge Base & AI Instructions'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {isAz
              ? 'Süni intellekt resepşnin müştəri suallarına dəqiq cavab verməsi üçün biznesinizə aid sual-cavab və qayda qeydləri.'
              : 'Business-specific rules, FAQs, and answers used by your AI receptionist to assist clients accurately.'}
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} />
          {isAz ? 'Yeni Qeyd Əlavə Et' : 'Add Knowledge Entry'}
        </button>
      </div>

      <DataTable
        columns={columns}
        data={entries}
        emptyMessage={
          isAz
            ? 'Hələ bilik bazası qeydi yoxdur. AI köməkçiniz üçün tez-tez verilən sualları, parkinq və daxili qaydaları əlavə edin.'
            : 'No knowledge base entries yet. Add FAQs, parking instructions, or policies for your AI assistant.'
        }
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isAz ? 'Bilik Bazasına Qeyd Əlavə Et' : 'Add Knowledge Base Entry'}
      >
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Başlıq / Mövzu' : 'Title / Topic'}</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder={isAz ? 'məs: Parkinq məlumatı, Ləğvetmə qaydası' : 'e.g. Parking Instructions, Cancellation Policy'}
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Kateqoriya' : 'Category'}</label>
            <select
              className="form-control"
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
            >
              <option value="faq">{isAz ? 'Tez-tez verilən sual (FAQ)' : 'FAQ'}</option>
              <option value="policy">{isAz ? 'Daxili Qayda / Siyasət' : 'Policy'}</option>
              <option value="service_info">{isAz ? 'Xidmət Məlumatı' : 'Service Information'}</option>
              <option value="correction">{isAz ? 'Öyrədilmiş Düzəliş' : 'Learned Correction'}</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">{isAz ? 'Məzmun / AI Təlimatı' : 'Knowledge Content'}</label>
            <textarea
              className="form-control"
              rows={4}
              required
              placeholder={
                isAz
                  ? 'AI köməkçinin müştəriyə verməli olduğu dəqiq cavabı və ya qaydanı yazın...'
                  : 'Write the exact answer or rule the AI should follow...'
              }
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary">
              {isAz ? 'Yaddaşa Əlavə Et' : 'Save to Knowledge Base'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Knowledge;
