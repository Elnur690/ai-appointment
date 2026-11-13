import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { Modal } from '../components/common/Modal';
import api from '../api/client';
import { Clock, Plus } from 'lucide-react';

const Staff = () => {
  const [staff, setStaff] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({
    name: '',
    role_title: 'Specialist',
    shift: 'Full-Day (09:00 - 20:00)',
    overtime_enabled: true,
  });

  const loadStaff = async () => {
    try {
      const res = await api.get('/staff/');
      setStaff(res.data || []);
    } catch {
      setStaff([]);
    }
  };

  useEffect(() => {
    loadStaff();
  }, []);

  const toggleOvertime = async (row) => {
    await api.patch(`/staff/${row.id}`, { overtime_enabled: !row.overtime_enabled });
    await loadStaff();
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/staff/', form);
    setIsModalOpen(false);
    setForm({ name: '', role_title: 'Specialist', shift: 'Full-Day (09:00 - 20:00)', overtime_enabled: true });
    await loadStaff();
  };

  const columns = [
    { header: 'Staff Member', accessor: 'name' },
    { header: 'Role / Specialty', accessor: 'role_title' },
    { header: 'Active Shift', accessor: 'shift' },
    {
      header: 'Overtime Allowed',
      cell: (row) => (
        <button
          type="button"
          className={`btn ${row.overtime_enabled ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '4px 10px', fontSize: '12px' }}
          onClick={() => toggleOvertime(row)}
        >
          <Clock size={14} />
          {row.overtime_enabled ? 'Overtime Enabled' : 'Strict Shift Bounds'}
        </button>
      ),
    },
    { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'confirmed' : 'cancelled'} /> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Staff Roster & Shift-Aware Scheduling</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Configure Morning, Evening, or Full-Day shifts and overtime allowances for your team.
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} />
          Add Staff Member
        </button>
      </div>

      <DataTable
        columns={columns}
        data={staff}
        emptyMessage="No staff members added yet. Click 'Add Staff Member' to add your team."
      />

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Staff Member">
        <form onSubmit={handleCreate}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="Staff member full name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Role / Specialty</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="e.g. Senior Stylist, Dentist, Barber"
              value={form.role_title}
              onChange={(e) => setForm({ ...form, role_title: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Shift Schedule</label>
            <select
              className="form-control"
              value={form.shift}
              onChange={(e) => setForm({ ...form, shift: e.target.value })}
            >
              <option value="Full-Day (09:00 - 20:00)">Full-Day (09:00 - 20:00)</option>
              <option value="Morning (09:00 - 15:00)">Morning (09:00 - 15:00)</option>
              <option value="Evening (15:00 - 21:00)">Evening (15:00 - 21:00)</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={form.overtime_enabled}
                onChange={(e) => setForm({ ...form, overtime_enabled: e.target.checked })}
              />
              <span>Allow overtime bookings outside shift bounds</span>
            </label>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Staff Member
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Staff;
