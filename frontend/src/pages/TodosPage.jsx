import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import todosApi from '../api/todosApi';
import usersApi from '../api/usersApi';

const STATUS_OPTIONS = ['pending', 'in_progress', 'completed'];
const STATUS_COLORS = {
  pending: { bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-500/30' },
  in_progress: { bg: 'bg-sky-500/20', text: 'text-sky-300', border: 'border-sky-500/30' },
  completed: { bg: 'bg-emerald-500/20', text: 'text-emerald-300', border: 'border-emerald-500/30' },
};

export default function TodosPage() {
  const { user, isAdmin } = useAuth();
  const toast = useToast();
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [students, setStudents] = useState([]);
  const [studentFilter, setStudentFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);
  const [form, setForm] = useState({ title: '', description: '', assigned_to: '', deadline: '' });

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    try {
      const res = await todosApi.list();
      setTodos(res.data?.todos || []);
    } catch (err) {
      toast.error(err.message || 'Failed to load todos');
    } finally {
      setLoading(false);
    }
  }, [toast]);

  const fetchAssignableUsers = useCallback(async () => {
    try {
      const [studRes, mentorRes] = await Promise.all([
        usersApi.listUsers({ page_size: 100, role: 'STUDENT' }),
        usersApi.listUsers({ page_size: 100, role: 'MENTOR' }),
      ]);
      setStudents([...(studRes.data || []), ...(mentorRes.data || [])]);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    fetchTodos();
    if (isAdmin) fetchAssignableUsers();
  }, [fetchTodos, fetchAssignableUsers, isAdmin]);

  const openCreate = () => {
    setEditing(null);
    setForm({ title: '', description: '', assigned_to: '', deadline: '' });
    setShowModal(true);
  };

  const openEdit = (todo) => {
    setEditing(todo);
    setForm({
      title: todo.title,
      description: todo.description || '',
      assigned_to: todo.assigned_to || '',
      deadline: todo.deadline ? todo.deadline.slice(0, 16) : '',
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) { toast.error('Title is required'); return; }
    setSaving(true);
    try {
      const payload = {
        title: form.title,
        description: form.description || null,
        assigned_to: form.assigned_to || null,
        deadline: form.deadline ? new Date(form.deadline).toISOString() : null,
      };
      if (editing) {
        await todosApi.update(editing.id, payload);
        toast.success('Todo updated');
      } else {
        await todosApi.create(payload);
        toast.success('Todo created');
      }
      setShowModal(false);
      await fetchTodos();
    } catch (err) {
      toast.error(err.message || 'Failed to save todo');
    } finally {
      setSaving(false);
    }
  };

  const handleStatusUpdate = async (todo, newStatus) => {
    setActionLoading(`status-${todo.id}`);
    try {
      await todosApi.updateStatus(todo.id, newStatus);
      toast.success(`Status updated to ${newStatus}`);
      await fetchTodos();
    } catch (err) {
      toast.error(err.message || 'Failed to update status');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (id) => {
    setActionLoading(`delete-${id}`);
    try {
      await todosApi.delete(id);
      toast.success('Todo deleted');
      await fetchTodos();
    } catch (err) {
      toast.error(err.message || 'Failed to delete todo');
    } finally {
      setActionLoading(null);
    }
  };

  const filtered = todos.filter((t) => {
    if (statusFilter !== 'all' && t.status !== statusFilter) return false;
    if (isAdmin && studentFilter && t.assigned_to !== studentFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Todos</h1>
          <p className="text-sm text-white/50 mt-1">{filtered.length} todo{filtered.length !== 1 ? 's' : ''}</p>
        </div>
        {isAdmin && (
          <button onClick={openCreate} className="btn-primary text-sm inline-flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Create Todo
          </button>
        )}
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-1 bg-white/5 rounded-xl p-1">
          {['all', ...STATUS_OPTIONS].map((s) => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                statusFilter === s ? 'bg-white/10 text-white shadow-sm' : 'text-white/50 hover:text-white/80'
              }`}
            >
              {s === 'all' ? 'All' : s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
            </button>
          ))}
        </div>
        {isAdmin && students.length > 0 && (
          <select value={studentFilter} onChange={(e) => setStudentFilter(e.target.value)}
            className="input-field text-sm py-1.5 px-3 max-w-xs"
          >
            <option value="">All Users</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>{(s.role === 'MENTOR' ? '[Mentor] ' : '[Student] ') + (s.email || s.name || s.id)}</option>
            ))}
          </select>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
            <p className="text-sm text-white/50">Loading todos...</p>
          </div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-white/50 text-sm">No todos found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((todo, i) => {
            const sc = STATUS_COLORS[todo.status] || STATUS_COLORS.pending;
            return (
              <div key={todo.id} className="card flex flex-col animate-slide-up" style={{ animationDelay: `${i * 30}ms` }}>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <h3 className="text-sm font-bold text-white/90">{todo.title}</h3>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${sc.bg} ${sc.text} ${sc.border} flex-shrink-0`}>
                    {todo.status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  </span>
                </div>
                {todo.description && (
                  <p className="text-sm text-white/50 mb-3 line-clamp-2">{todo.description}</p>
                )}
                <div className="mt-auto space-y-2">
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-white/40">
                    {todo.deadline && (
                      <span>Due: {new Date(todo.deadline).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                    )}
                    {todo.assignee_name && <span>Assigned to: {todo.assignee_name}</span>}
                    {todo.created_by_name && <span>By: {todo.created_by_name}</span>}
                  </div>
                  <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                    {todo.status !== 'completed' && (
                      <button onClick={() => handleStatusUpdate(todo, 'completed')}
                        disabled={actionLoading === `status-${todo.id}`}
                        className="text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
                      >
                        {actionLoading === `status-${todo.id}` ? '...' : 'Mark complete'}
                      </button>
                    )}
                    {todo.status === 'pending' && (
                      <button onClick={() => handleStatusUpdate(todo, 'in_progress')}
                        disabled={actionLoading === `status-${todo.id}`}
                        className="text-xs font-medium text-sky-400 hover:text-sky-300 transition-colors"
                      >
                        Start
                      </button>
                    )}
                    {isAdmin && (
                      <>
                        <button onClick={() => openEdit(todo)}
                          className="text-xs font-medium text-purple-400 hover:text-purple-300 transition-colors"
                        >
                          Edit
                        </button>
                        <button onClick={() => handleDelete(todo.id)}
                          disabled={actionLoading === `delete-${todo.id}`}
                          className="text-xs font-medium text-rose-400 hover:text-rose-300 transition-colors"
                        >
                          {actionLoading === `delete-${todo.id}` ? '...' : 'Delete'}
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowModal(false)}>
          <div className="card w-full max-w-lg mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold text-white/90 mb-4">{editing ? 'Edit Todo' : 'Create Todo'}</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Title *</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="input-field w-full" placeholder="Todo title" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field w-full h-24 resize-none" placeholder="Optional description" />
              </div>
              {isAdmin && (
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-1">Assign to</label>
                  <select value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} className="input-field w-full">
                    <option value="">Unassigned</option>
                    {students.map((s) => (
                      <option key={s.id} value={s.id}>
                        {(s.role === 'MENTOR' ? '[Mentor] ' : '[Student] ') + (s.email || s.name || s.id)}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Due Date</label>
                <input type="datetime-local" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} className="input-field w-full" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 rounded-xl text-sm font-medium text-white/60 hover:text-white/80 hover:bg-white/5 transition-all">Cancel</button>
              <button onClick={handleSave} disabled={saving} className="btn-primary text-sm">
                {saving ? 'Saving...' : editing ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
