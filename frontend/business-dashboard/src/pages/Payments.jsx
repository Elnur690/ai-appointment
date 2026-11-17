import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import api from '../api/client';
import { Plus } from 'lucide-react';

const Payments = () => {
  const [payments, setPayments] = useState([]);
  const [summary, setSummary] = useState({ total_revenue: 0, count: 0 });
  const [gateways, setGateways] = useState([
    { provider: 'cash', name: 'Cash Payment (At Venue)', enabled: true },
    { provider: 'payriff', name: 'Payriff Payment Gateway', enabled: true },
    { provider: 'paymegate', name: 'Paymegate Payment Gateway', enabled: true },
  ]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ amount: '', currency: 'AZN', method: 'cash', status: 'paid', notes: '' });

  const loadPayments = async () => {
    const [payRes, sumRes, gwRes] = await Promise.all([
      api.get('/payments/').catch(() => ({ data: [] })),
      api.get('/payments/summary').catch(() => ({ data: { total_revenue: 0, count: 0 } })),
      api.get('/payments/gateways').catch(() => ({ data: [] })),
    ]);
    setPayments(payRes.data || []);
    setSummary(sumRes.data || { total_revenue: 0, count: 0 });
    if (Array.isArray(gwRes.data) && gwRes.data.length > 0) {
      setGateways(gwRes.data);
      const firstEnabled = gwRes.data.find((g) => g.enabled);
      if (firstEnabled) {
        setForm((prev) => ({ ...prev, method: firstEnabled.provider }));
      }
    }
  };

  useEffect(() => {
    loadPayments();
  }, []);

  const enabledGateways = gateways.filter((g) => g.enabled);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/payments/', {
      amount: Number(form.amount),
      currency: form.currency,
      method: form.method,
      status: form.status,
      notes: form.notes || null,
    });
    setIsModalOpen(false);
    setForm({
      amount: '',
      currency: 'AZN',
      method: enabledGateways[0]?.provider || 'cash',
      status: 'paid',
      notes: '',
    });
    await loadPayments();
  };

  const columns = [
    { header: 'Transaction ID', cell: (row) => String(row.id).slice(0, 8).toUpperCase() },
    { header: 'Customer / Note', accessor: 'customer' },
    { header: 'Method / Gateway', accessor: 'gateway' },
    { header: 'Amount', accessor: 'amount' },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status === 'paid' ? 'confirmed' : row.status} /> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2>Payments, Deposits & Transaction Ledger</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Total Settled Revenue: <strong>{Number(summary.total_revenue || 0).toFixed(2)} AZN</strong> ({summary.count || 0} transactions)
          </p>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
            {gateways.map((gw) => (
              <span
                key={gw.provider}
                className={gw.enabled ? 'badge badge-success' : 'badge badge-warning'}
                style={{ fontSize: '0.75rem' }}
              >
                {gw.name}: {gw.enabled ? 'Enabled' : 'Disabled'}
              </span>
            ))}
          </div>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setIsModalOpen(true)}
          disabled={enabledGateways.length === 0}
        >
          <Plus size={16} />
          Record Payment
        </button>
      </div>

      <DataTable
        columns={columns}
        data={payments}
        emptyMessage="No payments recorded yet. Cash, Payriff, and PaymenGate transactions will appear here."
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
          <div className="form-group">
            <label className="form-label">Customer / Note (Optional)</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Leyla M. - Haircut Deposit"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Payment Gateway / Method</label>
            <select
              className="form-control"
              value={form.method}
              onChange={(e) => setForm({ ...form, method: e.target.value })}
            >
              {enabledGateways.map((gw) => (
                <option key={gw.provider} value={gw.provider}>
                  {gw.name}
                </option>
              ))}
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
