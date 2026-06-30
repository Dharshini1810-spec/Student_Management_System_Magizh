import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import usersApi from '../api/usersApi';
import client from '../api/client';

const ROLE_BADGES = {
  SUPER_ADMIN: { bg: 'bg-purple-500/20', text: 'text-purple-300', border: 'border-purple-500/30', label: 'Super Admin' },
  ADMIN: { bg: 'bg-brand-500/20', text: 'text-brand-300', border: 'border-brand-500/30', label: 'Admin' },
  MENTOR: { bg: 'bg-emerald-500/20', text: 'text-emerald-300', border: 'border-emerald-500/30', label: 'Mentor' },
  STUDENT: { bg: 'bg-sky-500/20', text: 'text-sky-300', border: 'border-sky-500/30', label: 'Student' },
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
              <p className="text-white/70 max-w-xl text-sm md:text-base">
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
                className="glass-card rounded-xl p-6 animate-pulse"
              >
                <div className="h-4 bg-white/10 rounded w-20 mb-4" />
                <div className="h-8 bg-white/10 rounded w-14" />
              </div>
            ))
            : statCards.map((card, i) => (
              <div
                key={card.label}
                className="card hover:shadow-2xl hover:shadow-purple-500/10 transition-all duration-300 hover:-translate-y-0.5 animate-slide-up"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-white/60">{card.label}</span>
                  <span className={`
                      inline-flex items-center justify-center w-9 h-9 rounded-lg
                      bg-gradient-to-br ${card.color} text-white text-sm shadow-lg
                    `}>
                    {card.icon}
                  </span>
                </div>
                <p className="text-3xl font-extrabold text-white">{card.value}</p>
              </div>
            ))}
        </div>
      )}

      {/* Quick Actions + Health */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="card animate-slide-up animation-delay-200">
          <h2 className="text-lg font-bold text-white/90 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            {isSuperAdmin && (
              <Link
                to="/users/new"
                className="flex items-center gap-3 px-4 py-3 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 font-medium text-sm transition-all duration-200 group"
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
                className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white/70 hover:text-white font-medium text-sm transition-all duration-200 group"
              >
                <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Manage Users
              </Link>
            )}
            <Link
              to="/profile"
              className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white/70 hover:text-white font-medium text-sm transition-all duration-200 group"
            >
              <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              View Profile
            </Link>
          </div>
        </div>

        {/* Backend Health */}
        <div className="card animate-slide-up animation-delay-300">
          <h2 className="text-lg font-bold text-white/90 mb-4">System Health</h2>
          {loading ? (
            <div className="flex items-center gap-2 text-white/50">
              <div className="w-4 h-4 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
              <span className="text-sm">Checking services...</span>
            </div>
          ) : health ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2 px-4 py-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-sm font-semibold text-emerald-300">All systems operational</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 rounded-lg p-3">
                  <p className="text-xs font-medium text-white/50 mb-0.5">API Server</p>
                  <p className="text-sm font-bold text-emerald-400 uppercase">{health?.services?.api || 'UP'}</p>
                </div>
                <div className="bg-white/5 rounded-lg p-3">
                  <p className="text-xs font-medium text-white/50 mb-0.5">Database</p>
                  <p className="text-sm font-bold text-emerald-400 uppercase">{health?.services?.database || 'UP'}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-4 py-3 bg-rose-500/10 border border-rose-500/20 rounded-xl">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-400 animate-pulse" />
              <span className="text-sm font-semibold text-rose-300">Backend unreachable</span>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      {isAdmin && (
        <div className="card animate-slide-up animation-delay-400">
          <div className="flex items-center justify-between gap-4 mb-4">
            <div>
              <h2 className="text-lg font-bold text-white/90">Recent Activity</h2>
              <p className="text-sm text-white/50">Latest account events from recent user activity.</p>
            </div>
            <span className="inline-flex items-center rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white/60">
              Updated in real-time
            </span>
          </div>

          {recentUsers.length === 0 ? (
            <div className="text-sm text-white/50">No recent activity available yet.</div>
          ) : (
            <div className="space-y-3">
              {recentUsers.map((u) => (
                <div key={u.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-2xl bg-white/5 border border-white/10">
                  <div>
                    <p className="text-sm font-semibold text-white/90">{u.email}</p>
                    <p className="text-xs text-white/50">
                      {u.role === 'SUPER_ADMIN' ? 'Super Admin' : u.role.charAt(0) + u.role.slice(1).toLowerCase()} • Created {new Date(u.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="inline-flex items-center gap-2 text-xs font-medium text-white/50">
                    <span className={`inline-flex items-center rounded-full px-2.5 py-1 ${u.is_active ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span className="text-white/40">{u.is_first_login ? 'First login pending' : 'Active account'}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Technology footer */}
      <div className="card animate-slide-up animation-delay-500">
        <h2 className="text-lg font-bold text-white/90 mb-4">Technology Stack</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { name: 'FastAPI', desc: 'Backend', icon: '⚡' },
            { name: 'SQLAlchemy 2.0', desc: 'ORM', icon: '🗄️' },
            { name: 'React + Vite', desc: 'Frontend', icon: '⚛️' },
            { name: 'JWT Auth', desc: 'Security', icon: '🔐' },
          ].map((tech) => (
            <div key={tech.name} className="bg-white/5 rounded-xl p-4 border border-white/10 hover:border-purple-500/30 transition-colors">
              <span className="text-xl mb-2 block">{tech.icon}</span>
              <p className="text-sm font-semibold text-white/90">{tech.name}</p>
              <p className="text-xs text-white/50">{tech.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
