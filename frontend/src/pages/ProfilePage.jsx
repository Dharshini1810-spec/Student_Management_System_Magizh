import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import authApi from '../api/authApi';

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

export default function ProfilePage() {
  const { user, isAdmin, isSuperAdmin } = useAuth();
  const toast = useToast();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const passwordValid = newPassword.length >= 8;
  const passwordsMatch = newPassword === confirmPassword;

  const handleChangePassword = async (e) => {
    e.preventDefault();

    if (!passwordValid) {
      toast.warning('New password must be at least 8 characters');
      return;
    }
    if (!passwordsMatch) {
      toast.warning('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await authApi.changePassword(currentPassword, newPassword);
      toast.success('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setShowPasswordForm(false);
    } catch (err) {
      toast.error(err.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  const roleGradient = ROLE_COLORS[user.role] || ROLE_COLORS.STUDENT;
  const roleLabel = ROLE_LABELS[user.role] || user.role;

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <h1 className="page-title">My Profile</h1>

      {/* Profile Card */}
      <div className="card overflow-hidden !p-0">
        <div className={`h-20 bg-gradient-to-r ${roleGradient} relative`}>
          <div className="absolute -bottom-8 left-6">
            <div className={`
              w-16 h-16 rounded-2xl bg-gradient-to-br ${roleGradient}
              flex items-center justify-center text-white text-2xl font-bold
              shadow-lg border-4 border-slate-800
            `}>
              {user.email?.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>

        <div className="pt-12 px-6 pb-6">
          <h2 className="text-lg font-bold text-white">{user.name || user.email}</h2>
          {user.name && <p className="text-sm text-white/50 mt-0.5">{user.email}</p>}
          <div className="flex items-center gap-2 mt-1">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
              user.role === 'SUPER_ADMIN' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' :
              user.role === 'ADMIN' ? 'bg-brand-500/20 text-brand-300 border-brand-500/30' :
              user.role === 'MENTOR' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
              'bg-sky-500/20 text-sky-300 border-sky-500/30'
            }`}>
              {roleLabel}
            </span>
            {user.is_active ? (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Active</span>
            ) : (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30">Inactive</span>
            )}
            {user.is_first_login && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">First Login</span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6 p-4 bg-white/5 rounded-xl">
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">User ID</p>
              <p className="text-sm text-white/90 font-mono">{user.id}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">Email</p>
              <p className="text-sm text-white/90">{user.email}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">Account Created</p>
              <p className="text-sm text-white/90">
                {new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-white/50 mb-0.5">Last Updated</p>
              <p className="text-sm text-white/90">
                {new Date(user.updated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            {isSuperAdmin && (
              <div className="sm:col-span-2">
                <p className="text-xs font-medium text-white/50 mb-0.5">Role Description</p>
                <p className="text-sm text-white/70">Full system access. Can create, update, and delete users of all roles. Manages all permissions and system settings.</p>
              </div>
            )}
            {user.role === 'ADMIN' && (
              <div className="sm:col-span-2">
                <p className="text-xs font-medium text-white/50 mb-0.5">Role Description</p>
                <p className="text-sm text-white/70">User and student management. Assigns tasks and projects to mentors and students. Manages attendance requests and monitors system activity.</p>
              </div>
            )}
            {user.role === 'MENTOR' && (
              <div className="sm:col-span-2">
                <p className="text-xs font-medium text-white/50 mb-0.5">Role Description</p>
                <p className="text-sm text-white/70">Manages assigned students. Creates tasks and provides learning resources. Monitors student progress and daily activities.</p>
              </div>
            )}
            {user.role === 'STUDENT' && (
              <div className="sm:col-span-2">
                <p className="text-xs font-medium text-white/50 mb-0.5">Role Description</p>
                <p className="text-sm text-white/70">Completes assigned tasks, projects, and daily content. Records attendance and tracks personal learning progress.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Change Password Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="section-title">Security</h2>
          {!showPasswordForm && (
            <button
              onClick={() => setShowPasswordForm(true)}
              className="btn-secondary text-sm py-2"
            >
              Change Password
            </button>
          )}
        </div>

        {showPasswordForm ? (
          <form onSubmit={handleChangePassword} className="space-y-4 animate-slide-down" id="profile-change-password-form">
            <div>
              <label htmlFor="profile-current-password" className="block text-sm font-medium text-white/80 mb-1.5">
                Current Password
              </label>
              <input
                id="profile-current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="input-field"
                placeholder="Enter current password"
              />
            </div>
            <div>
              <label htmlFor="profile-new-password" className="block text-sm font-medium text-white/80 mb-1.5">
                New Password
              </label>
              <input
                id="profile-new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="input-field"
                placeholder="Min 8 characters"
              />
              {newPassword && !passwordValid && (
                <p className="text-xs text-rose-400 mt-1">Must be at least 8 characters</p>
              )}
            </div>
            <div>
              <label htmlFor="profile-confirm-password" className="block text-sm font-medium text-white/80 mb-1.5">
                Confirm New Password
              </label>
              <input
                id="profile-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input-field"
                placeholder="Re-enter new password"
              />
              {confirmPassword && !passwordsMatch && (
                <p className="text-xs text-rose-400 mt-1">Passwords do not match</p>
              )}
            </div>
            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                disabled={loading || !passwordValid || !passwordsMatch}
                className="btn-primary flex items-center gap-2 text-sm"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Update Password'
                )}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowPasswordForm(false);
                  setCurrentPassword('');
                  setNewPassword('');
                  setConfirmPassword('');
                }}
                className="btn-secondary text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <p className="text-sm text-white/50">
            Regularly update your password to keep your account secure.
          </p>
        )}
      </div>
    </div>
  );
}
