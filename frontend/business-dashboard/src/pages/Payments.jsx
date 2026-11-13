import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import api from '../api/client';
import { Plus } from 'lucide-react';

const Payments = () => {
  const [payments, setPayments] = useState([]);
  const [summary, setSummary] = useState({ total_revenue: 0, count: 0 });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ amount: '', currency: 'AZN', method: 'cash', status: 'paid' });

  const loadPayments = async () => {
    const [payRes, sumRes] = await Promise.all([
      api.get('/payments/').catch(() => ({ data: [] })),
      api.get('/payments/summary').catch(() => ({ data: { total_revenue: 0, count: 0 } })),
    ]);
    setPayments(payRes.data || []);
    setSummary(sumRes.data || { total_revenue: 0, count: 0 });
  };

  useEffect(() => {
    loadPayments();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/payments/', {
      amount: Number(form.amount),
      currency: form.currency,
      method: form.method,
      status: form.status,
    });
    setIsModalOpen(false);
    setForm({ amount: '', currency: 'AZN', method: 'cash', status: 'paid' });
    await loadPayments();
  };

  const columns = [
    { header: 'Transaction ID', cell: (row) => String(row.id).slice(0, 8).toUpperCase() },
    { header: 'Customer', accessor: 'customer' },
    { header: 'Method / Gateway', accessor: 'gateway' },
    { header: 'Amount', accessor: 'amount' },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status === 'paid' ? 'confirmed' : row.status} /> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Payments, Deposits & Transaction Ledger</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Total Settled Revenue: <strong>{Number(summary.total_revenue || 0).toFixed(2)} AZN</strong> ({summary.count || 0} transactions)
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} />
          Record Payment
        </button>
      </div>

      <DataTable
        columns={columns}
        data={payments}
        emptyMessage="No payments recorded yet. Online Payriff/EPoint deposits and manual payments will appear here."
      />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Record Payment">
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">Amount (AZN)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              className="form-control"
              required
              placeholder="e.g. 45.00"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
            />
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Payment Method</label>
            <select
              className="form-control"
              value={form.method}
              onChange={(e) => setForm({ ...form, method: e.target.value })}
            >
              <option value="cash">Cash at Salon</option>
              <option value="card">POS Terminal / Card</option>
              <option value="online">Online Gateway (Payriff / EPoint)</option>
            </select>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Record Payment
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Payments;
