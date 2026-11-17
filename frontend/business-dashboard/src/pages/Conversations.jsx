import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import { useAuthStore } from '../store/authStore';
import api from '../api/client';
import { Bot, UserCheck, RefreshCw } from 'lucide-react';

const Conversations = () => {
  const { language } = useAuthStore();
  const isAz = (language || 'az') !== 'en';
  const [chats, setChats] = useState([]);

  const loadConversations = async () => {
    try {
      const res = await api.get('/conversations/');
      setChats(res.data || []);
    } catch {
      setChats([]);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  const toggleAi = async (row) => {
    if (row.ai_active) {
      await api.post(`/conversations/${row.id}/takeover`);
    } else {
      await api.post(`/conversations/${row.id}/release`);
    }
    await loadConversations();
  };

  const columns = [
    { header: isAz ? 'Müştəri' : 'Customer', accessor: 'customer' },
    { header: isAz ? 'Kanal' : 'Channel', accessor: 'channel' },
    { header: isAz ? 'Son Mesaj' : 'Latest Message', accessor: 'last_message' },
    { header: isAz ? 'Təhlükəsizlik (Guardrail)' : 'Guardrail Status', accessor: 'guardrail' },
    {
      header: isAz ? 'AI / Operator Rejimi' : 'AI / Human Mode',
      cell: (row) => (
        <button
          type="button"
          className={`btn ${row.ai_active ? 'btn-primary' : 'btn-danger'}`}
          style={{ padding: '4px 10px', fontSize: '12px' }}
          onClick={() => toggleAi(row)}
        >
          {row.ai_active ? (
            <>
              <Bot size={14} /> {isAz ? 'AI Aktivdir' : 'AI Active'}
            </>
          ) : (
            <>
              <UserCheck size={14} /> {isAz ? 'Canlı Operator' : 'Human Takeover'}
            </>
          )}
        </button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>
            {isAz
              ? 'Omnikanal Söhbətlər və Canlı Operatora Keçid'
              : 'Omnichannel Conversations & Guardrail Hand-Offs'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {isAz
              ? 'WhatsApp, Instagram Direct və Telegram yazışmalarını canlı izləyin. İstənilən an bir kliklə AI rejimindən canlı operator rejiminə keçin.'
              : 'Monitor real-time WhatsApp, Instagram DM, and Telegram chats. Switch between AI mode and human takeover anytime.'}
          </p>
        </div>
        <button type="button" className="btn btn-secondary" onClick={loadConversations}>
          <RefreshCw size={16} />
          {isAz ? 'Yenilə' : 'Refresh'}
        </button>
      </div>
      <DataTable
        columns={columns}
        data={chats}
        emptyMessage={
          isAz
            ? 'Hələ aktiv müştəri yazışması yoxdur. Mesajları qəbul etmək üçün Tənzimləmələrdən WhatsApp, Instagram və ya Telegram qoşun.'
            : 'No active customer conversations yet. Pair your WhatsApp, Instagram, or Telegram in Settings to start receiving messages.'
        }
      />
    </div>
  );
};

export default Conversations;
