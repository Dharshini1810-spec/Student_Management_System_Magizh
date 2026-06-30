import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import dailyContentApi from '../api/dailyContentApi';

const PAGE_SIZE = 50;

function todayStr() {
  const d = new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

export default function DailyContentPage() {
  const { user, isAdmin } = useAuth();
  const toast = useToast();

  const [contents, setContents] = useState([]);
  const [total, setTotal] = useState(0);
  const [todayContent, setTodayContent] = useState(null);
  const [dateFilter, setDateFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formTitle, setFormTitle] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formDate, setFormDate] = useState(todayStr());
  const [formLoading, setFormLoading] = useState(false);

  const fetchContents = useCallback(async () => {
    setLoading(true);
    try {
      const params = { limit: PAGE_SIZE, offset: 0 };
      if (dateFilter) params.content_date = dateFilter;
      const [listRes, todayRes] = await Promise.all([
        dailyContentApi.list(params),
        dailyContentApi.getToday().catch(() => null),
      ]);
      setContents(listRes.data.daily_contents || []);
      setTotal(listRes.data.total || 0);
      if (todayRes?.data) setTodayContent(todayRes.data);
    } catch (err) {
      toast.error(err.message || 'Failed to load daily content');
    } finally {
      setLoading(false);
    }
  }, [dateFilter, toast]);

  useEffect(() => { fetchContents(); }, [fetchContents]);

  const resetForm = () => {
    setShowForm(false);
    setEditId(null);
    setFormTitle('');
    setFormContent('');
    setFormDate(todayStr());
  };

  const openEdit = (item) => {
    setEditId(item.id);
    setFormTitle(item.title);
    setFormContent(item.content || '');
    setFormDate(item.content_date || todayStr());
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formTitle) { toast.warning('Title is required'); return; }
    setFormLoading(true);
    try {
      const data = { title: formTitle, content: formContent || undefined, content_date: formDate || undefined };
      if (editId) {
        await dailyContentApi.update(editId, data);
        toast.success('Daily content updated');
      } else {
        await dailyContentApi.create(data);
        toast.success('Daily content created');
      }
      resetForm();
      await fetchContents();
    } catch (err) {
      toast.error(err.message || 'Failed to save daily content');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this daily content?')) return;
    setActionLoading(`del-${id}`);
    try {
      await dailyContentApi.delete(id);
      toast.success('Daily content deleted');
      await fetchContents();
    } catch (err) {
      toast.error(err.message || 'Failed to delete');
    } finally {
      setActionLoading(null);
    }
  };

  const canAssign = isAdmin || user?.role === 'SUPER_ADMIN' || user?.role === 'MENTOR';

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Daily Content</h1>
          <p className="text-sm text-white/50 mt-1">{total} item{total !== 1 ? 's' : ''}</p>
        </div>
        {canAssign && (
          <button onClick={() => { resetForm(); setShowForm(true); }} className="btn-primary text-sm">
            <svg className="w-4 h-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            New Content
          </button>
        )}
      </div>

      {todayContent && (
        <div className="stat-card">
          <p className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-1">Today's Content</p>
          <h3 className="text-lg font-bold text-white mb-1">{todayContent.title}</h3>
          {todayContent.content && <p className="text-sm text-white/70 whitespace-pre-wrap">{todayContent.content}</p>}
          <p className="text-xs text-white/30 mt-2">By {todayContent.created_by_name || 'Unknown'}</p>
        </div>
      )}

      {showForm && (
        <div className="card">
          <h2 className="section-title mb-4">{editId ? 'Edit Content' : 'Create New Content'}</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-white/80 mb-1.5">Title *</label>
              <input type="text" value={formTitle} onChange={(e) => setFormTitle(e.target.value)}
                className="input-field" placeholder="Content title" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-1.5">Content</label>
              <textarea value={formContent} onChange={(e) => setFormContent(e.target.value)}
                className="input-field" rows={4} placeholder="Write content here..." />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/80 mb-1.5">Date</label>
              <input type="date" value={formDate} onChange={(e) => setFormDate(e.target.value)}
                className="input-field" />
            </div>
            <div className="flex gap-2">
              <button type="submit" disabled={formLoading || !formTitle}
                className="btn-primary text-sm">{formLoading ? 'Saving...' : editId ? 'Update' : 'Create'}</button>
              <button type="button" onClick={resetForm} className="btn-secondary text-sm">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div>
        <div className="flex gap-2 mb-4">
          <input type="date" value={dateFilter} onChange={(e) => setDateFilter(e.target.value)}
            className="input-field w-auto" />
          {dateFilter && (
            <button onClick={() => setDateFilter('')} className="btn-secondary text-sm py-2">Clear</button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
            <p className="text-sm text-white/50">Loading daily content...</p>
          </div>
        </div>
      ) : contents.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-white/50 text-sm">No daily content found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {contents.map((item, i) => (
            <div key={item.id} className="card animate-slide-up" style={{ animationDelay: `${i * 30}ms` }}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-bold text-white">{item.title}</h3>
                    {!item.is_active && <span className="badge-warning">Inactive</span>}
                  </div>
                  {item.content && <p className="text-sm text-white/70 whitespace-pre-wrap">{item.content}</p>}
                  <div className="flex items-center gap-3 mt-2 text-xs text-white/40">
                    <span>{item.content_date}</span>
                    <span>By {item.created_by_name || 'Unknown'}</span>
                  </div>
                </div>
                {canAssign && (
                  <div className="flex gap-1 flex-shrink-0">
                    <button onClick={() => openEdit(item)} className="text-xs px-2 py-1 rounded-lg bg-white/5 text-white/60 hover:bg-white/10 hover:text-white transition-colors">
                      Edit
                    </button>
                    {user?.role === 'SUPER_ADMIN' && (
                      <button onClick={() => handleDelete(item.id)} disabled={actionLoading === `del-${item.id}`}
                        className="text-xs px-2 py-1 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors">
                        {actionLoading === `del-${item.id}` ? '...' : 'Delete'}
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
