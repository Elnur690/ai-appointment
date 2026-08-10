import React from 'react';

export const DataTable = ({ columns, data }) => (
  <div className="glass" style={{ overflow: 'hidden' }}>
    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
      <thead style={{ backgroundColor: 'rgba(255,255,255,0.05)', borderBottom: '1px solid var(--border)' }}>
        <tr>
          {columns.map((col, i) => (
            <th key={i} style={{ padding: '1rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
            {columns.map((col, j) => (
              <td key={j} style={{ padding: '1rem' }}>{col.cell ? col.cell(row) : row[col.accessor]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);\n