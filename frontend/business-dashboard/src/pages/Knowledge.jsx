import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { Modal } from '../components/common/Modal';
import api from '../api/client';
import { Plus, Trash2 } from 'lucide-react';

const Knowledge = () => {
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
    { header: 'Knowledge Title', accessor: 'title' },
    { header: 'Type', accessor: 'type' },
    { header: 'Vectorized Content', accessor: 'content' },
    { header: 'RAG Status', accessor: 'status' },
    {
      header: 'Actions',
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
          <h2>RAG Knowledge Base & "Learn from Mistakes"</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            PostgreSQL pgvector knowledge entries used by your AI receptionist to answer business-specific questions accurately.
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} />
          Add Knowledge Entry
        </button>
      </div>

      <DataTable
        columns={columns}
        data={entries}
        emptyMessage="No knowledge base entries yet. Add FAQs, parking instructions, or policies for your AI assistant."
      />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Knowledge Base Entry">
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">Title / Topic</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="e.g. Parking Instructions, Cancellation Policy"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select
              className="form-control"
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
            >
              <option value="faq">FAQ</option>
              <option value="policy">Policy</option>
              <option value="service_info">Service Information</option>
              <option value="correction">Learned Correction</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Knowledge Content</label>
            <textarea
              className="form-control"
              rows={4}
              required
              placeholder="Write the exact answer or rule the AI should follow..."
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save to Knowledge Base
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Knowledge;
