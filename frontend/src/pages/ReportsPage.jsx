import React, { useState, useEffect, useCallback } from 'react';
import { useToast } from '../components/Toast';
import reportsApi from '../api/reportsApi';

const TABS = [
  { key: 'attendance', label: 'Attendance' },
  { key: 'students', label: 'Students' },
  { key: 'projects', label: 'Projects' },
  { key: 'todos', label: 'Todos' },
  { key: 'activity', label: 'Activity' },
];

function todayStr() {
  const d = new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

function AttendanceReport() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState(daysAgo(29));
  const [endDate, setEndDate] = useState(todayStr());

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await reportsApi.attendance({ start_date: startDate, end_date: endDate });
      setData(res.data);
    } catch (err) {
      toast.error(err.message || 'Failed to load attendance report');
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, toast]);

  useEffect(() => { fetch(); }, [fetch]);

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <label className="text-xs text-white/60 self-center">From:</label>
        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="input-field w-auto" />
        <label className="text-xs text-white/60 self-center">To:</label>
        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="input-field w-auto" />
        <button onClick={fetch} className="btn-primary text-sm py-2" disabled={loading}>Refresh</button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" /></div>
      ) : data ? (
        <>
          {data.summary && (
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="stat-card text-center">
                <p className="text-2xl font-bold text-emerald-400">{data.summary.total_present}</p>
                <p className="text-xs text-white/50">Present</p>
              </div>
              <div className="stat-card text-center">
                <p className="text-2xl font-bold text-rose-400">{data.summary.total_absent}</p>
                <p className="text-xs text-white/50">Absent</p>
              </div>
              <div className="stat-card text-center">
                <p className="text-2xl font-bold text-amber-400">{data.summary.total_late}</p>
                <p className="text-xs text-white/50">Late</p>
              </div>
            </div>
          )}
          <div className="table-container">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="table-header text-left py-3 px-4">Date</th>
                  <th className="table-header text-left py-3 px-4">Total</th>
                  <th className="table-header text-left py-3 px-4">Present</th>
                  <th className="table-header text-left py-3 px-4">Absent</th>
                  <th className="table-header text-left py-3 px-4">Late</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {data.report?.map((row, i) => (
                  <tr key={row.date} className="table-row" style={{ animationDelay: `${i * 20}ms` }}>
                    <td className="py-2.5 px-4 text-sm text-white/80">{row.date}</td>
                    <td className="py-2.5 px-4 text-sm text-white/80">{row.total}</td>
                    <td className="py-2.5 px-4 text-sm text-emerald-400">{row.present}</td>
                    <td className="py-2.5 px-4 text-sm text-rose-400">{row.absent}</td>
                    <td className="py-2.5 px-4 text-sm text-amber-400">{row.late}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </div>
  );
}

function StudentsReport() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsApi.students()
      .then((res) => setData(res.data))
      .catch((err) => toast.error(err.message || 'Failed to load student report'))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" /></div>;
  if (!data?.students?.length) return <p className="text-white/50 text-sm py-8 text-center">No student data available</p>;

  return (
    <div className="table-container">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/5">
            <th className="table-header text-left py-3 px-4">Student</th>
            <th className="table-header text-left py-3 px-4">Todos</th>
            <th className="table-header text-left py-3 px-4">Projects</th>
            <th className="table-header text-left py-3 px-4">Attendance</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {data.students.map((s, i) => (
            <tr key={s.student_id} className="table-row" style={{ animationDelay: `${i * 20}ms` }}>
              <td className="py-3 px-4">
                <p className="text-sm font-semibold text-white/90">{s.name}</p>
                <p className="text-xs text-white/40">{s.email}</p>
              </td>
              <td className="py-3 px-4">
                <span className="text-sm text-white/80">{s.todos.completed}/{s.todos.total}</span>
              </td>
              <td className="py-3 px-4">
                <span className="text-sm text-white/80">{s.projects.completed}/{s.projects.total}</span>
              </td>
              <td className="py-3 px-4">
                <span className="text-sm text-white/80">{s.attendance.present}/{s.attendance.total}</span>
                <span className="text-xs text-white/40 ml-1">({s.attendance.attendance_rate}%)</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ProjectsReport() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsApi.projects()
      .then((res) => setData(res.data))
      .catch((err) => toast.error(err.message || 'Failed to load project report'))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" /></div>;

  const stats = data?.status_breakdown || {};
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div className="stat-card text-center">
        <p className="text-3xl font-bold text-amber-400">{stats.not_started || 0}</p>
        <p className="text-xs text-white/50 mt-1">Not Started</p>
      </div>
      <div className="stat-card text-center">
        <p className="text-3xl font-bold text-sky-400">{stats.in_progress || 0}</p>
        <p className="text-xs text-white/50 mt-1">In Progress</p>
      </div>
      <div className="stat-card text-center">
        <p className="text-3xl font-bold text-emerald-400">{stats.completed || 0}</p>
        <p className="text-xs text-white/50 mt-1">Completed</p>
      </div>
      <div className="card col-span-full text-center">
        <p className="text-sm text-white/60">Total Projects: <strong className="text-white">{data?.total_projects || 0}</strong></p>
      </div>
    </div>
  );
}

function TodosReport() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsApi.todos()
      .then((res) => setData(res.data))
      .catch((err) => toast.error(err.message || 'Failed to load todo report'))
      .finally(() => setLoading(false));
  }, [toast]);

  if (loading) return <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" /></div>;

  const stats = data?.status_breakdown || {};
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div className="stat-card text-center">
        <p className="text-3xl font-bold text-amber-400">{stats.pending || 0}</p>
        <p className="text-xs text-white/50 mt-1">Pending</p>
      </div>
      <div className="stat-card text-center">
        <p className="text-3xl font-bold text-sky-400">{stats.in_progress || 0}</p>
        <p className="text-xs text-white/50 mt-1">In Progress</p>
      </div>
      <div className="stat-card text-center">
        <p className="text-3xl font-bold text-emerald-400">{stats.completed || 0}</p>
        <p className="text-xs text-white/50 mt-1">Completed</p>
      </div>
      <div className="card col-span-full text-center">
        <p className="text-sm text-white/60">Total Todos: <strong className="text-white">{data?.total_todos || 0}</strong></p>
      </div>
    </div>
  );
}

