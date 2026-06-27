import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import projectsApi from '../api/projectsApi';
import usersApi from '../api/usersApi';

const STATUS_OPTIONS = ['not_started', 'in_progress', 'completed'];
const STATUS_COLORS = {
  not_started: { bg: 'bg-slate-500/20', text: 'text-slate-300', border: 'border-slate-500/30' },
  in_progress: { bg: 'bg-sky-500/20', text: 'text-sky-300', border: 'border-sky-500/30' },
  completed: { bg: 'bg-emerald-500/20', text: 'text-emerald-300', border: 'border-emerald-500/30' },
};

export default function ProjectsPage() {
  const { user, isAdmin } = useAuth();
  const toast = useToast();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [students, setStudents] = useState([]);
  const [studentFilter, setStudentFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);
  const [form, setForm] = useState({ name: '', description: '', tech_stack: '', assigned_to: '', deadline: '' });

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const res = await projectsApi.list();
      setProjects(res.data?.projects || []);
    } catch (err) {
      toast.error(err.message || 'Failed to load projects');
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
    fetchProjects();
    if (isAdmin) fetchAssignableUsers();
  }, [fetchProjects, fetchAssignableUsers, isAdmin]);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', description: '', tech_stack: '', assigned_to: '', deadline: '' });
    setShowModal(true);
  };

  const openEdit = (project) => {
    setEditing(project);
    setForm({
      name: project.name,
      description: project.description || '',
      tech_stack: project.tech_stack || '',
      assigned_to: project.assigned_to || '',
      deadline: project.deadline ? project.deadline.slice(0, 16) : '',
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error('Project name is required'); return; }
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        description: form.description || null,
        tech_stack: form.tech_stack || null,
        assigned_to: editing ? (form.assigned_to || null) : (form.assigned_to || null),
        deadline: form.deadline ? new Date(form.deadline).toISOString() : null,
      };
      if (editing) {
        await projectsApi.update(editing.id, payload);
        toast.success('Project updated');
      } else {
        await projectsApi.create(payload);
        toast.success('Project created');
      }
      setShowModal(false);
      await fetchProjects();
    } catch (err) {
      toast.error(err.message || 'Failed to save project');
    } finally {
      setSaving(false);
    }
  };

  const handleStatusUpdate = async (project, newStatus) => {
    setActionLoading(`status-${project.id}`);
    try {
      await projectsApi.updateStatus(project.id, newStatus);
      toast.success(`Status updated to ${newStatus.replace(/_/g, ' ')}`);
      await fetchProjects();
    } catch (err) {
      toast.error(err.message || 'Failed to update status');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (id) => {
    setActionLoading(`delete-${id}`);
    try {
      await projectsApi.delete(id);
      toast.success('Project deleted');
      await fetchProjects();
    } catch (err) {
      toast.error(err.message || 'Failed to delete project');
    } finally {
      setActionLoading(null);
    }
  };

  const filtered = projects.filter((p) => {
    if (statusFilter !== 'all' && p.status !== statusFilter) return false;
    if (isAdmin && studentFilter && p.assigned_to !== studentFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Projects</h1>
          <p className="text-sm text-white/50 mt-1">{filtered.length} project{filtered.length !== 1 ? 's' : ''}</p>
        </div>
        {isAdmin && (
          <button onClick={openCreate} className="btn-primary text-sm inline-flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Create Project
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
            <p className="text-sm text-white/50">Loading projects...</p>
          </div>
        </div>
      ) : filtered.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-white/50 text-sm">No projects found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((project, i) => {
            const sc = STATUS_COLORS[project.status] || STATUS_COLORS.not_started;
            return (
              <div key={project.id} className="card flex flex-col animate-slide-up" style={{ animationDelay: `${i * 30}ms` }}>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <h3 className="text-sm font-bold text-white/90">{project.name}</h3>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${sc.bg} ${sc.text} ${sc.border} flex-shrink-0`}>
                    {project.status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  </span>
                </div>
                {project.description && (
                  <p className="text-sm text-white/50 mb-3 line-clamp-2">{project.description}</p>
                )}
                <div className="mt-auto space-y-2">
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-white/40">
                    {project.deadline && (
                      <span>Due: {new Date(project.deadline).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                    )}
                    {project.tech_stack && <span>Stack: {project.tech_stack}</span>}
                    {project.assignee_name && <span>Assigned to: {project.assignee_name}</span>}
                    {project.assigner_name && <span>By: {project.assigner_name}</span>}
                  </div>
                  <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                    {project.status === 'not_started' && (
                      <button onClick={() => handleStatusUpdate(project, 'in_progress')}
                        disabled={actionLoading === `status-${project.id}`}
                        className="text-xs font-medium text-sky-400 hover:text-sky-300 transition-colors"
                      >
                        {actionLoading === `status-${project.id}` ? '...' : 'Start'}
                      </button>
                    )}
                    {project.status !== 'completed' && (
                      <button onClick={() => handleStatusUpdate(project, 'completed')}
                        disabled={actionLoading === `status-${project.id}`}
                        className="text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
                      >
                        {actionLoading === `status-${project.id}` ? '...' : 'Complete'}
                      </button>
                    )}
                    {isAdmin && (
                      <>
                        <button onClick={() => openEdit(project)}
                          className="text-xs font-medium text-purple-400 hover:text-purple-300 transition-colors"
                        >
                          Edit
                        </button>
                        <button onClick={() => handleDelete(project.id)}
                          disabled={actionLoading === `delete-${project.id}`}
                          className="text-xs font-medium text-rose-400 hover:text-rose-300 transition-colors"
                        >
                          {actionLoading === `delete-${project.id}` ? '...' : 'Delete'}
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
            <h2 className="text-lg font-bold text-white/90 mb-4">{editing ? 'Edit Project' : 'Create Project'}</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Name *</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input-field w-full" placeholder="Project name" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field w-full h-24 resize-none" placeholder="Optional description" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Tech Stack</label>
                <input value={form.tech_stack} onChange={(e) => setForm({ ...form, tech_stack: e.target.value })} className="input-field w-full" placeholder="e.g. React, Python, PostgreSQL" />
              </div>
              {isAdmin && (
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-1">Assign to *</label>
                  <select value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} className="input-field w-full">
                    <option value="">Select a user</option>
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
