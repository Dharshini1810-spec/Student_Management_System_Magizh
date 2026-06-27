import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import attendanceApi from '../api/attendanceApi';

const STATUS_COLORS = {
  PRESENT: { bg: 'bg-emerald-500/20', text: 'text-emerald-300', border: 'border-emerald-500/30', label: 'Present' },
  ABSENT: { bg: 'bg-rose-500/20', text: 'text-rose-300', border: 'border-rose-500/30', label: 'Absent' },
  LATE: { bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-500/30', label: 'Late' },
  HALF_DAY: { bg: 'bg-sky-500/20', text: 'text-sky-300', border: 'border-sky-500/30', label: 'Half Day' },
};

const REQUEST_TYPE_COLORS = {
  CHECK_IN: { bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-500/30', label: 'Late Check-In' },
  CHECK_OUT: { bg: 'bg-purple-500/20', text: 'text-purple-300', border: 'border-purple-500/30', label: 'Early Departure' },
};

const REQUEST_STATUS_COLORS = {
  PENDING: { bg: 'bg-amber-500/20', text: 'text-amber-300' },
  APPROVED: { bg: 'bg-emerald-500/20', text: 'text-emerald-300' },
  REJECTED: { bg: 'bg-rose-500/20', text: 'text-rose-300' },
};

export default function AttendancePage() {
  const { user, isAdmin, isSuperAdmin } = useAuth();
  const toast = useToast();
  const [logs, setLogs] = useState([]);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestType, setRequestType] = useState('late');
  const [requestReason, setRequestReason] = useState('');
  const [checkingIn, setCheckingIn] = useState(false);
  const [checkingOut, setCheckingOut] = useState(false);

  const isStudent = user?.role === 'STUDENT';

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const logsRes = await attendanceApi.list();
      setLogs(logsRes.data?.logs || []);
      if (!isStudent) {
        const reqRes = await attendanceApi.listRequests();
        setRequests(reqRes.data?.requests || []);
      }
    } catch (err) {
      toast.error(err.message || 'Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  }, [toast, isStudent]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const todayLog = logs.find((l) => {
    const today = new Date().toISOString().slice(0, 10);
    return l.date === today;
  });

  const handleCheckIn = async () => {
    setCheckingIn(true);
    try {
      const res = await attendanceApi.checkIn(null);
      if (res.data?.status === 'LATE_REQUEST_PENDING') {
        toast.info('Check-in deadline passed. A late request has been submitted.');
      } else {
        toast.success('Checked in successfully');
      }
      await fetchData();
    } catch (err) {
      toast.error(err.message || 'Failed to check in');
    } finally {
      setCheckingIn(false);
    }
  };

  const handleCheckOut = async () => {
    setCheckingOut(true);
    try {
      const res = await attendanceApi.checkOut(null);
      if (res.data?.status === 'LATE_REQUEST_PENDING') {
        toast.info('Early departure request submitted.');
      } else {
        toast.success('Checked out successfully');
      }
      await fetchData();
    } catch (err) {
      toast.error(err.message || 'Failed to check out');
    } finally {
      setCheckingOut(false);
    }
  };

  const handleSubmitRequest = async () => {
    if (!requestReason.trim()) { toast.error('Please provide a reason'); return; }
    setActionLoading('submit-request');
    try {
      if (requestType === 'late') {
        await attendanceApi.checkIn(requestReason);
      } else {
        await attendanceApi.checkOut(requestReason);
      }
      toast.success('Request submitted');
      setShowRequestModal(false);
      setRequestReason('');
      await fetchData();
    } catch (err) {
      toast.error(err.message || 'Failed to submit request');
    } finally {
      setActionLoading(null);
    }
  };

  const handleApprove = async (id) => {
    setActionLoading(`approve-${id}`);
    try {
      await attendanceApi.approveRequest(id);
      toast.success('Request approved');
      await fetchData();
    } catch (err) {
      toast.error(err.message || 'Failed to approve request');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id) => {
    setActionLoading(`reject-${id}`);
    try {
      await attendanceApi.rejectRequest(id);
      toast.success('Request rejected');
      await fetchData();
    } catch (err) {
      toast.error(err.message || 'Failed to reject request');
    } finally {
      setActionLoading(null);
    }
  };

  const pendingRequests = requests.filter((r) => r.status === 'PENDING');

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Attendance</h1>
          <p className="text-sm text-white/50 mt-1">{logs.length} record{logs.length !== 1 ? 's' : ''}</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
            <p className="text-sm text-white/50">Loading attendance...</p>
          </div>
        </div>
      ) : (
        <>
          {isStudent && (
            <div className="card">
              <h2 className="text-lg font-bold text-white/90 mb-4">Today</h2>
              <div className="flex flex-col sm:flex-row gap-4">
                {todayLog ? (
                  <div className="flex items-center gap-3 flex-1">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${
                      (STATUS_COLORS[todayLog.status] || STATUS_COLORS.ABSENT).bg
                    } ${(STATUS_COLORS[todayLog.status] || STATUS_COLORS.ABSENT).text} ${
                      (STATUS_COLORS[todayLog.status] || STATUS_COLORS.ABSENT).border
                    }`}>
                      {(STATUS_COLORS[todayLog.status] || STATUS_COLORS.ABSENT).label}
                    </span>
                    {todayLog.check_in_time && (
                      <span className="text-sm text-white/60">In: {new Date(todayLog.check_in_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                    )}
                    {todayLog.check_out_time && (
                      <span className="text-sm text-white/60">Out: {new Date(todayLog.check_out_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-white/50 flex-1">No record for today</p>
                )}
                <div className="flex gap-2">
                  <button onClick={handleCheckIn} disabled={checkingIn || (!!todayLog && !!todayLog.check_in_time)}
                    className="px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/30 transition-all disabled:opacity-40"
                  >
                    {checkingIn ? '...' : todayLog?.check_in_time ? 'Checked In' : 'Check In'}
                  </button>
                  <button onClick={handleCheckOut} disabled={checkingOut || !todayLog?.check_in_time || !!todayLog?.check_out_time}
                    className="px-4 py-2 rounded-xl text-sm font-semibold bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 border border-amber-500/30 transition-all disabled:opacity-40"
                  >
                    {checkingOut ? '...' : todayLog?.check_out_time ? 'Checked Out' : 'Check Out'}
                  </button>
                  <button onClick={() => setShowRequestModal(true)}
                    className="px-4 py-2 rounded-xl text-sm font-semibold bg-white/5 text-white/60 hover:bg-white/10 border border-white/10 transition-all"
                  >
                    Request
                  </button>
                </div>
              </div>
            </div>
          )}

          {(isAdmin || isSuperAdmin) && pendingRequests.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-bold text-white/90 mb-4">
                Pending Requests
                <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {pendingRequests.length}
                </span>
              </h2>
              <div className="space-y-3">
                {pendingRequests.map((req) => (
                  <div key={req.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
                    <div>
                      <p className="text-sm font-semibold text-white/90">{req.student_name || 'Unknown'}</p>
                      <div className="flex gap-3 mt-1 text-xs text-white/50">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                          (REQUEST_TYPE_COLORS[req.request_type] || REQUEST_TYPE_COLORS.CHECK_IN).bg
                        } ${(REQUEST_TYPE_COLORS[req.request_type] || REQUEST_TYPE_COLORS.CHECK_IN).text} ${
                          (REQUEST_TYPE_COLORS[req.request_type] || REQUEST_TYPE_COLORS.CHECK_IN).border
                        }`}>
                          {(REQUEST_TYPE_COLORS[req.request_type] || REQUEST_TYPE_COLORS.CHECK_IN).label}
                        </span>
                        <span>{new Date(req.created_at).toLocaleString()}</span>
                      </div>
                      {req.reason && <p className="text-xs text-white/40 mt-1">Reason: {req.reason}</p>}
                    </div>
                    <div className="flex gap-2 flex-shrink-0">
                      <button onClick={() => handleApprove(req.id)}
                        disabled={actionLoading === `approve-${req.id}`}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/30 transition-all"
                      >
                        {actionLoading === `approve-${req.id}` ? '...' : 'Approve'}
                      </button>
                      <button onClick={() => handleReject(req.id)}
                        disabled={actionLoading === `reject-${req.id}`}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 border border-rose-500/30 transition-all"
                      >
                        {actionLoading === `reject-${req.id}` ? '...' : 'Reject'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="table-container">
            {logs.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-white/50 text-sm">No attendance records found</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/5">
                      {!isStudent && <th className="table-header text-left py-3.5 px-5">Student</th>}
                      <th className="table-header text-left py-3.5 px-5">Date</th>
                      <th className="table-header text-left py-3.5 px-5">Status</th>
                      <th className="table-header text-left py-3.5 px-5">Check In</th>
                      <th className="table-header text-left py-3.5 px-5">Check Out</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {logs.map((log, i) => (
                      <tr key={log.id} className="table-row animate-slide-up" style={{ animationDelay: `${i * 30}ms` }}>
                        {!isStudent && (
                          <td className="py-3.5 px-5">
                            <span className="text-sm font-semibold text-white/90">{log.student_name || 'Unknown'}</span>
                          </td>
                        )}
                        <td className="py-3.5 px-5">
                          <span className="text-sm text-white/70">
                            {new Date(log.date + 'T00:00:00').toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
                          </span>
                        </td>
                        <td className="py-3.5 px-5">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                            (STATUS_COLORS[log.status] || STATUS_COLORS.ABSENT).bg
                          } ${(STATUS_COLORS[log.status] || STATUS_COLORS.ABSENT).text} ${
                            (STATUS_COLORS[log.status] || STATUS_COLORS.ABSENT).border
                          }`}>
                            {(STATUS_COLORS[log.status] || STATUS_COLORS.ABSENT).label}
                          </span>
                          {log.is_late_check_in && <span className="ml-2 text-[10px] text-amber-400 font-semibold">Late In</span>}
                          {log.is_late_check_out && <span className="ml-2 text-[10px] text-amber-400 font-semibold">Late Out</span>}
                        </td>
                        <td className="py-3.5 px-5">
                          <span className="text-sm text-white/50">
                            {log.check_in_time ? new Date(log.check_in_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : '-'}
                          </span>
                        </td>
                        <td className="py-3.5 px-5">
                          <span className="text-sm text-white/50">
                            {log.check_out_time ? new Date(log.check_out_time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : '-'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {showRequestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowRequestModal(false)}>
          <div className="card w-full max-w-md mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold text-white/90 mb-4">Attendance Request</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Type</label>
                <select value={requestType} onChange={(e) => setRequestType(e.target.value)} className="input-field w-full">
                  <option value="late">Late Check-In</option>
                  <option value="early">Early Departure</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-1">Reason *</label>
                <textarea value={requestReason} onChange={(e) => setRequestReason(e.target.value)} className="input-field w-full h-24 resize-none" placeholder="Explain why..." />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowRequestModal(false)} className="px-4 py-2 rounded-xl text-sm font-medium text-white/60 hover:text-white/80 hover:bg-white/5 transition-all">Cancel</button>
              <button onClick={handleSubmitRequest} disabled={actionLoading === 'submit-request'} className="btn-primary text-sm">
                {actionLoading === 'submit-request' ? 'Submitting...' : 'Submit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