function ActivityReport() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState(daysAgo(6));
  const [endDate, setEndDate] = useState(todayStr());

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await reportsApi.activity({ start_date: startDate, end_date: endDate, limit: 100 });
      setData(res.data);
    } catch (err) {
      toast.error(err.message || 'Failed to load activity report');
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, toast]);

  useEffect(() => { fetch(); }, [fetch]);

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <label className="text-xs text-white/60 self-center">From:</label>
        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="input-field w-auto" />
        <label className="text-xs text-white/60 self-center">To:</label>
        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="input-field w-auto" />
        <button onClick={fetch} className="btn-primary text-sm py-2" disabled={loading}>Refresh</button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" /></div>
      ) : !data?.activity_logs?.length ? (
        <p className="text-white/50 text-sm py-8 text-center">No activity found</p>
      ) : (
        <div className="table-container">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="table-header text-left py-3 px-4">Time</th>
                <th className="table-header text-left py-3 px-4">Action</th>
                <th className="table-header text-left py-3 px-4">Description</th>
                <th className="table-header text-left py-3 px-4">Entity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {data.activity_logs.map((log, i) => (
                <tr key={log.id} className="table-row" style={{ animationDelay: `${i * 10}ms` }}>
                  <td className="py-2.5 px-4 text-xs text-white/40 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="badge-brand text-xs">{log.action}</span>
                  </td>
                  <td className="py-2.5 px-4 text-sm text-white/70">{log.description}</td>
                  <td className="py-2.5 px-4 text-xs text-white/40">{log.entity_type || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const TAB_COMPONENTS = {
  attendance: AttendanceReport,
  students: StudentsReport,
  projects: ProjectsReport,
  todos: TodosReport,
  activity: ActivityReport,
};

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState('attendance');

  const ActiveComponent = TAB_COMPONENTS[activeTab];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Reports</h1>
          <p className="text-sm text-white/50 mt-1">View and analyze system data</p>
        </div>
        <button className="btn-secondary text-sm py-2" onClick={() => window.alert('Export feature coming soon')}>
          <svg className="w-4 h-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export
        </button>
      </div>

      <div className="flex gap-1 bg-white/5 rounded-xl p-1 flex-wrap">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
              activeTab === tab.key
                ? 'bg-white/10 text-white shadow-sm'
                : 'text-white/50 hover:text-white/80'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="animate-fade-in" key={activeTab}>
        <ActiveComponent />
      </div>
    </div>
  );
}
