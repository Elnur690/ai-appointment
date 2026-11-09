import React, { useState } from 'react';
import { DataTable } from '../components/common/DataTable';
import { Bot, UserCheck } from 'lucide-react';

const Conversations = () => {
  const [chats, setChats] = useState([
    { id: 'c1', customer: '+994 50 211 44 55 (Murad)', channel: 'WhatsApp', lastMsg: 'Sabah saat 16:00-da yer var?', aiActive: true, guardrail: 'In-Scope (Booking)' },
    { id: 'c2', customer: '+994 55 322 11 99 (Nigar)', channel: 'WhatsApp', lastMsg: 'Dəri allergiyam var, hansı dərmanı məsləhət görürsünüz?', aiActive: false, guardrail: 'Out-of-Scope (Human Takeover)' },
    { id: 'c3', customer: '@aysel_baku', channel: 'Instagram DM', lastMsg: 'Balayage qiyməti nə qədərdir?', aiActive: true, guardrail: 'In-Scope (Catalog)' },
  ]);

  const toggleAi = (id) => {
    setChats(chats.map((c) => (c.id === id ? { ...c, aiActive: !c.aiActive } : c)));
  };

  const columns = [
    { header: 'Customer', accessor: 'customer' },
    { header: 'Channel', accessor: 'channel' },
    { header: 'Latest Message', accessor: 'lastMsg' },
    { header: 'Guardrail Status', accessor: 'guardrail' },
    {
      header: 'AI / Human Mode',
      cell: (row) => (
        <button
          className={`btn ${row.aiActive ? 'btn-primary' : 'btn-danger'}`}
          style={{ padding: '4px 10px', fontSize: '12px' }}
          onClick={() => toggleAi(row.id)}
        >
          {row.aiActive ? <><Bot size={14} /> AI Active</> : <><UserCheck size={14} /> Human Takeover</>}
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
            Monitor WhatsApp, Instagram DM, and Facebook Messenger chats. Out-of-scope queries pause the bot automatically for human reply.
          </p>
        </div>
      </div>
      <DataTable columns={columns} data={chats} />
    </div>
  );
};

export default Conversations;
