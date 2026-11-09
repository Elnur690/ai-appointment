import React from 'react';
import { DataTable } from '../components/common/DataTable';
import { Plus, BookOpen } from 'lucide-react';

const Knowledge = () => {
  const entries = [
    { title: 'Parking & Location (28 May Branch)', type: 'FAQ', content: 'Free underground parking is available right next to 28 Mall entrance.', status: 'Active (pgvector)' },
    { title: 'Late Arrival Policy', type: 'Policy', content: 'Appointments are held for 15 minutes before waitlist auto-backfill activates.', status: 'Active (pgvector)' },
    { title: 'Mistake Correction #14', type: 'Learned Correction', content: 'Keratin treatment takes 120 minutes, not 60 minutes.', status: 'Active (pgvector)' },
  ];

  const columns = [
    { header: 'Knowledge Title', accessor: 'title' },
    { header: 'Type', accessor: 'type' },
    { header: 'Vectorized Content', accessor: 'content' },
    { header: 'RAG Status', accessor: 'status' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>RAG Knowledge Base & "Learn from Mistakes"</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            PostgreSQL pgvector knowledge entries used by the AI Agent to answer business-specific questions accurately.
          </p>
        </div>
        <button className="btn btn-primary">
          <Plus size={16} />
          Add Knowledge Entry
        </button>
      </div>
      <DataTable columns={columns} data={entries} />
    </div>
  );
};

export default Knowledge;
