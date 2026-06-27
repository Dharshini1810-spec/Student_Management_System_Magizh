import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import activityLogsApi from '../api/activityLogsApi';
import usersApi from '../api/usersApi';

const ACTION_COLORS = {
  LOGIN: 'badge-info',
  LOGOUT: 'badge-warning',
  TODO_CREATED: 'badge-brand',
  TODO_STATUS_UPDATED: 'badge-info',
  PROJECT_CREATED: 'badge-brand',
  PROJECT_STATUS_UPDATED: 'badge-info',
  ATTENDANCE_MARKED: 'badge-success',
  ATTENDANCE_REQUESTED: 'badge-warning',
  ATTENDANCE_APPROVED: 'badge-success',
  ATTENDANCE_REJECTED: 'badge-danger',
  USER_CREATED: 'badge-brand',
  USER_UPDATED: 'badge-info',
  NOTE_CREATED: 'badge-brand',
  NOTE_DELETED: 'badge-danger',
  NOTIFICATION_SENT: 'badge-info',
  PASSWORD_CHANGED: 'badge-warning',
};

function getBadgeClass(action) {
  return ACTION_COLORS[action] || 'badge-brand';
}

function groupByDate(logs) {
  const groups = {};
  logs.forEach((log) => {
    const d = new Date(log.created_at).toLocaleDateString('en-US', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    });
    if (!groups[d]) groups[d] = [];
    groups[d].push(log);
  });
  return groups;
}

export default function ActivityPage() {
  const { user, isSuperAdmin } = useAuth();
  const toast = useToast();

  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [userFilter, setUserFilter] = useState('');
  const [users, setUsers] = useState([]);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      if (isSuperAdmin) {
        const params = { limit: 100 };
        if (userFilter) params.user_id = userFilter;
        const res = await activityLogsApi.list(params);
        setLogs(res.data.logs || []);
        setTotal(res.data.total || 0);
      } else {
        const res = await activityLogsApi.getMine();
        setLogs(res.data.logs || []);
        setTotal(res.data.logs?.length || 0);
      }
    } catch (err) {
      toast.error(err.message || 'Failed to load activity logs');
    } finally {
      setLoading(false);
    }
  }, [isSuperAdmin, userFilter, toast]);

  useEffect(() => {
    if (isSuperAdmin) {
      usersApi.listUsers({ page_size: 100 })
        .then((res) => setUsers(res.data || []))
        .catch(() => {});
    }
  }, [isSuperAdmin]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const grouped = groupByDate(logs);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Activity Log</h1>
        <p className="text-sm text-white/50 mt-1">{total} log entr{total === 1 ? 'y' : 'ies'}</p>
      </div>

      {isSuperAdmin && (
        <div className="flex gap-2 items-center">
          <label className="text-xs text-white/60">Filter by user:</label>
          <select
            value={userFilter}
            onChange={(e) => setUserFilter(e.target.value)}
            className="input-field w-auto"
          >
            <option value="">All Users</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.email}</option>
            ))}
          </select>
          <button onClick={fetchLogs} className="btn-primary text-sm py-2" disabled={loading}>Refresh</button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
            <p className="text-sm text-white/50">Loading activity logs...</p>
          </div>
        </div>
      ) : logs.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-white/50 text-sm">No activity logs found</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([date, dateLogs]) => (
            <div key={date}>
              <h3 className="text-sm font-bold text-white/60 mb-3 sticky top-0 bg-slate-900/90 backdrop-blur-sm py-2 z-10">
                {date}
              </h3>
              <div className="space-y-2">
                {dateLogs.map((log, i) => (
                  <div key={log.id} className="card animate-slide-up" style={{ animationDelay: `${i * 20}ms` }}>
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
                        <svg className="w-4 h-4 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={getBadgeClass(log.action)}>{log.action}</span>
                          <span className="text-xs text-white/30">
                            {new Date(log.created_at).toLocaleTimeString('en-US', {
                              hour: '2-digit', minute: '2-digit',
                            })}
                          </span>
                          {isSuperAdmin && log.user_id && (
                            <span className="text-xs text-white/30">by {log.user_id?.substring(0, 8)}...</span>
                          )}
                        </div>
                        <p className="text-sm text-white/70 mt-1">{log.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
