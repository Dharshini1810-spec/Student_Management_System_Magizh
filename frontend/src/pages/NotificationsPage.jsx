import React, { useState, useEffect, useCallback } from 'react';
import { useToast } from '../components/Toast';
import notificationsApi from '../api/notificationsApi';

const PAGE_SIZE = 20;

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const toast = useToast();

  const fetchNotifications = useCallback(async (isRead = null, offset = 0) => {
    setLoading(true);
    try {
      const params = { limit: PAGE_SIZE, offset };
      if (isRead === true) params.is_read = true;
      else if (isRead === false) params.is_read = false;
      const res = await notificationsApi.list(params);
      setNotifications(res.data.notifications || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      toast.error(err.message || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    const isRead = filter === 'read' ? true : filter === 'unread' ? false : null;
    fetchNotifications(isRead);
  }, [filter, fetchNotifications]);

  const handleMarkRead = async (id) => {
    setActionLoading(`read-${id}`);
    try {
      await notificationsApi.markRead(id);
      toast.success('Notification marked as read');
      await fetchNotifications(
        filter === 'read' ? true : filter === 'unread' ? false : null
      );
    } catch (err) {
      toast.error(err.message || 'Failed to mark as read');
    } finally {
      setActionLoading(null);
    }
  };

  const handleMarkAllRead = async () => {
    setActionLoading('all');
    try {
      const res = await notificationsApi.markAllRead();
      toast.success(`${res.data.marked_read} notifications marked as read`);
      await fetchNotifications(
        filter === 'read' ? true : filter === 'unread' ? false : null
      );
    } catch (err) {
      toast.error(err.message || 'Failed to mark all as read');
    } finally {
      setActionLoading(null);
    }
  };

  const unread = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="text-sm text-white/50 mt-1">
            {total} notification{total !== 1 ? 's' : ''}
            {unread > 0 && ` · ${unread} unread`}
          </p>
        </div>
        <div className="flex gap-2">
          {unread > 0 && (
            <button
              onClick={handleMarkAllRead}
              disabled={actionLoading === 'all'}
              className="btn-primary text-sm py-2"
            >
              {actionLoading === 'all' ? 'Marking...' : 'Mark All Read'}
            </button>
          )}
        </div>
      </div>

      <div className="flex gap-1 bg-white/5 rounded-xl p-1 w-fit">
        {['all', 'unread', 'read'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
              filter === f
                ? 'bg-white/10 text-white shadow-sm'
                : 'text-white/50 hover:text-white/80'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
            <p className="text-sm text-white/50">Loading notifications...</p>
          </div>
        </div>
      ) : notifications.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="flex justify-center mb-3">
            <svg className="w-12 h-12 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <p className="text-white/50 text-sm">No notifications found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n, i) => (
            <div
              key={n.id}
              className={`card flex items-start gap-4 animate-slide-up ${
                !n.is_read ? 'border-l-2 border-l-purple-500' : ''
              }`}
              style={{ animationDelay: `${i * 30}ms` }}
            >
              <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${
                !n.is_read ? 'bg-purple-500/20 text-purple-300' : 'bg-white/5 text-white/40'
              }`}>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className={`text-sm font-semibold ${!n.is_read ? 'text-white' : 'text-white/60'}`}>
                      {n.title}
                    </p>
                    <p className="text-sm text-white/50 mt-0.5">{n.message}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-xs text-white/30 whitespace-nowrap">
                      {new Date(n.created_at).toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                      })}
                    </span>
                    {!n.is_read && (
                      <button
                        onClick={() => handleMarkRead(n.id)}
                        disabled={actionLoading === `read-${n.id}`}
                        className="text-xs font-medium text-purple-400 hover:text-purple-300 transition-colors"
                      >
                        {actionLoading === `read-${n.id}` ? '...' : 'Mark read'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
