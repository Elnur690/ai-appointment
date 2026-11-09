import React, { useState } from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { Clock, AlertTriangle, Plus } from 'lucide-react';

const Staff = () => {
  const [staff, setStaff] = useState([
    { id: 1, name: 'Elvin Məmmədov', role: 'Master Barber', shift: 'Morning (09:00 - 15:00)', overtime: true, status: 'confirmed' },
    { id: 2, name: 'Leyla Əliyeva', role: 'Senior Colorist', shift: 'Full-Day (09:00 - 20:00)', overtime: true, status: 'confirmed' },
    { id: 3, name: 'Nigar Həsənova', role: 'Nail & Lash Specialist', shift: 'Evening (15:00 - 21:00)', overtime: false, status: 'confirmed' },
  ]);

  const toggleOvertime = (id) => {
    setStaff(staff.map((s) => (s.id === id ? { ...s, overtime: !s.overtime } : s)));
  };

  const columns = [
    { header: 'Staff Member', accessor: 'name' },
    { header: 'Role / Specialty', accessor: 'role' },
    { header: 'Active Shift', accessor: 'shift' },
    {
      header: 'Overtime Allowed',
      cell: (row) => (
        <button
          className={`btn ${row.overtime ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '4px 10px', fontSize: '12px' }}
          onClick={() => toggleOvertime(row.id)}
        >
          <Clock size={14} />
          {row.overtime ? 'Overtime Enabled' : 'Strict Shift Bounds'}
        </button>
      ),
    },
    { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Staff Roster & Shift-Aware Scheduling</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Configure Morning, Evening, or Full-Day shifts, overtime allowances, and emergency sick-leave swaps.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-danger" onClick={() => alert('Emergency Sick-Leave Reassignment triggered via WhatsApp!')}>
            <AlertTriangle size={16} />
            Emergency Sick-Leave Swap
          </button>
          <button className="btn btn-primary">
            <Plus size={16} />
            Add Staff Member
          </button>
        </div>
      </div>
      <DataTable columns={columns} data={staff} />
    </div>
  );
};

export default Staff;
