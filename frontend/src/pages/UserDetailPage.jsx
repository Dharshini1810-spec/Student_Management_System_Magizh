import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import usersApi from '../api/usersApi';
import rolesApi from '../api/rolesApi';

const ROLE_COLORS = {
  SUPER_ADMIN: 'from-purple-500 to-indigo-600',
  ADMIN: 'from-brand-500 to-brand-700',
  MENTOR: 'from-emerald-500 to-teal-600',
  STUDENT: 'from-sky-500 to-blue-600',
};

const ROLE_LABELS = {
  SUPER_ADMIN: 'Super Admin',
  ADMIN: 'Admin',
  MENTOR: 'Mentor',
  STUDENT: 'Student',
};

export default function UserDetailPage() {
  const { id } = useParams();
  const { isSuperAdmin, user: currentUser } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [userData, setUserData] = useState(null);
  const [permissions, setPermissions] = useState(null);
  const [allPermissions, setAllPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  useEffect(() => {
    fetchUserData();
  }, [id]);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const [userRes, permsRes] = await Promise.all([
        usersApi.getUser(id),
        usersApi.getUserPermissions(id).catch(() => null),
      ]);
      setUserData(userRes.data);

      if (permsRes?.data) {
        setPermissions(permsRes.data);
      }

      // Fetch all permissions list for Super Admin
      if (isSuperAdmin) {
        const allPermsRes = await rolesApi.listPermissions().catch(() => null);
        if (allPermsRes?.data) {
          setAllPermissions(allPermsRes.data);
        }
      }
    } catch (err) {
      toast.error(err.message || 'Failed to load user');
      navigate('/users');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async () => {
    setActionLoading('toggle');
    try {
      if (userData.is_active) {
        await usersApi.deactivateUser(id);
        toast.success('User deactivated');
      } else {
        await usersApi.updateUser(id, { is_active: true });
        toast.success('User activated');
      }
      await fetchUserData();
    } catch (err) {
      toast.error(err.message || 'Action failed');
    } finally {
      setActionLoading(null);
    }
  };

  const handleResetPassword = async () => {
    setActionLoading('reset');
    try {
      const res = await usersApi.adminResetPassword(id);
      toast.success(`Reset token: ${res.data?.reset_token || 'Generated'}`);
    } catch (err) {
      toast.error(err.message || 'Failed to reset password');
    } finally {
      setActionLoading(null);
    }
  };

  const handleAssignPermission = async (permName) => {
    setActionLoading(`assign-${permName}`);
    try {
      await usersApi.assignPermission(id, permName);
      toast.success(`Permission '${permName}' granted`);
      await fetchUserData();
    } catch (err) {
      toast.error(err.message || 'Failed to assign permission');
    } finally {
      setActionLoading(null);
    }
  };

  const handleRevokePermission = async (permName) => {
    setActionLoading(`revoke-${permName}`);
    try {
      await usersApi.revokePermission(id, permName);
      toast.success(`Permission '${permName}' revoked`);
      await fetchUserData();
    } catch (err) {
      toast.error(err.message || 'Failed to revoke permission');
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
            <p className="text-sm text-white/50">Loading user details...</p>
          </div>
        </div>
    );
  }

  if (!userData) return null;

  const roleGradient = ROLE_COLORS[userData.role] || ROLE_COLORS.STUDENT;
  const roleLabel = ROLE_LABELS[userData.role] || userData.role;
  const isSelf = currentUser?.id === userData.id;

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Back link */}
      <Link
        to="/users"
        className="inline-flex items-center gap-1.5 text-sm text-white/50 hover:text-purple-400 transition-colors font-medium"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Users
      </Link>

      {/* User Profile Card */}
      <div className="card overflow-hidden !p-0">
        {/* Header band */}
        <div className={`h-24 bg-gradient-to-r ${roleGradient} relative`}>
          <div className="absolute -bottom-8 left-6">
            <div className={`
              w-16 h-16 rounded-2xl bg-gradient-to-br ${roleGradient}
              flex items-center justify-center text-white text-2xl font-bold
              shadow-lg border-4 border-slate-800
            `}>
              {userData.email?.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>

        <div className="pt-12 px-6 pb-6">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-white">{userData.email}</h1>
              <div className="flex items-center gap-2 mt-1">
                <span className={`badge ${userData.role === 'SUPER_ADMIN' ? 'badge-brand' : userData.role === 'ADMIN' ? 'badge-brand' : userData.role === 'MENTOR' ? 'badge-info' : 'badge-info'}`}>
                  {roleLabel}
                </span>
                {userData.is_active ? (
                  <span className="badge-success">Active</span>
                ) : (
                  <span className="badge-danger">Inactive</span>
                )}
                {userData.is_first_login && (
                  <span className="badge-warning">First Login Pending</span>
                )}
              </div>
            </div>

            {/* Actions */}
            {isSuperAdmin && !isSelf && userData.role !== 'SUPER_ADMIN' && (
              <div className="flex gap-2">
                <button
                  onClick={handleToggleActive}
                  disabled={actionLoading === 'toggle'}
                  className={`text-sm font-medium px-4 py-2 rounded-xl transition-all duration-200 ${
                    userData.is_active
                      ? 'btn-danger text-sm py-2'
                      : 'btn-primary text-sm py-2'
                  }`}
                >
                  {actionLoading === 'toggle'
                    ? 'Processing...'
                    : userData.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <button
                  onClick={handleResetPassword}
                  disabled={actionLoading === 'reset'}
                  className="btn-secondary text-sm py-2"
                >
                  {actionLoading === 'reset' ? 'Resetting...' : 'Reset Password'}
                </button>
              </div>
            )}
          </div>

          {/* User Details Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6 p-4 bg-white/5 rounded-xl">
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">User ID</p>
              <p className="text-sm text-white/90 font-mono">{userData.id}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">Email</p>
              <p className="text-sm text-white/90">{userData.email}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">Created At</p>
              <p className="text-sm text-white/90">
                {new Date(userData.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">Updated At</p>
              <p className="text-sm text-white/90">
                {new Date(userData.updated_at).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Permissions Panel */}
      {permissions && (
        <div className="card">
          <h2 className="section-title mb-4">Permissions</h2>

          {/* Role permissions */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-white/60 mb-2">Role Permissions ({roleLabel})</h3>
            <div className="flex flex-wrap gap-2">
              {permissions.role_permissions?.length > 0 ? (
                permissions.role_permissions.map((p) => (
                  <span key={p} className="badge-brand">{p}</span>
                ))
              ) : (
                <span className="text-xs text-white/40">No role permissions</span>
              )}
            </div>
          </div>

          {/* Direct permissions */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-white/60 mb-2">Direct Permissions</h3>
            <div className="flex flex-wrap gap-2">
              {permissions.direct_permissions?.length > 0 ? (
                permissions.direct_permissions.map((p) => (
                  <span key={p} className="inline-flex items-center gap-1.5 badge-info">
                    {p}
                    {isSuperAdmin && (
                      <button
                        onClick={() => handleRevokePermission(p)}
                        disabled={actionLoading === `revoke-${p}`}
                        className="text-sky-300 hover:text-rose-400 transition-colors"
                        title="Revoke"
                      >
                        ×
                      </button>
                    )}
                  </span>
                ))
              ) : (
                <span className="text-xs text-white/40">No direct permissions</span>
              )}
            </div>
          </div>

          {/* Assign permissions (Super Admin) */}
          {isSuperAdmin && allPermissions.length > 0 && (
            <div className="border-t border-white/5 pt-4">
              <h3 className="text-sm font-semibold text-white/60 mb-3">Grant Permission</h3>
              <div className="flex flex-wrap gap-2">
                {allPermissions
                  .filter((p) => !permissions.all_permissions?.includes(p.name))
                  .map((p) => (
                    <button
                      key={p.name}
                      onClick={() => handleAssignPermission(p.name)}
                      disabled={actionLoading === `assign-${p.name}`}
                      className="text-xs px-3 py-1.5 rounded-lg border border-dashed border-white/20
                                 text-white/50 hover:border-purple-400 hover:text-purple-300 hover:bg-purple-500/10
                                 transition-all duration-200"
                      title={p.description}
                    >
                      + {p.name}
                    </button>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
