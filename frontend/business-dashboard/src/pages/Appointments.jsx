import React from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';

const AppointmentsPage = () => {
  const cols = [
    { header: 'Customer', accessor: 'customer' },
    { header: 'Service', accessor: 'service' },
    { header: 'Date', accessor: 'date' },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> }
  ];
  const data = [
    { customer: 'Alice Wang', service: 'Haircut', date: '2023-10-01 10:00', status: 'confirmed' },
    { customer: 'Bob Smith', service: 'Massage', date: '2023-10-01 11:30', status: 'pending' },
    { customer: 'Carol Danvers', service: 'Facial', date: '2023-10-01 13:00', status: 'completed' },
  ];
  return (
    <div>
      <div style={{display:'flex', justifyContent:'space-between', marginBottom:'2rem'}}>
        <h2>Appointments</h2>
        <button className="glass" style={{padding:'0.5rem 1rem', cursor:'pointer', color:'white', background:'var(--primary)'}}>New Appointment</button>
      </div>
      <DataTable columns={cols} data={data} />
    </div>
  );
};
export default AppointmentsPage;\n