import React from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';

const Payments = () => {
  const payments = [
    { id: 'PAY-901', customer: 'Murad Quliyev', type: 'Appointment Checkout', gateway: 'Payriff', amount: '25.00 AZN', status: 'confirmed' },
    { id: 'PAY-902', customer: 'Leyla ➔ Nigar', type: 'Digital Gift Voucher (GIFT-X89K92)', gateway: 'Payriff', amount: '100.00 AZN', status: 'confirmed' },
    { id: 'PAY-903', customer: 'Aysel Məmmədova', type: 'No-Show Protection Deposit', gateway: 'EPoint', amount: '20.00 AZN', status: 'confirmed' },
  ];

  const columns = [
    { header: 'Transaction ID', accessor: 'id' },
    { header: 'Customer', accessor: 'customer' },
    { header: 'Payment Type', accessor: 'type' },
    { header: 'Gateway', accessor: 'gateway' },
    { header: 'Amount', accessor: 'amount' },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Payments, Deposits & Gift Voucher Ledger</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Track Payriff and EPoint online transactions, no-show protection deposits, and digital gift voucher sales.
          </p>
        </div>
      </div>
      <DataTable columns={columns} data={payments} />
    </div>
  );
};

export default Payments;
