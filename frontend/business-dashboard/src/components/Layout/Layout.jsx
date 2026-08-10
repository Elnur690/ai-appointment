import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Bell, Search, User } from 'lucide-react';
import './Layout.css';

export const Layout = () => {
  return (
    <div className="layout">
      <Sidebar />
      <div className="main-content">
        <header className="topbar glass" style={{borderRadius: 0}}>
          <div className="search-bar">
            <Search size={20} color="var(--text-secondary)" />
            <input type="text" placeholder="Search..." style={{background: 'transparent', border: 'none', color: 'var(--text-primary)', marginLeft: '0.5rem', outline: 'none'}} />
          </div>
          <div style={{display: 'flex', gap: '1.5rem', alignItems: 'center'}}>
            <Bell size={20} style={{cursor: 'pointer'}} />
            <User size={20} style={{cursor: 'pointer'}} />
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};\n