import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useToast } from '../components/Toast';
import authApi from '../api/authApi';

export default function ResetPasswordPage() {
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const passwordValid = newPassword.length >= 8;
  const passwordsMatch = newPassword === confirmPassword;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!token || !newPassword || !confirmPassword) {
      toast.warning('Please fill in all fields');
      return;
    }
    if (!passwordValid) {
      toast.warning('Password must be at least 8 characters');
      return;
    }
    if (!passwordsMatch) {
      toast.warning('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await authApi.resetPassword(token, newPassword);
      toast.success('Password reset successfully! Please log in.');
      navigate('/login');
    } catch (err) {
      toast.error(err.message || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-md mx-4 animate-scale-in">
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-50 border border-brand-200 mb-4">
              <svg className="w-7 h-7 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-slate-800">Reset Password</h1>
            <p className="text-slate-500 text-sm mt-1">
              Enter your reset token and new password.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5" id="reset-password-form">
            <div>
              <label htmlFor="reset-token" className="block text-sm font-medium text-slate-700 mb-1.5">
                Reset Token
              </label>
              <input
                id="reset-token"
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="input-field font-mono text-sm"
                placeholder="Paste your reset token here"
              />
            </div>

            <div>
              <label htmlFor="reset-new-password" className="block text-sm font-medium text-slate-700 mb-1.5">
                New Password
              </label>
              <input
                id="reset-new-password"
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
              <label htmlFor="reset-confirm-password" className="block text-sm font-medium text-slate-700 mb-1.5">
                Confirm Password
              </label>
              <input
                id="reset-confirm-password"
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

            <button
              type="submit"
              disabled={loading || !passwordValid || !passwordsMatch}
              className="btn-primary w-full flex items-center justify-center gap-2"
              id="reset-password-submit"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Resetting...
                </>
              ) : (
                'Reset Password'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link to="/login" className="text-sm text-brand-600 hover:text-brand-700 font-medium transition-colors">
              ← Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
