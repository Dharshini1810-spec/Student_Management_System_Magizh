import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../components/Toast';
import authApi from '../api/authApi';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetToken, setResetToken] = useState(null);
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      toast.warning('Please enter your email');
      return;
    }

    setLoading(true);
    try {
      const res = await authApi.forgotPassword(email);
      setResetToken(res.data?.reset_token);
      toast.success('Reset token generated!');
    } catch (err) {
      toast.error(err.message || 'Failed to generate reset token');
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
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-slate-800">Forgot Password</h1>
            <p className="text-slate-500 text-sm mt-1">
              Enter your email to receive a reset token.
            </p>
          </div>

          {!resetToken ? (
            <form onSubmit={handleSubmit} className="space-y-5" id="forgot-password-form">
              <div>
                <label htmlFor="forgot-email" className="block text-sm font-medium text-slate-700 mb-1.5">
                  Email Address
                </label>
                <input
                  id="forgot-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field"
                  placeholder="admin@example.com"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center gap-2"
                id="forgot-password-submit"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Sending...
                  </>
                ) : (
                  'Send Reset Token'
                )}
              </button>
            </form>
          ) : (
            <div className="space-y-4 animate-fade-in">
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                <p className="text-sm font-medium text-emerald-800 mb-2">Reset Token Generated</p>
                <code className="block bg-white rounded-lg p-3 text-xs text-slate-800 break-all border border-emerald-100 font-mono">
                  {resetToken}
                </code>
              </div>
              <Link
                to="/reset-password"
                className="btn-primary w-full flex items-center justify-center"
              >
                Go to Reset Password →
              </Link>
            </div>
          )}

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
