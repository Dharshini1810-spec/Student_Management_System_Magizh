import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// SVG icon components for a clean look
const icons = {
  dashboard: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  ),
  users: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  addUser: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
    </svg>
  ),
  profile: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  ),
  logout: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  ),
  collapse: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
    </svg>
  ),
  expand: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
    </svg>
  ),
};

const ROLE_COLORS = {
  SUPER_ADMIN: 'from-purple-600 to-indigo-600',
  ADMIN: 'from-brand-600 to-brand-700',
  MENTOR: 'from-emerald-600 to-teal-600',
  STUDENT: 'from-sky-600 to-blue-600',
};

const ROLE_LABELS = {
  SUPER_ADMIN: 'Super Admin',
  ADMIN: 'Admin',
  MENTOR: 'Mentor',
  STUDENT: 'Student',
};

export default function Sidebar() {
  const { user, isAdmin, isSuperAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/', icon: icons.dashboard, label: 'Dashboard', show: true },
    { to: '/users', icon: icons.users, label: 'Users', show: isAdmin },
    { to: '/users/new', icon: icons.addUser, label: 'Create User', show: isSuperAdmin },
    { to: '/profile', icon: icons.profile, label: 'My Profile', show: true },
  ].filter((item) => item.show);

  const initials = user?.email
    ? user.email.charAt(0).toUpperCase()
    : '?';

  const roleGradient = ROLE_COLORS[user?.role] || ROLE_COLORS.STUDENT;
  const roleLabel = ROLE_LABELS[user?.role] || user?.role;

  return (
    <aside
      className={`
        ${collapsed ? 'w-[72px]' : 'w-64'}
        flex flex-col bg-white border-r border-slate-200 h-screen sticky top-0
        transition-all duration-300 ease-in-out z-40
      `}
    >
      {/* Logo / Brand */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-slate-100 flex-shrink-0">
        <div className={`
          h-9 w-9 rounded-xl bg-gradient-to-br ${roleGradient}
          flex items-center justify-center text-white font-bold text-sm shadow-md flex-shrink-0
        `}>
          M
        </div>
        {!collapsed && (
          <span className="font-bold text-slate-800 tracking-tight text-lg whitespace-nowrap animate-fade-in">
            SMS Magizh
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => `
              flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
              transition-all duration-200 group relative
              ${isActive
                ? 'bg-brand-50 text-brand-700 shadow-sm'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }
            `}
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-brand-600 rounded-r-full" />
                )}
                <span className={`flex-shrink-0 transition-colors ${isActive ? 'text-brand-600' : 'text-slate-400 group-hover:text-slate-600'}`}>
                  {item.icon}
                </span>
                {!collapsed && (
                  <span className="whitespace-nowrap">{item.label}</span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom section — user info + collapse */}
      <div className="border-t border-slate-100 p-3 space-y-2 flex-shrink-0">
        {/* User info */}
        <div className={`
          flex items-center gap-3 px-3 py-2.5 rounded-xl bg-slate-50
          ${collapsed ? 'justify-center' : ''}
        `}>
          <div className={`
            h-8 w-8 rounded-lg bg-gradient-to-br ${roleGradient}
            flex items-center justify-center text-white text-xs font-bold flex-shrink-0
          `}>
            {initials}
          </div>
          {!collapsed && (
            <div className="min-w-0 animate-fade-in">
              <p className="text-sm font-semibold text-slate-800 truncate">
                {user?.email}
              </p>
              <p className="text-xs text-slate-500">{roleLabel}</p>
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className={`flex ${collapsed ? 'flex-col' : ''} gap-1`}>
          <button
            onClick={handleLogout}
            className={`
              flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium
              text-rose-600 hover:bg-rose-50 transition-all duration-200
              ${collapsed ? 'justify-center w-full' : 'flex-1'}
            `}
            title="Logout"
          >
            {icons.logout}
            {!collapsed && <span>Logout</span>}
          </button>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center justify-center p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all duration-200"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? icons.expand : icons.collapse}
          </button>
        </div>
      </div>
    </aside>
  );
}
