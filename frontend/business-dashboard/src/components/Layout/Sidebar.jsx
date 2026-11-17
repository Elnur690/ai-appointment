import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  Users,
  Briefcase,
  Users2,
  MessageSquare,
  BookOpen,
  CreditCard,
  Settings,
} from 'lucide-react';
import './Layout.css';
import { useAuthStore } from '../../store/authStore';
import { UI_TEXT } from '../../i18n/translations';
import { BrandLogo } from '../common/BrandLogo';

export const Sidebar = () => {
  const { businessContext, language } = useAuthStore();
  const lang = language || 'az';
  const t = (UI_TEXT[lang] || UI_TEXT.az).sidebar;

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: t.dashboard },
    { path: '/calendar', icon: Calendar, label: t.calendar },
    { path: '/appointments', icon: Users, label: t.appointments },
    { path: '/staff', icon: Users2, label: t.staff },
    { path: '/services', icon: Briefcase, label: t.services },
    { path: '/customers', icon: Users, label: t.customers },
    { path: '/conversations', icon: MessageSquare, label: t.conversations },
    { path: '/knowledge', icon: BookOpen, label: t.knowledge },
    { path: '/payments', icon: CreditCard, label: t.payments },
    { path: '/settings', icon: Settings, label: t.settings },
  ];

  return (
    <div className="sidebar glass">
      <div className="sidebar-header">
        <NavLink to="/" style={{ textDecoration: 'none' }}>
          <BrandLogo size={34} fontSize="1.25rem" label={businessContext?.name || 'Randevu.vip'} />
        </NavLink>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};
