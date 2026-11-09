import React from 'react';
import { DataTable } from '../components/common/DataTable';
import { Plus, RefreshCw, Sparkles } from 'lucide-react';

const Services = () => {
  const services = [
    { name: "Men's Fade & Beard Trim", duration: '45 mins', price: '25 AZN', cadence: 'Every 16 days', flashDrop: '20% off (<4h)' },
    { name: 'Balayage & Blowout Combo', duration: '150 mins', price: '140 AZN', cadence: 'Every 45 days', flashDrop: '20% off (<4h)' },
    { name: 'Gel Manicure & Nail Art', duration: '60 mins', price: '40 AZN', cadence: 'Every 24 days', flashDrop: '15% off (<4h)' },
    { name: 'HydraFacial Skin Treatment', duration: '60 mins', price: '85 AZN', cadence: 'Every 30 days', flashDrop: '20% off (<4h)' },
  ];

  const columns = [
    { header: 'Service / Combo Package', accessor: 'name' },
    { header: 'Duration', accessor: 'duration' },
    { header: 'Base Price', accessor: 'price' },
    {
      header: 'Predictive Cadence Cycle',
      cell: (row) => (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--primary-accent)' }}>
          <RefreshCw size={14} /> {row.cadence}
        </span>
      ),
    },
    {
      header: 'Last-Minute Flash Drop',
      cell: (row) => (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: 'var(--success)' }}>
          <Sparkles size={14} /> {row.flashDrop}
        </span>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Services, Combo Packages & Cadence Cycles</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Manage service durations, Predictive Cadence rebooking intervals, and Last-Minute Flash Drop discounts.
          </p>
        </div>
        <button className="btn btn-primary">
          <Plus size={16} />
          Add Service
        </button>
      </div>
      <DataTable columns={columns} data={services} />
    </div>
  );
};

export default Services;
