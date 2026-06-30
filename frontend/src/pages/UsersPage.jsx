import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import usersApi from '../api/usersApi';

const ROLE_BADGES = {
  SUPER_ADMIN: { bg: 'bg-purple-500/20', text: 'text-purple-300', border: 'border-purple-500/30' },
  ADMIN: { bg: 'bg-brand-500/20', text: 'text-brand-300', border: 'border-brand-500/30' },
  MENTOR: { bg: 'bg-emerald-500/20', text: 'text-emerald-300', border: 'border-emerald-500/30' },
  STUDENT: { bg: 'bg-sky-500/20', text: 'text-sky-300', border: 'border-sky-500/30' },
};

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
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
      const res = await usersApi.listUsers({ page_size: 50 });
      setUsers(res.data || []);
    } catch (err) {
      toast.error(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (user) => {
    setActionLoading(`toggle-${user.id}`);
    try {
      if (user.is_active) {
        await usersApi.deactivateUser(user.id);
        toast.success(`User ${user.email} has been deactivated`);
      } else {
        await usersApi.updateUser(user.id, { is_active: true });
        toast.success(`User ${user.email} has been activated`);
      }
      await fetchUsers();
    } catch (err) {
      toast.error(err.message || 'Failed to update user status');
    } finally {
      setActionLoading(null);
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
          <h1 className="page-title">User Management</h1>
          <p className="text-sm text-white/50 mt-1">
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
          <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
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
        <div className="flex gap-1 bg-white/5 rounded-xl p-1">
          {roleTabs.map((role) => (
            <button
              key={role}
              onClick={() => setRoleFilter(role)}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200
                ${roleFilter === role
                  ? 'bg-white/10 text-white shadow-sm'
                  : 'text-white/50 hover:text-white/80'
                }
              `}
            >
              {role === 'ALL' ? 'All' : role === 'SUPER_ADMIN' ? 'Super Admin' : role.charAt(0) + role.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Users table */}
      <div className="table-container">
        {loading ? (
          <div className="p-12 text-center">
            <div className="inline-flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
              <p className="text-sm text-white/50">Loading users...</p>
            </div>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-white/40 text-sm">No users found matching your criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full" id="users-table">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="table-header text-left py-3.5 px-5">User</th>
                  <th className="table-header text-left py-3.5 px-5">Role</th>
                  <th className="table-header text-left py-3.5 px-5">Status</th>
                  <th className="table-header text-left py-3.5 px-5">Created</th>
                  <th className="table-header text-right py-3.5 px-5">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredUsers.map((u, i) => {
                  const badge = ROLE_BADGES[u.role] || ROLE_BADGES.STUDENT;
                  return (
                    <tr
                      key={u.id}
                      className="table-row animate-slide-up"
                      style={{ animationDelay: `${i * 30}ms` }}
                    >
                      <td className="py-3.5 px-5">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-lg">
                            {u.email?.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-white/90">{u.email}</p>
                            <p className="text-xs text-white/40 font-mono">{u.id?.substring(0, 8)}...</p>
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
                        <span className="text-sm text-white/50">
                          {new Date(u.created_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </span>
                      </td>
                      <td className="py-3.5 px-5 text-right space-y-2 sm:space-y-0 sm:flex sm:items-center sm:justify-end sm:gap-2">
                        <Link
                          to={`/users/${u.id}`}
                          className="text-sm font-medium text-purple-400 hover:text-purple-300 transition-colors"
                        >
                          View
                        </Link>
                        {isSuperAdmin && u.role !== 'SUPER_ADMIN' && (
                          <>
                            <button
                              type="button"
                              onClick={() => handleToggleActive(u)}
                              disabled={actionLoading === `toggle-${u.id}`}
                              className="text-sm font-medium text-white/50 hover:text-white/80 transition-colors"
                            >
                              {actionLoading === `toggle-${u.id}` ? 'Updating…' : u.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                          </>
                        )}
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
