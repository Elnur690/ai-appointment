import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Plus } from 'lucide-react';

const Payments = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
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
    { header: isAz ? 'Əməliyyat ID' : 'Transaction ID', cell: (row) => String(row.id).slice(0, 8).toUpperCase() },
    { header: isAz ? 'Müştəri / Qeyd' : 'Customer / Note', accessor: 'customer' },
    { header: isAz ? 'Ödəniş Üsulu / Şlüz' : 'Method / Gateway', accessor: 'gateway' },
    { header: isAz ? 'Məbləğ' : 'Amount', accessor: 'amount' },
    {
      header: isAz ? 'Status' : 'Status',
      cell: (row) => <StatusBadge status={row.status === 'paid' ? 'confirmed' : row.status} />,
    },
  ];

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h2>
            {isAz
              ? 'Ödənişlər, Beh (Depozit) və Gəlir Jurnalı'
              : 'Payments, Deposits & Transaction Ledger'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {isAz ? 'Ümumi Təsdiqlənmiş Gəlir:' : 'Total Settled Revenue:'}{' '}
            <strong>{Number(summary.total_revenue || 0).toFixed(2)} AZN</strong> (
            {summary.count || 0} {isAz ? 'əməliyyat' : 'transactions'})
          </p>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
            {gateways.map((gw) => (
              <span
                key={gw.provider}
                className={gw.enabled ? 'badge badge-success' : 'badge badge-warning'}
                style={{ fontSize: '0.75rem' }}
              >
                {gw.name}: {gw.enabled ? (isAz ? 'Aktiv' : 'Enabled') : isAz ? 'Deaktiv' : 'Disabled'}
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
          {isAz ? 'Ödəniş Qeydə Al' : 'Record Payment'}
        </button>
      </div>

      <DataTable
        columns={columns}
        data={payments}
        emptyMessage={
          isAz
            ? 'Hələ ödəniş qeydə alınmayıb. Nağd, Payriff və Paymegate əməliyyatları burada görünəcək.'
            : 'No payments recorded yet. Cash, Payriff, and Paymegate transactions will appear here.'
        }
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isAz ? 'Yeni Ödəniş Qeydə Al' : 'Record Payment'}
      >
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Məbləğ (AZN)' : 'Amount (AZN)'}</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              className="form-control"
              required
              placeholder="məs: 45.00"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">{isAz ? 'Müştəri / Qeyd (İstəyə bağlı)' : 'Customer / Note (Optional)'}</label>
            <input
              type="text"
              className="form-control"
              placeholder={isAz ? 'məs: Leyla M. - Saç kəsimi beh' : 'e.g. Leyla M. - Haircut Deposit'}
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">{isAz ? 'Ödəniş Şlüzü / Üsulu' : 'Payment Gateway / Method'}</label>
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
              {isAz ? 'Ləğv et' : 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary">
              {isAz ? 'Ödənişi Yadda Saxla' : 'Record Payment'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Payments;
