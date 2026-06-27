import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useToast } from '../components/Toast';
import usersApi from '../api/usersApi';

const ROLES = [
  { value: 'ADMIN', label: 'Admin', desc: 'Can manage users, view reports', color: 'border-brand-500/30 bg-brand-500/10' },
  { value: 'MENTOR', label: 'Mentor', desc: 'Can manage students, attendance', color: 'border-emerald-500/30 bg-emerald-500/10' },
  { value: 'STUDENT', label: 'Student', desc: 'Can view own profile, tasks', color: 'border-sky-500/30 bg-sky-500/10' },
];

export default function CreateUserPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const passwordValid = password.length >= 8;
  const formValid = email && passwordValid && role;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formValid) return;

    setLoading(true);
    try {
      const data = { email, password, role, full_name: fullName || undefined };
      await usersApi.createUser(data);
      toast.success(`User '${email}' created successfully!`);
      navigate('/users');
    } catch (err) {
      toast.error(err.message || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
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

      <div className="card p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="page-title">Create New User</h1>
          <p className="text-sm text-white/50 mt-1">
            Set up a new account with a temporary password. The user will be required to change it on first login.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6" id="create-user-form">
          {/* Email */}
          <div>
            <label htmlFor="create-email" className="block text-sm font-medium text-slate-700 mb-1.5">
              Email Address <span className="text-rose-400">*</span>
            </label>
            <input
              id="create-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              placeholder="user@example.com"
              required
            />
          </div>

          {/* Full Name */}
          <div>
            <label htmlFor="create-fullname" className="block text-sm font-medium text-white/80 mb-1.5">
              Full Name <span className="text-white/40 text-xs">(optional)</span>
            </label>
            <input
              id="create-fullname"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input-field"
              placeholder="John Doe"
            />
          </div>

          {/* Temporary Password */}
          <div>
            <label htmlFor="create-password" className="block text-sm font-medium text-slate-700 mb-1.5">
              Temporary Password <span className="text-rose-400">*</span>
            </label>
            <input
              id="create-password"
              type="text"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field font-mono"
              placeholder="Minimum 8 characters"
              required
            />
            {password && !passwordValid && (
              <p className="text-xs text-rose-400 mt-1">Must be at least 8 characters</p>
            )}
            {password && passwordValid && (
              <p className="text-xs text-emerald-400 mt-1">✓ Password meets requirements</p>
            )}
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-white/80 mb-3">
              Role <span className="text-rose-400">*</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {ROLES.map((r) => (
                <button
                  key={r.value}
                  type="button"
                  onClick={() => setRole(r.value)}
                  className={`
                    p-4 rounded-xl border-2 text-left transition-all duration-200
                    ${role === r.value
                      ? `${r.color} border-purple-500 shadow-lg shadow-purple-500/10`
                      : 'border-white/10 bg-white/5 hover:border-white/20'
                    }
                  `}
                >
                  <p className={`text-sm font-bold ${role === r.value ? 'text-white' : 'text-white/70'}`}>
                    {r.label}
                  </p>
                  <p className="text-xs text-white/40 mt-0.5">{r.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="flex items-center gap-3 pt-4 border-t border-white/5">
            <button
              type="submit"
              disabled={loading || !formValid}
              className="btn-primary flex items-center gap-2"
              id="create-user-submit"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  Create User
                </>
              )}
            </button>
            <Link to="/users" className="btn-secondary">
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
