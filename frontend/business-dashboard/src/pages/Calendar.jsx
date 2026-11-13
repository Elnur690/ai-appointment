import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/common/StatusBadge';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';

const CalendarPage = () => {
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadSchedule = async (dateStr) => {
    setLoading(true);
    try {
      const startIso = `${dateStr}T00:00:00`;
      const endIso = `${dateStr}T23:59:59`;
      const res = await api.get('/appointments/calendar', {
        params: { start_date: startIso, end_date: endIso },
      });
      setAppointments(res.data || []);
    } catch {
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedule(selectedDate);
  }, [selectedDate]);

  const shiftDay = (delta) => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + delta);
    setSelectedDate(d.toISOString().slice(0, 10));
  };

  const hours = Array.from({ length: 13 }, (_, idx) => idx + 9); // 09:00 to 21:00

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2>Schedule Calendar</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Real-time daily schedule synchronized with WhatsApp & Instagram bookings.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button type="button" className="btn btn-secondary" onClick={() => shiftDay(-1)}>
            <ChevronLeft size={16} />
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CalendarIcon size={18} color="var(--primary)" />
            <input
              type="date"
              className="form-control"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>
          <button type="button" className="btn btn-secondary" onClick={() => shiftDay(1)}>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      <div className="glass" style={{ padding: '1.5rem' }}>
        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Loading schedule...</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {hours.map((hour) => {
              const slotAppts = appointments.filter((a) => {
                if (!a.start_time) return false;
                const h = new Date(a.start_time).getHours();
                return h === hour;
              });
              const label = `${String(hour).padStart(2, '0')}:00`;
              return (
                <div
                  key={hour}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '90px 1fr',
                    gap: '1rem',
                    padding: '0.75rem',
                    borderBottom: '1px solid var(--border)',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ fontFamily: 'monospace', color: 'var(--text-secondary)', fontWeight: 600 }}>
                    {label}
                  </span>
                  {slotAppts.length === 0 ? (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Available</span>
                  ) : (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                      {slotAppts.map((appt) => (
                        <div
                          key={appt.id}
                          className="glass-card"
                          style={{ padding: '0.65rem 1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}
                        >
                          <div>
                            <div style={{ fontWeight: 600 }}>{appt.customer_name}</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                              {appt.service_name} • {appt.staff_name}
                            </div>
                          </div>
                          <StatusBadge status={appt.status} />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
export default CalendarPage;
