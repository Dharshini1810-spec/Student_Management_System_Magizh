import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import referralLinksApi from '../api/referralLinksApi';

export default function ReferralLinksPage() {
  const { user, isAdmin } = useAuth();
  const toast = useToast();
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ description: '', max_uses: '' });
  const [copiedId, setCopiedId] = useState(null);

  const fetchLinks = useCallback(async () => {
    setLoading(true);
    try {
      const res = await referralLinksApi.list();
      setLinks(res.data?.links || []);
    } catch (err) {
      toast.error(err.message || 'Failed to load referral links');
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => { fetchLinks(); }, [fetchLinks]);

  const handleCreate = async () => {
    setSaving(true);
    try {
      const payload = {
        description: form.description || null,
        max_uses: form.max_uses ? parseInt(form.max_uses) : null,
      };
      await referralLinksApi.create(payload);
      toast.success('Referral link created');
      setShowModal(false);
      setForm({ description: '', max_uses: '' });
      await fetchLinks();
    } catch (err) {
      toast.error(err.message || 'Failed to create referral link');
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (id) => {
    try {
      await referralLinksApi.deactivate(id);
      toast.success('Referral link deactivated');
      await fetchLinks();
    } catch (err) {
      toast.error(err.message || 'Failed to deactivate referral link');
    }
  };

  const handleCopy = async (code) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedId(code);
      setTimeout(() => setCopiedId(null), 2000);
      toast.success('Code copied');
    } catch {
      toast.error('Failed to copy');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Referral Links</h1>
          <p className="text-sm text-white/50 mt-1">{links.length} link{links.length !== 1 ? 's' : ''}</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary text-sm inline-flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Create Link
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
            <p className="text-sm text-white/50">Loading referral links...</p>
          </div>
        </div>
      ) : links.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-white/50 text-sm">No referral links yet. Create one to share with students.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {links.map((link, i) => (
            <div key={link.id} className="card p-4 flex flex-col sm:flex-row sm:items-center gap-3 animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${link.is_active ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
                    {link.is_active ? 'Active' : 'Inactive'}
                  </span>
                  {link.max_uses && (
                    <span className="text-xs text-white/40">{link.current_uses}/{link.max_uses} uses</span>
                  )}
                </div>
                <code className="text-sm font-mono text-purple-300 bg-white/5 px-2 py-0.5 rounded">{link.code}</code>
                {link.description && <p className="text-sm text-white/50 mt-1">{link.description}</p>}
                {link.expires_at && (
                  <p className="text-xs text-white/30 mt-0.5">Expires: {new Date(link.expires_at).toLocaleDateString()}</p>
                )}
                <p className="text-xs text-white/20 mt-0.5">Created {new Date(link.created_at).toLocaleDateString()}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <button onClick={() => handleCopy(link.code)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-white/5 text-white/60 hover:bg-white/10 hover:text-white/80 transition-all">
                  {copiedId === link.code ? 'Copied!' : 'Copy Link'}
                </button>
                {link.is_active && (
                  <button onClick={() => handleDeactivate(link.id)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-all">
                    Deactivate
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowModal(false)}>
          <div className="card w-full max-w-md mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold text-white/90 mb-4">Create Referral Link</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Description (optional)</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field w-full" placeholder="e.g. Batch 2026 students" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Max Uses (optional)</label>
                <input type="number" value={form.max_uses} onChange={(e) => setForm({ ...form, max_uses: e.target.value })} className="input-field w-full" placeholder="Leave empty for unlimited" min="1" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl text-sm font-medium text-white/60 hover:text-white/80 hover:bg-white/5 transition-all">Cancel</button>
              <button onClick={handleCreate} disabled={saving} className="btn-primary text-sm">
                {saving ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
