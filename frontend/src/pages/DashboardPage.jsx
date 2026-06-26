import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import usersApi from '../api/usersApi';
import client from '../api/client';

const ROLE_BADGES = {
  SUPER_ADMIN: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', label: 'Super Admin' },
  ADMIN: { bg: 'bg-brand-50', text: 'text-brand-700', border: 'border-brand-200', label: 'Admin' },
  MENTOR: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', label: 'Mentor' },
  STUDENT: { bg: 'bg-sky-50', text: 'text-sky-700', border: 'border-sky-200', label: 'Student' },
};

export default function DashboardPage() {
  const { user, isAdmin, isSuperAdmin } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentUsers, setRecentUsers] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const healthRes = await client.get('/health').catch(() => null);
        setHealth(healthRes?.data || null);

        if (isAdmin) {
          const usersRes = await usersApi.listUsers({ page_size: 20 });
          const users = usersRes.data || [];
          setStats({
            total: users.length,
            active: users.filter((u) => u.is_active).length,
            inactive: users.filter((u) => !u.is_active).length,
            admins: users.filter((u) => u.role === 'ADMIN').length,
            mentors: users.filter((u) => u.role === 'MENTOR').length,
            students: users.filter((u) => u.role === 'STUDENT').length,
          });
          setRecentUsers(
            [...users]
              .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
              .slice(0, 5),
          );
        }
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [isAdmin]);

  const roleBadge = ROLE_BADGES[user?.role] || ROLE_BADGES.STUDENT;

  const statCards = stats
    ? [
      { label: 'Total Users', value: stats.total, icon: '👥', color: 'from-brand-500 to-brand-700' },
      { label: 'Active Users', value: stats.active, icon: '✓', color: 'from-emerald-500 to-emerald-700' },
      { label: 'Mentors', value: stats.mentors, icon: '🎓', color: 'from-teal-500 to-teal-700' },
      { label: 'Students', value: stats.students, icon: '📚', color: 'from-sky-500 to-sky-700' },
    ]
    : [];

  return (
    <div className="space-y-8">
      {/* Welcome banner */}
      <div className="bg-gradient-to-r from-brand-800 via-brand-700 to-purple-700 rounded-2xl p-8 md:p-10 text-white shadow-xl shadow-brand-900/20 relative overflow-hidden animate-fade-in">
        {/* Decorative circles */}
        <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full" />
        <div className="absolute -bottom-16 -right-16 w-64 h-64 bg-white/5 rounded-full" />
        <div className="absolute top-1/2 right-1/4 w-20 h-20 bg-white/5 rounded-full" />

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              Welcome back!
            </h1>
            <span className={`
              inline-flex items-center px-3 py-1 rounded-full text-xs font-bold
              ${roleBadge.bg} ${roleBadge.text} ${roleBadge.border} border
            `}>
              {roleBadge.label}
            </span>
          </div>
          <p className="text-brand-100 max-w-xl text-sm md:text-base">
            {user?.email} — You are signed in as <strong>{roleBadge.label}</strong>.
            {isAdmin
              ? ' You have access to user management and system administration.'
              : ' You can view your profile and change your password.'}
          </p>
        </div>
      </div>

      {/* Stats Grid (admin only) */}
      {isAdmin && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="bg-white rounded-xl border border-slate-100 p-6 animate-pulse"
              >
                <div className="h-4 bg-slate-200 rounded w-20 mb-4" />
                <div className="h-8 bg-slate-200 rounded w-14" />
              </div>
            ))
            : statCards.map((card, i) => (
              <div
                key={card.label}
                className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-0.5 animate-slide-up"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-slate-500">{card.label}</span>
                  <span className={`
                      inline-flex items-center justify-center w-9 h-9 rounded-lg
                      bg-gradient-to-br ${card.color} text-white text-sm shadow-sm
                    `}>
                    {card.icon}
                  </span>
                </div>
                <p className="text-3xl font-extrabold text-slate-800">{card.value}</p>
              </div>
            ))}
        </div>
      )}

      {/* Quick Actions + Health */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm animate-slide-up animation-delay-200">
          <h2 className="text-lg font-bold text-slate-800 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            {isSuperAdmin && (
              <Link
                to="/users/new"
                className="flex items-center gap-3 px-4 py-3 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 font-medium text-sm transition-all duration-200 group"
              >
                <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                Create New User
              </Link>
            )}
            {isAdmin && (
              <Link
                to="/users"
                className="flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 font-medium text-sm transition-all duration-200 group"
              >
                <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Manage Users
              </Link>
            )}
            <Link
              to="/profile"
              className="flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 font-medium text-sm transition-all duration-200 group"
            >
              <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              View Profile
            </Link>
          </div>
        </div>

        {/* Backend Health */}
        <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm animate-slide-up animation-delay-300">
          <h2 className="text-lg font-bold text-slate-800 mb-4">System Health</h2>
          {loading ? (
            <div className="flex items-center gap-2 text-slate-400">
              <div className="w-4 h-4 border-2 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
              <span className="text-sm">Checking services...</span>
            </div>
          ) : health ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2 px-4 py-3 bg-emerald-50 border border-emerald-100 rounded-xl">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-sm font-semibold text-emerald-800">All systems operational</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs font-medium text-slate-500 mb-0.5">API Server</p>
                  <p className="text-sm font-bold text-emerald-600 uppercase">{health?.services?.api || 'UP'}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs font-medium text-slate-500 mb-0.5">Database</p>
                  <p className="text-sm font-bold text-emerald-600 uppercase">{health?.services?.database || 'UP'}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-4 py-3 bg-rose-50 border border-rose-100 rounded-xl">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-500 animate-pulse" />
              <span className="text-sm font-semibold text-rose-800">Backend unreachable</span>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      {isAdmin && (
        <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm animate-slide-up animation-delay-400">
          <div className="flex items-center justify-between gap-4 mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-800">Recent Activity</h2>
              <p className="text-sm text-slate-500">Latest account events from recent user activity.</p>
            </div>
            <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
              Updated in real-time
            </span>
          </div>

          {recentUsers.length === 0 ? (
            <div className="text-sm text-slate-500">No recent activity available yet.</div>
          ) : (
            <div className="space-y-3">
              {recentUsers.map((u) => (
                <div key={u.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-2xl bg-slate-50 border border-slate-100">
                  <div>
                    <p className="text-sm font-semibold text-slate-800">{u.email}</p>
                    <p className="text-xs text-slate-500">
                      {u.role === 'SUPER_ADMIN' ? 'Super Admin' : u.role.charAt(0) + u.role.slice(1).toLowerCase()} • Created {new Date(u.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="inline-flex items-center gap-2 text-xs font-medium text-slate-500">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-1 ${u.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span className="text-slate-400">{u.is_first_login ? 'First login pending' : 'Active account'}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Technology footer */}
      <div className="bg-white rounded-xl border border-slate-100 p-6 shadow-sm animate-slide-up animation-delay-500">
        <h2 className="text-lg font-bold text-slate-800 mb-4">Technology Stack</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { name: 'FastAPI', desc: 'Backend', icon: '⚡' },
            { name: 'SQLAlchemy 2.0', desc: 'ORM', icon: '🗄️' },
            { name: 'React + Vite', desc: 'Frontend', icon: '⚛️' },
            { name: 'JWT Auth', desc: 'Security', icon: '🔐' },
          ].map((tech) => (
            <div key={tech.name} className="bg-slate-50 rounded-xl p-4 border border-slate-100 hover:border-brand-200 transition-colors">
              <span className="text-xl mb-2 block">{tech.icon}</span>
              <p className="text-sm font-semibold text-slate-800">{tech.name}</p>
              <p className="text-xs text-slate-500">{tech.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
