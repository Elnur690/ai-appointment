import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Plus, CreditCard } from 'lucide-react';

const Payments = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [payments, setPayments] = useState([]);
  const [summary, setSummary] = useState({ total_revenue: 0, count: 0 });
  const [subscription, setSubscription] = useState(null);
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutMessage, setCheckoutMessage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ amount: '', currency: 'AZN', method: 'cash', status: 'paid', notes: '' });

  const paymentMethods = [
    {
      provider: 'cash',
      name: isAz ? 'Nağd Ödəniş (Yerində)' : 'Cash Payment (On-Site)',
      enabled: true,
    },
    {
      provider: 'card',
      name: isAz ? 'Onlayn Kart / Beh Ödənişi' : 'Online Card / Deposit Payment',
      enabled: true,
    },
  ];

  const loadPayments = async () => {
    const [payRes, sumRes, subRes] = await Promise.all([
      api.get('/payments/').catch(() => ({ data: [] })),
      api.get('/payments/summary').catch(() => ({ data: { total_revenue: 0, count: 0 } })),
      api.get('/businesses/subscription').catch(() => ({ data: null })),
    ]);
    setPayments(payRes.data || []);
    setSummary(sumRes.data || { total_revenue: 0, count: 0 });
    if (subRes.data) {
      setSubscription(subRes.data);
      setSelectedPlanId((prev) => prev || subRes.data.current_plan_id || subRes.data.plans?.[0]?.id || '');
    }
  };

  const handlePlanCheckout = async () => {
    setCheckoutMessage('');
    setCheckoutLoading(true);
    try {
      const res = await api.post('/businesses/subscription/checkout', { plan_id: selectedPlanId });
      if (res.data?.checkout_url) {
        window.open(res.data.checkout_url, '_blank', 'noopener,noreferrer');
      } else {
        setCheckoutMessage(
          isAz
            ? `Ödəniş sorğusu yaradıldı (${res.data?.plan_name} — ${res.data?.amount} AZN).`
            : `Subscription invoice created (${res.data?.plan_name} — ${res.data?.amount} AZN).`
        );
      }
    } catch (err) {
      setCheckoutMessage(err.response?.data?.detail || 'Checkout failed.');
    } finally {
      setCheckoutLoading(false);
    }
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
      notes: form.notes || null,
    });
    setIsModalOpen(false);
    setForm({
      amount: '',
      currency: 'AZN',
      method: 'cash',
      status: 'paid',
      notes: '',
    });
    await loadPayments();
  };

  const formatGatewayLabel = (gw) => {
    const raw = String(gw || '').toLowerCase();
    if (raw.includes('cash') || raw.includes('nağd')) {
      return isAz ? 'Nağd Ödəniş' : 'Cash Payment';
    }
    return isAz ? 'Onlayn Kart / Beh Ödənişi' : 'Online Card / Deposit';
  };

  const columns = [
    { header: isAz ? 'Əməliyyat ID' : 'Transaction ID', cell: (row) => String(row.id).slice(0, 8).toUpperCase() },
    { header: isAz ? 'Müştəri / Qeyd' : 'Customer / Note', accessor: 'customer' },
    { header: isAz ? 'Ödəniş Üsulu' : 'Payment Method', cell: (row) => formatGatewayLabel(row.gateway) },
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
            {paymentMethods.map((pm) => (
              <span
                key={pm.provider}
                className="badge badge-success"
                style={{ fontSize: '0.75rem' }}
              >
                {pm.name}: {isAz ? 'Aktiv' : 'Active'}
              </span>
            ))}
          </div>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setIsModalOpen(true)}
        >
          <Plus size={16} />
          {isAz ? 'Ödəniş Qeydə Al' : 'Record Payment'}
        </button>
      </div>

      {subscription && (
        <div
          className="glass-card"
          style={{
            padding: '1.25rem 1.5rem',
            marginBottom: '1.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
            border: '1px solid rgba(212, 175, 55, 0.35)',
          }}
        >
          <div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              {isAz ? 'Cari Abunəlik Paketi' : 'Current Subscription Plan'}
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700 }}>
              {subscription.current_plan_name} ({subscription.current_plan_price} AZN/ay) •{' '}
              <span style={{ color: subscription.subscription_status === 'active' ? 'var(--success)' : 'var(--warning)' }}>
                {subscription.subscription_status}
              </span>
            </div>
            {checkoutMessage && (
              <div style={{ fontSize: '0.84rem', color: 'var(--primary)', marginTop: '0.35rem' }}>
                {checkoutMessage}
              </div>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
            <select
              className="form-control"
              style={{ width: 'auto', minWidth: '190px' }}
              value={selectedPlanId}
              onChange={(e) => setSelectedPlanId(e.target.value)}
            >
              {(subscription.plans || []).map((pl) => (
                <option key={pl.id} value={pl.id}>
                  {pl.name} — {pl.price} AZN
                </option>
              ))}
            </select>
            <button
              type="button"
              className="btn btn-gold"
              onClick={handlePlanCheckout}
              disabled={checkoutLoading || !selectedPlanId}
            >
              <CreditCard size={16} />
              {checkoutLoading
                ? isAz
                  ? 'Yönləndirilir...'
                  : 'Redirecting...'
                : isAz
                ? 'Abunəliyi Ödə / Yenilə'
                : 'Pay / Upgrade Plan'}
            </button>
          </div>
        </div>
      )}

      <DataTable
        columns={columns}
        data={payments}
        emptyMessage={
          isAz
            ? 'Hələ ödəniş qeydə alınmayıb. Nağd və onlayn kart / beh ödənişləri burada görünəcək.'
            : 'No payments recorded yet. Cash and online card / deposit transactions will appear here.'
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
              placeholder={isAz ? 'məs: Leyla M. - Konsultasiya behi' : 'e.g. Leyla M. - Consultation Deposit'}
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">{isAz ? 'Ödəniş Üsulu' : 'Payment Method'}</label>
            <select
              className="form-control"
              value={form.method}
              onChange={(e) => setForm({ ...form, method: e.target.value })}
            >
              {paymentMethods.map((pm) => (
                <option key={pm.provider} value={pm.provider}>
                  {pm.name}
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
