import React from 'react';
import { DataTable } from '../components/common/DataTable';
import { Gift, Award } from 'lucide-react';

const Customers = () => {
  const customers = [
    { name: 'Murad Quliyev', phone: '+994 50 211 44 55', visits: 12, tier: 'VIP Gold (15% Off)', nextCadence: 'In 3 days (Fade)', voucher: 'None' },
    { name: 'Nigar Əliyeva', phone: '+994 55 322 11 99', visits: 6, tier: 'Silver (10% Off)', nextCadence: 'In 9 days (Gel Nails)', voucher: 'GIFT-X89K92 (100 AZN)' },
    { name: 'Aysel Məmmədova', phone: '+994 70 500 88 77', visits: 3, tier: 'Standard', nextCadence: 'In 18 days (Balayage)', voucher: 'None' },
  ];

  const columns = [
    { header: 'Customer Name', accessor: 'name' },
    { header: 'WhatsApp Phone', accessor: 'phone' },
    { header: 'Total Visits', accessor: 'visits' },
    {
      header: 'Loyalty Tier',
      cell: (row) => (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--warning)' }}>
          <Award size={14} /> {row.tier}
        </span>
      ),
    },
    { header: 'Predictive Rebooking', accessor: 'nextCadence' },
    {
      header: 'Digital Gift Voucher',
      cell: (row) => (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: row.voucher !== 'None' ? 'var(--success)' : 'var(--text-muted)' }}>
          <Gift size={14} /> {row.voucher}
        </span>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Customers, VIP Loyalty & Digital Gift Vouchers</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Track client visit history, automated Cadence reminders, and active WhatsApp Gift Vouchers.
          </p>
        </div>
      </div>
      <DataTable columns={columns} data={customers} />
    </div>
  );
};

export default Customers;
