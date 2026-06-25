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
  const { user } = useAuth();
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
      <h1 className="text-2xl font-extrabold text-slate-800 tracking-tight">My Profile</h1>

      {/* Profile Card */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        <div className={`h-20 bg-gradient-to-r ${roleGradient} relative`}>
          <div className="absolute -bottom-8 left-6">
            <div className={`
              w-16 h-16 rounded-2xl bg-gradient-to-br ${roleGradient}
              flex items-center justify-center text-white text-2xl font-bold
              shadow-lg border-4 border-white
            `}>
              {user.email?.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>

        <div className="pt-12 px-6 pb-6">
          <h2 className="text-lg font-bold text-slate-800">{user.email}</h2>
          <div className="flex items-center gap-2 mt-1">
            <span className={`
              inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border
              ${user.role === 'SUPER_ADMIN' ? 'bg-purple-50 text-purple-700 border-purple-200'
                : user.role === 'ADMIN' ? 'bg-brand-50 text-brand-700 border-brand-200'
                : user.role === 'MENTOR' ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-sky-50 text-sky-700 border-sky-200'}
            `}>
              {roleLabel}
            </span>
            {user.is_active ? (
              <span className="badge-success">Active</span>
            ) : (
              <span className="badge-danger">Inactive</span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6 p-4 bg-slate-50 rounded-xl">
            <div>
              <p className="text-xs font-medium text-slate-500 mb-0.5">User ID</p>
              <p className="text-sm text-slate-800 font-mono">{user.id}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 mb-0.5">Email</p>
              <p className="text-sm text-slate-800">{user.email}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 mb-0.5">Account Created</p>
              <p className="text-sm text-slate-800">
                {new Date(user.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 mb-0.5">Last Updated</p>
              <p className="text-sm text-slate-800">
                {new Date(user.updated_at).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Change Password Section */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-800">Security</h2>
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
              <label htmlFor="profile-current-password" className="block text-sm font-medium text-slate-700 mb-1.5">
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
              <label htmlFor="profile-new-password" className="block text-sm font-medium text-slate-700 mb-1.5">
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
                <p className="text-xs text-rose-500 mt-1">Must be at least 8 characters</p>
              )}
            </div>
            <div>
              <label htmlFor="profile-confirm-password" className="block text-sm font-medium text-slate-700 mb-1.5">
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
                <p className="text-xs text-rose-500 mt-1">Passwords do not match</p>
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
          <p className="text-sm text-slate-500">
            Regularly update your password to keep your account secure.
          </p>
        )}
      </div>
    </div>
  );
}
