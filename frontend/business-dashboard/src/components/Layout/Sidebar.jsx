import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Calendar, Users, Briefcase, Users2, MessageSquare, BookOpen, CreditCard, Settings } from 'lucide-react';
import './Layout.css';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/calendar', icon: Calendar, label: 'Calendar' },
  { path: '/appointments', icon: Users, label: 'Appointments' },
  { path: '/staff', icon: Users2, label: 'Staff' },
  { path: '/services', icon: Briefcase, label: 'Services' },
  { path: '/customers', icon: Users, label: 'Customers' },
  { path: '/conversations', icon: MessageSquare, label: 'Conversations' },
  { path: '/knowledge', icon: BookOpen, label: 'Knowledge Base' },
  { path: '/payments', icon: CreditCard, label: 'Payments' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const Sidebar = () => {
  const { businessContext } = useAuthStore();
  return (
    <div className="sidebar glass">
      <div className="sidebar-header">
        <h2 className="text-gradient">{businessContext.name}</h2>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <NavLink key={item.path} to={item.path} className={({isActive}) => `nav-item ${isActive ? 'active' : ''}`}>
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};\n