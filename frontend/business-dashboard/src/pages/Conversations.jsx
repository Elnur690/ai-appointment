import React, { useState, useEffect } from 'react';
import { DataTable } from '../components/common/DataTable';
import api from '../api/client';
import { Bot, UserCheck, RefreshCw } from 'lucide-react';

const Conversations = () => {
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
    { header: 'Customer', accessor: 'customer' },
    { header: 'Channel', accessor: 'channel' },
    { header: 'Latest Message', accessor: 'last_message' },
    { header: 'Guardrail Status', accessor: 'guardrail' },
    {
      header: 'AI / Human Mode',
      cell: (row) => (
        <button
          type="button"
          className={`btn ${row.ai_active ? 'btn-primary' : 'btn-danger'}`}
          style={{ padding: '4px 10px', fontSize: '12px' }}
          onClick={() => toggleAi(row)}
        >
          {row.ai_active ? (
            <>
              <Bot size={14} /> AI Active
            </>
          ) : (
            <>
              <UserCheck size={14} /> Human Takeover
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
          <h2>Omnichannel Conversations & Guardrail Hand-Offs</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Monitor real-time WhatsApp, Instagram DM, and Facebook Messenger chats. Switch between AI mode and human takeover anytime.
          </p>
        </div>
        <button type="button" className="btn btn-secondary" onClick={loadConversations}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      <DataTable
        columns={columns}
        data={chats}
        emptyMessage="No active customer conversations yet. Pair your WhatsApp number in Settings to start receiving messages."
      />
    </div>
  );
};

export default Conversations;
