import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import usersApi from '../api/usersApi';

const ROLE_BADGES = {
  SUPER_ADMIN: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  ADMIN: { bg: 'bg-brand-50', text: 'text-brand-700', border: 'border-brand-200' },
  MENTOR: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  STUDENT: { bg: 'bg-sky-50', text: 'text-sky-700', border: 'border-sky-200' },
};

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const { isSuperAdmin } = useAuth();
  const toast = useToast();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await usersApi.listUsers();
      setUsers(res.data || []);
    } catch (err) {
      toast.error(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter((u) => {
    const matchSearch =
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      u.role.toLowerCase().includes(search.toLowerCase());
    const matchRole = roleFilter === 'ALL' || u.role === roleFilter;
    return matchSearch && matchRole;
  });

  const roleTabs = ['ALL', 'ADMIN', 'MENTOR', 'STUDENT'];
  if (users.some((u) => u.role === 'SUPER_ADMIN')) {
    roleTabs.splice(1, 0, 'SUPER_ADMIN');
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-800 tracking-tight">User Management</h1>
          <p className="text-sm text-slate-500 mt-1">
            {filteredUsers.length} user{filteredUsers.length !== 1 ? 's' : ''} found
          </p>
        </div>
        {isSuperAdmin && (
          <Link
            to="/users/new"
            className="btn-primary inline-flex items-center gap-2 text-sm"
            id="create-user-btn"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Create User
          </Link>
        )}
      </div>

      {/* Search + Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by email or role..."
            className="input-field pl-10"
            id="user-search"
          />
        </div>

        {/* Role filter tabs */}
        <div className="flex gap-1 bg-slate-100 rounded-xl p-1">
          {roleTabs.map((role) => (
            <button
              key={role}
              onClick={() => setRoleFilter(role)}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200
                ${roleFilter === role
                  ? 'bg-white text-brand-700 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
                }
              `}
            >
              {role === 'ALL' ? 'All' : role === 'SUPER_ADMIN' ? 'Super Admin' : role.charAt(0) + role.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Users table */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <div className="inline-flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
              <p className="text-sm text-slate-500">Loading users...</p>
            </div>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-slate-400 text-sm">No users found matching your criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full" id="users-table">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-3.5 px-5 text-xs font-semibold text-slate-500 uppercase tracking-wider">User</th>
                  <th className="text-left py-3.5 px-5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Role</th>
                  <th className="text-left py-3.5 px-5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                  <th className="text-left py-3.5 px-5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Created</th>
                  <th className="text-right py-3.5 px-5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {filteredUsers.map((u, i) => {
                  const badge = ROLE_BADGES[u.role] || ROLE_BADGES.STUDENT;
                  return (
                    <tr
                      key={u.id}
                      className="hover:bg-slate-50/50 transition-colors animate-slide-up"
                      style={{ animationDelay: `${i * 30}ms` }}
                    >
                      <td className="py-3.5 px-5">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                            {u.email?.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-slate-800">{u.email}</p>
                            <p className="text-xs text-slate-400 font-mono">{u.id?.substring(0, 8)}...</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-5">
                        <span className={`
                          inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border
                          ${badge.bg} ${badge.text} ${badge.border}
                        `}>
                          {u.role === 'SUPER_ADMIN' ? 'Super Admin' : u.role.charAt(0) + u.role.slice(1).toLowerCase()}
                        </span>
                      </td>
                      <td className="py-3.5 px-5">
                        {u.is_active ? (
                          <span className="badge-success">Active</span>
                        ) : (
                          <span className="badge-danger">Inactive</span>
                        )}
                      </td>
                      <td className="py-3.5 px-5">
                        <span className="text-sm text-slate-500">
                          {new Date(u.created_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </span>
                      </td>
                      <td className="py-3.5 px-5 text-right">
                        <Link
                          to={`/users/${u.id}`}
                          className="text-sm font-medium text-brand-600 hover:text-brand-700 transition-colors"
                        >
                          View →
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
