import React, { useState, useEffect, useCallback } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import notificationsApi from '../api/notificationsApi';

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
  notifications: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
  ),
  dailyContent: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  ),
  reports: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  activity: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  todos: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
    </svg>
  ),
  projects: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    </svg>
  ),
  attendance: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
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
  referral: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
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
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUnread = useCallback(async () => {
    try {
      const res = await notificationsApi.getUnreadCount();
      setUnreadCount(res.data?.unread_count || 0);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, [fetchUnread]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const canViewReports = isAdmin || user?.role === 'SUPER_ADMIN' || user?.role === 'MENTOR' || user?.role === 'STUDENT';
  const canViewReferralLinks = user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN' || user?.role === 'MENTOR';

  const navItems = [
    { to: '/', icon: icons.dashboard, label: 'Dashboard', show: true },
    { to: '/notifications', icon: icons.notifications, label: 'Notifications', show: true, badge: unreadCount },
    { to: '/daily-content', icon: icons.dailyContent, label: 'Daily Content', show: true },
    { to: '/reports', icon: icons.reports, label: 'Reports', show: canViewReports },
    { to: '/activity', icon: icons.activity, label: 'Activity', show: true },
    { to: '/todos', icon: icons.todos, label: 'Todos', show: true },
    { to: '/projects', icon: icons.projects, label: 'Projects', show: true },
    { to: '/attendance', icon: icons.attendance, label: 'Attendance', show: true },
    { to: '/referral-links', icon: icons.referral, label: 'Referral Links', show: canViewReferralLinks },
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
        flex flex-col bg-slate-900/90 border-r border-white/5 backdrop-blur-xl h-screen sticky top-0
        transition-all duration-300 ease-in-out z-40
      `}
    >
      {/* Logo / Brand */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-white/5 flex-shrink-0">
        <div className={`
          h-9 w-9 rounded-xl bg-gradient-to-br ${roleGradient}
          flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-purple-500/20 flex-shrink-0
        `}>
          M
        </div>
        {!collapsed && (
          <span className="font-bold text-white tracking-tight text-lg whitespace-nowrap animate-fade-in">
            Student Management
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
                ? 'bg-purple-500/15 text-purple-300 shadow-sm shadow-purple-500/10'
                : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }
            `}
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-gradient-to-b from-purple-400 to-pink-400 rounded-r-full shadow-lg shadow-purple-500/30" />
                )}
                <span className={`flex-shrink-0 transition-colors ${isActive ? 'text-purple-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                  {item.icon}
                </span>
                {!collapsed && (
                  <span className="whitespace-nowrap flex-1">{item.label}</span>
                )}
                {item.badge > 0 && (
                  <span className={`flex-shrink-0 min-w-[20px] h-5 px-1.5 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center ${collapsed ? '' : ''}`}>
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom section — user info + collapse */}
      <div className="border-t border-white/5 p-3 space-y-2 flex-shrink-0">
        {/* User info */}
        <div className={`
          flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/5
          ${collapsed ? 'justify-center' : ''}
        `}>
          <div className={`
            h-8 w-8 rounded-lg bg-gradient-to-br ${roleGradient}
            flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-lg
          `}>
            {initials}
          </div>
          {!collapsed && (
            <div className="min-w-0 animate-fade-in">
              <p className="text-sm font-semibold text-white truncate">
                {user?.email}
              </p>
              <p className="text-xs text-slate-400">{roleLabel}</p>
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className={`flex ${collapsed ? 'flex-col' : ''} gap-1`}>
          <button
            onClick={handleLogout}
            className={`
              flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium
              text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-all duration-200
              ${collapsed ? 'justify-center w-full' : 'flex-1'}
            `}
            title="Logout"
          >
            {icons.logout}
            {!collapsed && <span>Logout</span>}
          </button>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center justify-center p-2 rounded-xl text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-all duration-200"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? icons.expand : icons.collapse}
          </button>
        </div>
      </div>
    </aside>
  );
}
