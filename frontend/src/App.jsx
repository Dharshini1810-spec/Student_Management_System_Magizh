import React, { useState, useEffect } from 'react';
import client from './api/client';

// SVG Icons for clean, zero-dependency visual excellence
const Icons = {
  Dashboard: () => (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" />
    </svg>
  ),
  Students: () => (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
    </svg>
  ),
  Users: () => (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  ),
  Roles: () => (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  ),
  Logout: () => (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  ),
  Search: () => (
    <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  Plus: () => (
    <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  ),
  Edit: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
    </svg>
  ),
  Delete: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  ),
  Key: () => (
    <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m-5 4a5 5 0 01-10 0 5 5 0 0110 0zm0 0l3 3m0 0l3-3m-3 3V15" />
    </svg>
  ),
  Assign: () => (
    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
    </svg>
  ),
  Attendance: () => (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  )
};

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Scoped lists & states
  const [students, setStudents] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  
  // Dropdowns for assignments
  const [adminsList, setAdminsList] = useState([]);
  const [mentorsList, setMentorsList] = useState([]);

  // Stats
  const [stats, setStats] = useState({
    total_users: 0,
    total_admins: 0,
    total_mentors: 0,
    total_students: 0,
    present_today: 0,
    absent_today: 0,
    active_projects: 0,
    pending_attendance_requests: 0,
    completed_todos: 0
  });

  // Attendance States
  const [attendanceLogs, setAttendanceLogs] = useState([]);
  const [attendanceRequests, setAttendanceRequests] = useState([]);
  const [attendanceSettings, setAttendanceSettings] = useState({ check_in_deadline: '09:00', check_out_deadline: '17:00' });
  const [attendanceReason, setAttendanceReason] = useState('');
  const [settingsForm, setSettingsForm] = useState({ check_in_deadline: '09:00', check_out_deadline: '17:00' });

  // Filters & Pagination
  const [search, setSearch] = useState('');
  const [isActiveFilter, setIsActiveFilter] = useState('ALL');
  const [showDeleted, setShowDeleted] = useState(false);
  const [studentLimit] = useState(10);
  const [studentOffset, setStudentOffset] = useState(0);
  const [studentsCount, setStudentsCount] = useState(0);

  // Modals / Modifiers
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState('');
  const [modalType, setModalType] = useState(null); // 'create_student', 'edit_student', 'assign_admin', 'assign_mentor'
  const [selectedStudent, setSelectedStudent] = useState(null);
  
  // Login Form States
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isSignup, setIsSignup] = useState(false); // If bootstrapping Super Admin

  // Form inputs
  const [studentForm, setStudentForm] = useState({
    name: '',
    email: '',
    nickname: '',
    dob: '',
    contact: '',
    position: '',
    avatar: '',
    password: ''
  });

  const [assignForm, setAssignForm] = useState({
    targetId: ''
  });

  // Decode profile info
  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    } else {
      setCurrentUser(null);
    }
  }, [token]);

  // Handle auto-refresh on active changes
  useEffect(() => {
    if (currentUser) {
      loadData();
    }
  }, [currentUser, activeTab, search, isActiveFilter, showDeleted, studentOffset]);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchCurrentUser = async () => {
    try {
      const res = await client.get('/api/v1/auth/me');
      setCurrentUser(res.data);
    } catch (err) {
      setToken('');
      localStorage.removeItem('token');
    }
  };

  const loadData = async () => {
    if (!currentUser) return;
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        let endpoint = '/api/v1/dashboard/student';
        if (currentUser.role === 'SUPER_ADMIN') {
          endpoint = '/api/v1/dashboard/super-admin';
        } else if (currentUser.role === 'ADMIN') {
          endpoint = '/api/v1/dashboard/admin';
        } else if (currentUser.role === 'MENTOR') {
          endpoint = '/api/v1/dashboard/mentor';
        }
        
        const res = await client.get(endpoint);
        setStats(res.data);
      }

      if (activeTab === 'students') {
        const params = {
          limit: studentLimit,
          offset: studentOffset,
          include_deleted: showDeleted
        };
        if (search) params.search = search;
        if (isActiveFilter !== 'ALL') params.is_active = isActiveFilter === 'ACTIVE';

        const res = await client.get('/api/v1/students', { params });
        setStudents(res.data.students || []);
        setStudentsCount(res.data.total_count || 0);

        // Preload admins/mentors list for assignments if they are not already loaded
        if (currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') {
          const admRes = await client.get('/api/v1/users', { params: { role: 'ADMIN', limit: 100 } });
          const menRes = await client.get('/api/v1/users', { params: { role: 'MENTOR', limit: 100 } });
          setAdminsList(admRes.data.users || []);
          setMentorsList(menRes.data.users || []);
        }
      }

      if (activeTab === 'users') {
        const res = await client.get('/api/v1/users', { params: { limit: 100 } });
        setUsersList(res.data.users || []);
      }

      if (activeTab === 'permissions') {
        const rolesRes = await client.get('/api/v1/roles');
        const permsRes = await client.get('/api/v1/permissions');
        setRoles(rolesRes.data || []);
        setPermissions(permsRes.data || []);
      }

      if (activeTab === 'attendance') {
        const logsRes = await client.get('/api/v1/attendance');
        setAttendanceLogs(logsRes.data.logs || []);

        const settingsRes = await client.get('/api/v1/attendance/settings');
        setAttendanceSettings(settingsRes.data);
        setSettingsForm({
          check_in_deadline: settingsRes.data.check_in_deadline,
          check_out_deadline: settingsRes.data.check_out_deadline
        });

        const reqsRes = await client.get('/api/v1/attendance/requests');
        setAttendanceRequests(reqsRes.data.requests || []);
      }
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to retrieve data.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    setLoading(true);
    try {
      if (isSignup) {
        // Bootstrap Super Admin
        await client.post('/api/v1/auth/signup', {
          email: loginEmail,
          password: loginPassword
        });
        showToast('Super Admin registered successfully! Logging in...');
        setIsSignup(false);
      }
      
      const res = await client.post('/api/v1/auth/login', {
        email: loginEmail,
        password: loginPassword
      });
      localStorage.setItem('token', res.data.access_token);
      setToken(res.data.access_token);
      setLoginEmail('');
      setLoginPassword('');
    } catch (err) {
      setAuthError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setCurrentUser(null);
    setActiveTab('dashboard');
  };

  const handleDemoSwitch = async (role) => {
    setLoading(true);
    try {
      let email, password;
      if (role === 'SUPER_ADMIN') {
        email = 'admin@sms.com';
        password = 'SuperAdminSecurePassword123!';
      } else if (role === 'ADMIN') {
        email = 'demo_admin@sms.com';
        password = 'StandardPassword123!';
      } else if (role === 'MENTOR') {
        email = 'demo_mentor@sms.com';
        password = 'StandardPassword123!';
      } else if (role === 'STUDENT') {
        email = 'demo_student@sms.com';
        password = 'StandardPassword123!';
      }

      try {
        const res = await client.post('/api/v1/auth/login', { email, password });
        localStorage.setItem('token', res.data.access_token);
        setToken(res.data.access_token);
        showToast(`Switched simulation to: ${role}`);
      } catch (err) {
        // Self-Healing Bootstrap
        showToast(`Bootstrapping simulation account for ${role}...`, 'info');
        
        // Log in as Super Admin first to make users
        const saRes = await client.post('/api/v1/auth/login', {
          email: 'admin@sms.com',
          password: 'SuperAdminSecurePassword123!'
        });
        const saToken = saRes.data.access_token;
        const config = { headers: { Authorization: `Bearer ${saToken}` } };

        // Ensure we create target
        try {
          await client.post('/api/v1/users', {
            email,
            role,
            name: `Demo ${role.replace('_', ' ').toLowerCase()}`
          }, config);
        } catch (createErr) {
          // ignore duplicate errors
        }

        // Retry login
        const retryRes = await client.post('/api/v1/auth/login', { email, password });
        localStorage.setItem('token', retryRes.data.access_token);
        setToken(retryRes.data.access_token);
        showToast(`Simulation configured successfully as ${role}`);
      }
    } catch (err) {
      showToast(`Bootstrapping error: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStudent = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post('/api/v1/students', studentForm);
      showToast('Student successfully created!');
      setModalType(null);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleEditStudent = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.put(`/api/v1/students/${selectedStudent.id}`, studentForm);
      showToast('Student profile updated successfully.');
      setModalType(null);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteStudent = async (id) => {
    if (!window.confirm('Are you sure you want to soft delete this student?')) return;
    setLoading(true);
    try {
      await client.delete(`/api/v1/students/${id}`);
      showToast('Student profile soft-deleted.');
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignAdmin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post(`/api/v1/students/${selectedStudent.id}/assign-admin`, {
        admin_id: assignForm.targetId
      });
      showToast('Admin successfully assigned.');
      setModalType(null);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignMentor = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post(`/api/v1/students/${selectedStudent.id}/assign-mentor`, {
        mentor_id: assignForm.targetId
      });
      showToast('Mentor successfully assigned.');
      setModalType(null);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserActivation = async (user) => {
    const action = user.is_active ? 'deactivate' : 'activate';
    setLoading(true);
    try {
      await client.patch(`/api/v1/users/${user.id}/${action}`);
      showToast(`User account ${action}d successfully.`);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (user) => {
    if (!window.confirm(`Reset password for ${user.email} to default standard password?`)) return;
    setLoading(true);
    try {
      await client.patch(`/api/v1/users/${user.id}/reset-password`);
      showToast(`Password successfully reset to default standard password.`);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async (reason = '') => {
    setLoading(true);
    try {
      const res = await client.post('/api/v1/attendance/check-in', { reason });
      if (res.data.status === 'LATE_REQUEST_PENDING') {
        showToast('Check-in deadline passed. Late request submitted for Admin review.', 'info');
      } else {
        showToast('Successfully checked in today!');
      }
      setAttendanceReason('');
      setModalType(null);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async (reason = '') => {
    setLoading(true);
    try {
      const res = await client.post('/api/v1/attendance/check-out', { reason });
      if (res.data.status === 'LATE_REQUEST_PENDING') {
        showToast('Check-out deadline not reached. Early checkout request submitted.', 'info');
      } else {
        showToast('Successfully checked out today!');
      }
      setAttendanceReason('');
      setModalType(null);
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post('/api/v1/attendance/settings', settingsForm);
      showToast('Attendance deadlines updated successfully.');
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveRequest = async (requestId) => {
    setLoading(true);
    try {
      await client.post(`/api/v1/attendance/requests/${requestId}/approve`);
      showToast('Attendance request approved successfully.');
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRejectRequest = async (requestId) => {
    setLoading(true);
    try {
      await client.post(`/api/v1/attendance/requests/${requestId}/reject`);
      showToast('Attendance request rejected.');
      loadData();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setStudentForm({
      name: '',
      email: '',
      nickname: '',
      dob: '',
      contact: '',
      position: '',
      avatar: '',
      password: ''
    });
    setModalType('create_student');
  };

  const openEditModal = (student) => {
    setSelectedStudent(student);
    setStudentForm({
      name: student.name,
      email: student.email,
      nickname: student.nickname || '',
      dob: student.dob ? student.dob.split('T')[0] : '',
      contact: student.contact || '',
      position: student.position || '',
      avatar: student.avatar || '',
      is_active: student.is_active
    });
    setModalType('edit_student');
  };

  const openAssignModal = (student, type) => {
    setSelectedStudent(student);
    setAssignForm({ targetId: '' });
    setModalType(type);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-brand-500 selection:text-white">
      {/* Toast Alert */}
      {toast && (
        <div className={`fixed top-5 right-5 z-[100] px-4 py-3 rounded-lg shadow-xl text-sm font-semibold flex items-center space-x-2 animate-slideIn border ${
          toast.type === 'error' ? 'bg-rose-50 border-rose-200 text-rose-800' : 
          toast.type === 'info' ? 'bg-indigo-50 border-indigo-200 text-indigo-800' :
          'bg-emerald-50 border-emerald-200 text-emerald-800'
        }`}>
          <span className={`w-2 h-2 rounded-full ${
            toast.type === 'error' ? 'bg-rose-500' : 
            toast.type === 'info' ? 'bg-indigo-500' :
            'bg-emerald-500'
          } animate-pulse`}></span>
          <span>{toast.message}</span>
        </div>
      )}

      {!token ? (
        // Beautiful Premium Login Screen
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-brand-950 p-6">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden border border-slate-100 p-8 space-y-6">
            <div className="text-center space-y-2">
              <div className="inline-flex h-12 w-12 rounded-xl bg-brand-600 items-center justify-center text-white font-black text-2xl shadow-lg shadow-brand-500/30">
                M
              </div>
              <h2 className="text-2xl font-black text-slate-800 tracking-tight">
                {isSignup ? 'Bootstrap Super Admin' : 'Welcome to Magizh SMS'}
              </h2>
              <p className="text-sm text-slate-500">
                {isSignup ? 'Register the root administrator account.' : 'Sign in to access your administrative workspace.'}
              </p>
            </div>

            {authError && (
              <div className="p-3 bg-rose-50 border border-rose-100 rounded-lg text-xs font-semibold text-rose-700 flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                <span>{authError}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  placeholder="name@company.com"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all placeholder:text-slate-300"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all placeholder:text-slate-300"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-brand-600 hover:bg-brand-700 disabled:bg-slate-400 text-white rounded-lg text-sm font-semibold transition-colors shadow-md shadow-brand-500/20"
              >
                {loading ? 'Processing...' : isSignup ? 'Create Administrator' : 'Sign In'}
              </button>
            </form>

            <div className="relative flex py-2 items-center">
              <div className="flex-grow border-t border-slate-100"></div>
              <span className="flex-shrink mx-4 text-slate-400 text-xs font-medium uppercase tracking-wider">
                Or Quick Access Demo
              </span>
              <div className="flex-grow border-t border-slate-100"></div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleDemoSwitch('SUPER_ADMIN')}
                className="p-3 border border-slate-150 rounded-xl bg-slate-50 hover:bg-white hover:border-brand-500 hover:shadow-md hover:shadow-brand-500/5 transition-all text-left flex flex-col justify-between"
              >
                <span className="text-xs font-bold text-slate-700 block mb-0.5">Super Admin</span>
                <span className="text-[10px] text-slate-400">Total Scoped View</span>
              </button>
              <button
                onClick={() => handleDemoSwitch('ADMIN')}
                className="p-3 border border-slate-150 rounded-xl bg-slate-50 hover:bg-white hover:border-brand-500 hover:shadow-md hover:shadow-brand-500/5 transition-all text-left flex flex-col justify-between"
              >
                <span className="text-xs font-bold text-slate-700 block mb-0.5">Admin</span>
                <span className="text-[10px] text-slate-400">Co-ordinator Scoped</span>
              </button>
              <button
                onClick={() => handleDemoSwitch('MENTOR')}
                className="p-3 border border-slate-150 rounded-xl bg-slate-50 hover:bg-white hover:border-brand-500 hover:shadow-md hover:shadow-brand-500/5 transition-all text-left flex flex-col justify-between"
              >
                <span className="text-xs font-bold text-slate-700 block mb-0.5">Mentor</span>
                <span className="text-[10px] text-slate-400">Student Mentoring</span>
              </button>
              <button
                onClick={() => handleDemoSwitch('STUDENT')}
                className="p-3 border border-slate-150 rounded-xl bg-slate-50 hover:bg-white hover:border-brand-500 hover:shadow-md hover:shadow-brand-500/5 transition-all text-left flex flex-col justify-between"
              >
                <span className="text-xs font-bold text-slate-700 block mb-0.5">Student</span>
                <span className="text-[10px] text-slate-400">Personal Profile</span>
              </button>
            </div>

            <div className="text-center pt-2">
              <button
                onClick={() => setIsSignup(!isSignup)}
                className="text-xs text-brand-600 hover:underline font-semibold"
              >
                {isSignup ? 'Back to sign in' : 'Need to bootstrap Super Admin? Sign up here'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        // Beautiful Core Application Dashboard
        <div className="flex-grow flex h-screen overflow-hidden">
          {/* Left Navigation Sidebar */}
          <aside className="w-64 bg-slate-900 flex flex-col text-slate-300">
            <div className="h-16 flex items-center px-6 border-b border-slate-800 space-x-3">
              <div className="h-8 w-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-extrabold shadow-md shadow-brand-500/20">
                M
              </div>
              <span className="font-extrabold text-white text-lg tracking-tight">Magizh SMS</span>
            </div>

            {/* Sidebar Tabs */}
            <nav className="flex-grow p-4 space-y-1.5">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'dashboard' ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/10' : 'hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Icons.Dashboard />
                <span>Dashboard</span>
              </button>

              <button
                onClick={() => setActiveTab('students')}
                className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'students' ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/10' : 'hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Icons.Students />
                <span>Student Directory</span>
              </button>

              <button
                onClick={() => setActiveTab('attendance')}
                className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === 'attendance' ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/10' : 'hover:bg-slate-800 hover:text-white'
                }`}
              >
                <Icons.Attendance />
                <span>Attendance Log</span>
              </button>

              {currentUser?.role === 'SUPER_ADMIN' && (
                <button
                  onClick={() => setActiveTab('users')}
                  className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    activeTab === 'users' ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/10' : 'hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Icons.Users />
                  <span>User Accounts</span>
                </button>
              )}

              {currentUser?.role === 'SUPER_ADMIN' && (
                <button
                  onClick={() => setActiveTab('permissions')}
                  className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    activeTab === 'permissions' ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/10' : 'hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Icons.Roles />
                  <span>Access Matrix</span>
                </button>
              )}
            </nav>

            {/* User Footer Profile */}
            <div className="p-4 border-t border-slate-800 flex flex-col space-y-3">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center font-bold text-brand-400">
                  {currentUser?.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="min-w-0 flex-grow">
                  <span className="font-semibold text-white block text-sm truncate">{currentUser?.name || 'User Profile'}</span>
                  <span className="text-[10px] font-black tracking-wider text-brand-400 uppercase bg-brand-950 px-1.5 py-0.5 rounded block w-fit mt-0.5">
                    {currentUser?.role}
                  </span>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center space-x-2 py-2 border border-slate-800 hover:border-rose-900/50 hover:bg-rose-950/20 hover:text-rose-400 rounded-lg text-xs font-bold transition-all"
              >
                <Icons.Logout />
                <span>Sign Out</span>
              </button>
            </div>
          </aside>

          {/* Main Dashboard Section */}
          <main className="flex-grow flex flex-col h-full overflow-hidden bg-slate-50">
            {/* Top Navigation Navbar */}
            <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 z-10 shrink-0">
              <h2 className="text-xl font-extrabold text-slate-800 capitalize tracking-tight">
                {activeTab.replace('_', ' ')} Overview
              </h2>

              {/* Header Selector Switcher */}
              <div className="flex items-center space-x-3">
                <div className="bg-slate-100 rounded-lg p-1 flex items-center space-x-1">
                  <span className="text-xs font-bold text-slate-500 px-2">Simulation Role:</span>
                  {['SUPER_ADMIN', 'ADMIN', 'MENTOR', 'STUDENT'].map((role) => (
                    <button
                      key={role}
                      onClick={() => handleDemoSwitch(role)}
                      className={`px-2.5 py-1 text-xs font-bold rounded-md transition-all ${
                        currentUser?.role === role ? 'bg-brand-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      {role.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>
            </header>

            {/* Active Workspace Viewport */}
            <div className="flex-grow overflow-y-auto p-8 relative">
              {loading && (
                <div className="absolute inset-0 bg-white/50 backdrop-blur-xs flex items-center justify-center z-50">
                  <div className="animate-spin rounded-full h-8 w-8 border-4 border-brand-500 border-t-transparent"></div>
                </div>
              )}

              {/* View Dashboard */}
              {activeTab === 'dashboard' && (
                <div className="space-y-8 animate-fadeIn">
                  {/* Banner */}
                  <div className="bg-gradient-to-br from-slate-900 via-slate-850 to-brand-900 rounded-2xl p-8 md:p-10 text-white shadow-lg border border-slate-850 flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                      <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
                        Magizh SMS Dashboard
                      </h1>
                      <p className="text-slate-300 text-sm mt-2 max-w-xl">
                        Simulate, test, and manage student registry assignments, active status controls, and robust role-scoping permission boundaries.
                      </p>
                    </div>
                    <div className="mt-4 md:mt-0 px-5 py-3.5 bg-white/10 backdrop-blur-md rounded-xl border border-white/10 shrink-0">
                      <span className="text-[10px] font-black uppercase text-brand-400 block tracking-widest">Signed In As</span>
                      <span className="text-base font-bold text-white block mt-0.5">{currentUser?.email}</span>
                    </div>
                  </div>

                  {/* Stat metrics */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Total Users */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Users</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-slate-800">{stats.total_users}</span>
                        <span className="text-xs font-bold text-slate-600 bg-slate-50 px-2 py-0.5 rounded">All Registered</span>
                      </div>
                    </div>

                    {/* Total Admins */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Admins</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-slate-800">{stats.total_admins}</span>
                        <span className="text-xs font-bold text-indigo-650 bg-indigo-50 px-2 py-0.5 rounded">Co-ordinators</span>
                      </div>
                    </div>

                    {/* Total Mentors */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Mentors</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-slate-800">{stats.total_mentors}</span>
                        <span className="text-xs font-bold text-amber-650 bg-amber-50 px-2 py-0.5 rounded">Instructors</span>
                      </div>
                    </div>

                    {/* Total Students */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Students</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-slate-800">{stats.total_students}</span>
                        <span className="text-xs font-bold text-brand-600 bg-brand-50 px-2 py-0.5 rounded">Learners</span>
                      </div>
                    </div>

                    {/* Present Today */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Present Today</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-emerald-700">{stats.present_today}</span>
                        <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">Attendance</span>
                      </div>
                    </div>

                    {/* Absent Today */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Absent Today</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-rose-700">{stats.absent_today}</span>
                        <span className="text-xs font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded">Leaves</span>
                      </div>
                    </div>

                    {/* Active Projects */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Active Projects</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-blue-700">{stats.active_projects}</span>
                        <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">In Progress</span>
                      </div>
                    </div>

                    {/* Pending Attendance Requests */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Pending Attendance Requests</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-amber-700">{stats.pending_attendance_requests}</span>
                        <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded">Awaiting Approval</span>
                      </div>
                    </div>

                    {/* Completed Todos */}
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Completed Todos</span>
                      <div className="flex justify-between items-end mt-4">
                        <span className="text-3xl font-black text-purple-700">{stats.completed_todos}</span>
                        <span className="text-xs font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded">Tasks Done</span>
                      </div>
                    </div>
                  </div>

                  {/* Scoping rules info box */}
                  <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6">
                    <h3 className="text-base font-bold text-slate-800 mb-4">Active Database Data Access Scoping Rules</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
                        <span className="text-xs font-bold text-indigo-700 block mb-1">Super Admin View</span>
                        <p className="text-xs text-slate-500">Unrestricted query scope. Can view, edit, activate/deactivate, delete all student records, users, and configure assignments.</p>
                      </div>
                      <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
                        <span className="text-xs font-bold text-emerald-700 block mb-1">Admin View</span>
                        <p className="text-xs text-slate-500">Access limited only to students assigned to them via the admin_students junction mapping. Can view assigned mentors.</p>
                      </div>
                      <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
                        <span className="text-xs font-bold text-amber-700 block mb-1">Mentor View</span>
                        <p className="text-xs text-slate-500">Strictly scoped access. Can only view student profile summaries assigned to them via the mentor_students junction mapping.</p>
                      </div>
                      <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
                        <span className="text-xs font-bold text-rose-700 block mb-1">Student View</span>
                        <p className="text-xs text-slate-500">Personal access only. Scoped directly to the student's own identifier. Cannot view other records.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* View Attendance */}
              {activeTab === 'attendance' && (
                <div className="space-y-8 animate-fadeIn">
                  {/* Attendance Configuration and Check-in for Student */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Settings card (Admins/Super Admins only) */}
                    {(currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') ? (
                      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
                        <div>
                          <h3 className="text-base font-extrabold text-slate-800 mb-1">Deadlines Configuration</h3>
                          <p className="text-xs text-slate-500 mb-4">Update check-in and check-out rules for all students.</p>
                          <form onSubmit={handleSaveSettings} className="space-y-4">
                            <div>
                              <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Check-in Limit (Late limit)</label>
                              <input
                                type="text"
                                placeholder="09:00"
                                required
                                className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                                value={settingsForm.check_in_deadline}
                                onChange={(e) => setSettingsForm({ ...settingsForm, check_in_deadline: e.target.value })}
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Check-out Limit (Early limit)</label>
                              <input
                                type="text"
                                placeholder="17:00"
                                required
                                className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                                value={settingsForm.check_out_deadline}
                                onChange={(e) => setSettingsForm({ ...settingsForm, check_out_deadline: e.target.value })}
                              />
                            </div>
                            <button
                              type="submit"
                              className="w-full py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold transition-colors"
                            >
                              Save Deadlines Settings
                            </button>
                          </form>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
                        <div>
                          <h3 className="text-base font-extrabold text-slate-800 mb-1">Attendance Information</h3>
                          <p className="text-xs text-slate-500 mb-4">Official daily timelines enforced by coordinators.</p>
                          <div className="space-y-3 mt-4 text-xs">
                            <div className="flex justify-between border-b border-slate-100 pb-2">
                              <span className="font-semibold text-slate-500">Check-in Deadline:</span>
                              <span className="font-bold text-slate-800">{attendanceSettings.check_in_deadline} AM</span>
                            </div>
                            <div className="flex justify-between border-b border-slate-100 pb-2">
                              <span className="font-semibold text-slate-500">Check-out Deadline:</span>
                              <span className="font-bold text-slate-800">{attendanceSettings.check_out_deadline} PM</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Student Action buttons (only Student role) */}
                    {currentUser.role === 'STUDENT' && (
                      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between lg:col-span-2">
                        <div>
                          <h3 className="text-base font-extrabold text-slate-800 mb-1">Daily Log Action Console</h3>
                          <p className="text-xs text-slate-500 mb-4">Submit your daily registry check-in and check-out logs.</p>
                          
                          <div className="grid grid-cols-2 gap-4 mt-6">
                            {/* Check-in Trigger */}
                            <div className="p-4 border border-slate-150 rounded-xl bg-slate-50 flex flex-col justify-between items-center text-center">
                              <span className="text-xs font-bold text-slate-700 block mb-2">Check-in Session</span>
                              <button
                                onClick={() => {
                                  const localTime = `${String(new Date().getHours()).padStart(2,'0')}:${String(new Date().getMinutes()).padStart(2,'0')}`;
                                  if (localTime > attendanceSettings.check_in_deadline) {
                                    setModalType('late_check_in');
                                  } else {
                                    handleCheckIn();
                                  }
                                }}
                                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition-all shadow-xs"
                              >
                                Trigger Check-in
                              </button>
                            </div>

                            {/* Check-out Trigger */}
                            <div className="p-4 border border-slate-150 rounded-xl bg-slate-50 flex flex-col justify-between items-center text-center">
                              <span className="text-xs font-bold text-slate-700 block mb-2">Check-out Session</span>
                              <button
                                onClick={() => {
                                  const localTime = `${String(new Date().getHours()).padStart(2,'0')}:${String(new Date().getMinutes()).padStart(2,'0')}`;
                                  if (localTime < attendanceSettings.check_out_deadline) {
                                    setModalType('late_check_out');
                                  } else {
                                    handleCheckOut();
                                  }
                                }}
                                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all shadow-xs"
                              >
                                Trigger Check-out
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Late Attendance Requests list (only visible to Super Admin / Admin / Mentor) */}
                  {currentUser.role !== 'STUDENT' && (
                    <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6">
                      <h3 className="text-base font-extrabold text-slate-800 mb-4 tracking-tight">Time Extension & Late Requests</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="bg-slate-50/75 border-b border-slate-200 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                              <th className="px-4 py-3">Student</th>
                              <th className="px-4 py-3">Request Type</th>
                              <th className="px-4 py-3">Time Filed</th>
                              <th className="px-4 py-3">Reason / Context</th>
                              <th className="px-4 py-3">Status</th>
                              {(currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') && <th className="px-4 py-3 text-right">Approval Actions</th>}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100 text-xs">
                            {attendanceRequests.length === 0 ? (
                              <tr>
                                <td colSpan="6" className="px-4 py-8 text-center text-slate-400 font-medium">
                                  No pending or historical requests found.
                                </td>
                              </tr>
                            ) : (
                              attendanceRequests.map((req) => (
                                <tr key={req.id} className="hover:bg-slate-50/50 transition-colors">
                                  <td className="px-4 py-3 font-semibold text-slate-800">{req.student_name}</td>
                                  <td className="px-4 py-3 font-bold text-slate-600 text-[10px] uppercase">{req.request_type.replace('_',' ')}</td>
                                  <td className="px-4 py-3 text-slate-500">{new Date(req.requested_time).toLocaleString()}</td>
                                  <td className="px-4 py-3 text-slate-600 font-medium">{req.reason || <span className="text-slate-300">-</span>}</td>
                                  <td className="px-4 py-3">
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                      req.status === 'PENDING' ? 'bg-amber-50 text-amber-700' :
                                      req.status === 'APPROVED' ? 'bg-emerald-50 text-emerald-700' :
                                      'bg-rose-50 text-rose-700'
                                    }`}>
                                      {req.status}
                                    </span>
                                  </td>
                                  {(currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') && (
                                    <td className="px-4 py-3 text-right">
                                      {req.status === 'PENDING' ? (
                                        <div className="inline-flex space-x-1.5">
                                          <button
                                            onClick={() => handleApproveRequest(req.id)}
                                            className="px-2 py-1 bg-emerald-50 border border-emerald-100 hover:bg-emerald-100 text-emerald-700 font-bold rounded"
                                          >
                                            Approve
                                          </button>
                                          <button
                                            onClick={() => handleRejectRequest(req.id)}
                                            className="px-2 py-1 bg-rose-50 border border-rose-100 hover:bg-rose-100 text-rose-700 font-bold rounded"
                                          >
                                            Reject
                                          </button>
                                        </div>
                                      ) : (
                                        <span className="text-slate-400 font-semibold text-[10px]">Reviewed</span>
                                      )}
                                    </td>
                                  )}
                                </tr>
                              ))
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Attendance Logs List Table */}
                  <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6">
                    <h3 className="text-base font-extrabold text-slate-800 mb-4 tracking-tight">
                      {currentUser.role === 'STUDENT' ? 'My Attendance Registry Logs' : 'Student Attendance History'}
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-50/75 border-b border-slate-200 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                            {currentUser.role !== 'STUDENT' && <th className="px-4 py-3">Student Name</th>}
                            <th className="px-4 py-3">Date</th>
                            <th className="px-4 py-3">Check-in Time</th>
                            <th className="px-4 py-3">Check-out Time</th>
                            <th className="px-4 py-3">Status</th>
                            <th className="px-4 py-3">Notes</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 text-xs">
                          {attendanceLogs.length === 0 ? (
                            <tr>
                              <td colSpan="6" className="px-4 py-8 text-center text-slate-400 font-medium">
                                No attendance log history found.
                              </td>
                            </tr>
                          ) : (
                            attendanceLogs.map((log) => (
                              <tr key={log.id} className="hover:bg-slate-50/50 transition-colors">
                                {currentUser.role !== 'STUDENT' && <td className="px-4 py-3 font-semibold text-slate-800">{log.student_name}</td>}
                                <td className="px-4 py-3 font-semibold text-slate-600">{new Date(log.date).toLocaleDateString()}</td>
                                <td className="px-4 py-3 font-medium text-slate-500">{log.check_in_time ? new Date(log.check_in_time).toLocaleTimeString() : <span className="text-slate-300">-</span>}</td>
                                <td className="px-4 py-3 font-medium text-slate-500">{log.check_out_time ? new Date(log.check_out_time).toLocaleTimeString() : <span className="text-slate-300">-</span>}</td>
                                <td className="px-4 py-3">
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                    log.status === 'PRESENT' ? 'bg-emerald-50 text-emerald-700' :
                                    log.status === 'LATE' ? 'bg-amber-50 text-amber-700' :
                                    'bg-slate-100 text-slate-500'
                                  }`}>
                                    {log.status}
                                  </span>
                                </td>
                                <td className="px-4 py-3 text-slate-500 font-medium">
                                  {log.is_late_check_in && <span className="text-amber-600 font-semibold block">* Late Check-in</span>}
                                  {log.is_late_check_out && <span className="text-blue-600 font-semibold block">* Early Departure</span>}
                                  {!log.is_late_check_in && !log.is_late_check_out && <span className="text-slate-300">-</span>}
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* View Students List */}
              {activeTab === 'students' && (
                <div className="space-y-6 animate-fadeIn">
                  {/* Search and Action Bar */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
                    {/* Left filters */}
                    <div className="flex flex-wrap items-center gap-3">
                      <div className="relative">
                        <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Icons.Search />
                        </span>
                        <input
                          type="text"
                          placeholder="Search student details..."
                          className="pl-9 pr-4 py-1.5 border border-slate-200 rounded-lg text-xs w-60 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
                          value={search}
                          onChange={(e) => { setSearch(e.target.value); setStudentOffset(0); }}
                        />
                      </div>

                      <select
                        className="px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all font-semibold text-slate-600"
                        value={isActiveFilter}
                        onChange={(e) => { setIsActiveFilter(e.target.value); setStudentOffset(0); }}
                      >
                        <option value="ALL">All Status</option>
                        <option value="ACTIVE">Active Profiles</option>
                        <option value="INACTIVE">Deactivated Profiles</option>
                      </select>

                      {currentUser.role === 'SUPER_ADMIN' && (
                        <label className="flex items-center space-x-1.5 text-xs text-slate-600 font-semibold cursor-pointer select-none">
                          <input
                            type="checkbox"
                            className="rounded border-slate-350 text-brand-600 focus:ring-brand-500/20 h-3.5 w-3.5"
                            checked={showDeleted}
                            onChange={(e) => { setShowDeleted(e.target.checked); setStudentOffset(0); }}
                          />
                          <span>Show Deleted Profiles</span>
                        </label>
                      )}
                    </div>

                    {/* Create Action */}
                    {(currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') && (
                      <button
                        onClick={openCreateModal}
                        className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold flex items-center transition-colors shadow-xs"
                      >
                        <Icons.Plus />
                        <span>Register Student</span>
                      </button>
                    )}
                  </div>

                  {/* Student Table */}
                  <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-50/75 border-b border-slate-200 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                            <th className="px-6 py-4">Student Profile</th>
                            <th className="px-6 py-4">Nickname</th>
                            <th className="px-6 py-4">Position</th>
                            <th className="px-6 py-4">Date Joined</th>
                            <th className="px-6 py-4">Assigned Admin</th>
                            <th className="px-6 py-4">Assigned Mentor</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 text-xs">
                          {students.length === 0 ? (
                            <tr>
                              <td colSpan="7" className="px-6 py-12 text-center text-slate-400 font-medium">
                                No student profiles found matching your scope/filters.
                              </td>
                            </tr>
                          ) : (
                            students.map((student) => (
                              <tr key={student.id} className="hover:bg-slate-50/50 transition-colors">
                                <td className="px-6 py-4 flex items-center space-x-3">
                                  <div className="h-9 w-9 rounded-full bg-brand-50 flex items-center justify-center font-bold text-brand-700 uppercase">
                                    {student.name.charAt(0)}
                                  </div>
                                  <div>
                                    <span className="font-semibold text-slate-800 block text-sm">
                                      {student.name}
                                    </span>
                                    <span className="text-[10px] text-slate-400 block">{student.email}</span>
                                  </div>
                                </td>
                                <td className="px-6 py-4 font-semibold text-slate-600">
                                  {student.nickname || <span className="text-slate-300">-</span>}
                                </td>
                                <td className="px-6 py-4 text-slate-600 font-medium">
                                  {student.position || <span className="text-slate-300">-</span>}
                                </td>
                                <td className="px-6 py-4 text-slate-500 font-medium">
                                  {new Date(student.date_joined).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4">
                                  <div className="flex items-center space-x-1.5">
                                    {student.assigned_admin_id ? (
                                      <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded font-semibold text-[10px]">
                                        {adminsList.find(a => a.id === student.assigned_admin_id)?.name || 'Assigned Admin'}
                                      </span>
                                    ) : (
                                      <span className="text-slate-300 text-[10px]">Unassigned</span>
                                    )}
                                    {(currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') && (
                                      <button 
                                        onClick={() => openAssignModal(student, 'assign_admin')}
                                        className="text-slate-400 hover:text-brand-600 transition-colors"
                                        title="Change Admin Assignment"
                                      >
                                        <Icons.Assign />
                                      </button>
                                    )}
                                  </div>
                                </td>
                                <td className="px-6 py-4">
                                  <div className="flex items-center space-x-1.5">
                                    {student.assigned_mentor_id ? (
                                      <span className="px-2 py-0.5 bg-amber-50 text-amber-700 rounded font-semibold text-[10px]">
                                        {mentorsList.find(m => m.id === student.assigned_mentor_id)?.name || 'Assigned Mentor'}
                                      </span>
                                    ) : (
                                      <span className="text-slate-300 text-[10px]">Unassigned</span>
                                    )}
                                    {(currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') && (
                                      <button 
                                        onClick={() => openAssignModal(student, 'assign_mentor')}
                                        className="text-slate-400 hover:text-brand-600 transition-colors"
                                        title="Change Mentor Assignment"
                                      >
                                        <Icons.Assign />
                                      </button>
                                    )}
                                  </div>
                                </td>
                                <td className="px-6 py-4 text-right">
                                  <div className="inline-flex items-center space-x-2">
                                    {/* Edit Button */}
                                    <button
                                      onClick={() => openEditModal(student)}
                                      className="p-1 border border-slate-200 hover:border-brand-500 rounded text-slate-500 hover:text-brand-600 hover:bg-slate-50 transition-all"
                                      title="Edit Student"
                                    >
                                      <Icons.Edit />
                                    </button>

                                    {/* Soft Delete Button */}
                                    {(currentUser.role === 'SUPER_ADMIN' || currentUser.role === 'ADMIN') && !student.is_deleted && (
                                      <button
                                        onClick={() => handleDeleteStudent(student.id)}
                                        className="p-1 border border-slate-200 hover:border-rose-500 rounded text-slate-500 hover:text-rose-600 hover:bg-slate-50 transition-all"
                                        title="Soft Delete Student"
                                      >
                                        <Icons.Delete />
                                      </button>
                                    )}

                                    {student.is_deleted && (
                                      <span className="px-2 py-0.5 bg-rose-50 text-rose-600 rounded font-bold text-[10px] uppercase">
                                        Soft Deleted
                                      </span>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination Bar */}
                    <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-xs text-slate-500 font-medium">
                        Showing <span className="font-semibold text-slate-700">{studentOffset + 1}</span> to{' '}
                        <span className="font-semibold text-slate-700">
                          {Math.min(studentOffset + studentLimit, studentsCount)}
                        </span>{' '}
                        of <span className="font-semibold text-slate-700">{studentsCount}</span> entries
                      </span>

                      <div className="inline-flex space-x-2">
                        <button
                          disabled={studentOffset === 0}
                          onClick={() => setStudentOffset(Math.max(0, studentOffset - studentLimit))}
                          className="px-3 py-1 border border-slate-200 hover:border-slate-300 disabled:opacity-50 text-xs font-semibold text-slate-600 rounded-lg transition-colors bg-white"
                        >
                          Prev
                        </button>
                        <button
                          disabled={studentOffset + studentLimit >= studentsCount}
                          onClick={() => setStudentOffset(studentOffset + studentLimit)}
                          className="px-3 py-1 border border-slate-200 hover:border-slate-300 disabled:opacity-50 text-xs font-semibold text-slate-600 rounded-lg transition-colors bg-white"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* View Users Accounts List */}
              {activeTab === 'users' && (
                <div className="space-y-6 animate-fadeIn">
                  <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-50/75 border-b border-slate-200 text-slate-400 text-[10px] font-bold uppercase tracking-wider">
                            <th className="px-6 py-4">User</th>
                            <th className="px-6 py-4">Role</th>
                            <th className="px-6 py-4">Email Verification</th>
                            <th className="px-6 py-4">Is Active</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 text-xs">
                          {usersList.map((user) => (
                            <tr key={user.id} className="hover:bg-slate-50/50 transition-colors">
                              <td className="px-6 py-4 flex items-center space-x-3">
                                <div className="h-9 w-9 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700 uppercase">
                                  {user.name ? user.name.charAt(0) : 'U'}
                                </div>
                                <div>
                                  <span className="font-semibold text-slate-800 block text-sm">
                                    {user.name || 'No Name'}
                                  </span>
                                  <span className="text-[10px] text-slate-400 block">{user.email}</span>
                                </div>
                              </td>
                              <td className="px-6 py-4">
                                <span className="px-2.5 py-0.5 bg-slate-100 text-slate-700 rounded font-bold text-[10px] uppercase">
                                  {user.role}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                                  user.is_first_login ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'
                                }`}>
                                  {user.is_first_login ? 'First Login Required' : 'Completed'}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <button
                                  onClick={() => handleToggleUserActivation(user)}
                                  className={`px-3 py-1 rounded-full text-[10px] font-bold transition-all ${
                                    user.is_active ? 'bg-emerald-50 border border-emerald-100 text-emerald-700' : 'bg-rose-50 border border-rose-100 text-rose-700'
                                  }`}
                                >
                                  {user.is_active ? 'Active' : 'Suspended'}
                                </button>
                              </td>
                              <td className="px-6 py-4 text-right">
                                <button
                                  onClick={() => handleResetPassword(user)}
                                  className="px-3 py-1 border border-slate-200 hover:border-slate-350 hover:bg-slate-50 rounded text-slate-600 font-semibold text-[10px] flex items-center ml-auto"
                                >
                                  <Icons.Key />
                                  <span>Reset Pass</span>
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* View Permissions Matrix */}
              {activeTab === 'permissions' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fadeIn">
                  {/* System Roles */}
                  <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6">
                    <h3 className="text-base font-extrabold text-slate-800 mb-4 tracking-tight">System Roles</h3>
                    <div className="space-y-4">
                      {roles.map((role) => (
                        <div key={role.id} className="p-4 border border-slate-100 rounded-lg hover:shadow-xs transition-shadow">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-bold text-slate-800 uppercase">{role.name}</span>
                            <span className="text-[10px] text-slate-400 font-medium">Role ID: {role.id}</span>
                          </div>
                          <p className="text-xs text-slate-500 mt-2 font-medium">
                            {role.name === 'SUPER_ADMIN' ? 'Full operational root permission capability' : 
                             role.name === 'ADMIN' ? 'Coordinate assigned student records and mentors' :
                             role.name === 'MENTOR' ? 'View and update progress of assigned student registry' :
                             'Personal scoped profile reading capability.'}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Registered Permissions */}
                  <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 h-fit">
                    <h3 className="text-base font-extrabold text-slate-800 mb-4 tracking-tight">Registered Scope Permissions</h3>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      {permissions.map((p) => (
                        <div key={p.id} className="p-3 bg-slate-55 border border-slate-100 rounded-lg flex flex-col justify-between">
                          <span className="font-semibold text-slate-700">{p.name}</span>
                          <span className="text-[9px] text-slate-400 mt-1 uppercase font-bold">Code Permission</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </main>
        </div>
      )}

      {/* Form Dialog Modals */}
      {modalType && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-6">
          <div className="bg-white max-w-md w-full rounded-2xl shadow-2xl border border-slate-100 overflow-hidden flex flex-col max-h-[90vh]">
            <header className="px-6 py-4 border-b border-slate-200 flex items-center justify-between shrink-0">
              <h3 className="text-lg font-extrabold text-slate-800">
                {modalType === 'create_student' ? 'Register New Student' : 
                 modalType === 'edit_student' ? 'Update Student Profile' :
                 modalType === 'assign_admin' ? 'Assign Admin Coordinator' :
                 'Assign Mentor'}
              </h3>
              <button
                onClick={() => setModalType(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </header>

            <div className="p-6 overflow-y-auto flex-grow">
              {(modalType === 'create_student' || modalType === 'edit_student') && (
                <form 
                  onSubmit={modalType === 'create_student' ? handleCreateStudent : handleEditStudent} 
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Full Name</label>
                    <input
                      type="text"
                      required
                      className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      value={studentForm.name}
                      onChange={(e) => setStudentForm({ ...studentForm, name: e.target.value })}
                    />
                  </div>

                  {modalType === 'create_student' && (
                    <div>
                      <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Email Address</label>
                      <input
                        type="email"
                        required
                        className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                        value={studentForm.email}
                        onChange={(e) => setStudentForm({ ...studentForm, email: e.target.value })}
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Nickname</label>
                    <input
                      type="text"
                      className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      value={studentForm.nickname}
                      onChange={(e) => setStudentForm({ ...studentForm, nickname: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Position / Title</label>
                    <input
                      type="text"
                      className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      value={studentForm.position}
                      onChange={(e) => setStudentForm({ ...studentForm, position: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Contact Number</label>
                    <input
                      type="text"
                      className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      value={studentForm.contact}
                      onChange={(e) => setStudentForm({ ...studentForm, contact: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Date of Birth</label>
                    <input
                      type="date"
                      className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      value={studentForm.dob}
                      onChange={(e) => setStudentForm({ ...studentForm, dob: e.target.value })}
                    />
                  </div>

                  {modalType === 'create_student' && (
                    <div>
                      <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Custom Password (Optional)</label>
                      <input
                        type="password"
                        placeholder="Leave blank for standard password"
                        className="w-full px-3 py-1.5 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none placeholder:text-slate-300"
                        value={studentForm.password}
                        onChange={(e) => setStudentForm({ ...studentForm, password: e.target.value })}
                      />
                    </div>
                  )}

                  <footer className="pt-4 flex items-center justify-end space-x-2 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setModalType(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold"
                    >
                      {modalType === 'create_student' ? 'Register Student' : 'Save Changes'}
                    </button>
                  </footer>
                </form>
              )}

              {modalType === 'assign_admin' && (
                <form onSubmit={handleAssignAdmin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Choose Admin Coordinator</label>
                    <select
                      required
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      value={assignForm.targetId}
                      onChange={(e) => setAssignForm({ targetId: e.target.value })}
                    >
                      <option value="">Select Admin Account...</option>
                      {adminsList.map(admin => (
                        <option key={admin.id} value={admin.id}>{admin.name} ({admin.email})</option>
                      ))}
                    </select>
                  </div>

                  <footer className="pt-4 flex items-center justify-end space-x-2 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setModalType(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold"
                    >
                      Confirm Assignment
                    </button>
                  </footer>
                </form>
              )}

              {modalType === 'assign_mentor' && (
                <form onSubmit={handleAssignMentor} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">Choose Mentor</label>
                    <select
                      required
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      value={assignForm.targetId}
                      onChange={(e) => setAssignForm({ targetId: e.target.value })}
                    >
                      <option value="">Select Mentor Account...</option>
                      {mentorsList.map(mentor => (
                        <option key={mentor.id} value={mentor.id}>{mentor.name} ({mentor.email})</option>
                      ))}
                    </select>
                  </div>

                  <footer className="pt-4 flex items-center justify-end space-x-2 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setModalType(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold"
                    >
                      Confirm Assignment
                    </button>
                  </footer>
                </form>
              )}

              {(modalType === 'late_check_in' || modalType === 'late_check_out') && (
                <form 
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (modalType === 'late_check_in') {
                      handleCheckIn(attendanceReason);
                    } else {
                      handleCheckOut(attendanceReason);
                    }
                  }} 
                  className="space-y-4"
                >
                  <div>
                    <span className="text-rose-600 font-bold block mb-2 text-xs">
                      {modalType === 'late_check_in' ? 'Check-in deadline has passed!' : 'Check-out deadline has not been reached!'}
                    </span>
                    <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">
                      Reason for Late Attendance / Early Departure
                    </label>
                    <textarea
                      required
                      placeholder="Write your explanation or request reason here..."
                      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 focus:outline-none"
                      rows="3"
                      value={attendanceReason}
                      onChange={(e) => setAttendanceReason(e.target.value)}
                    />
                  </div>

                  <footer className="pt-4 flex items-center justify-end space-x-2 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setModalType(null)}
                      className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold"
                    >
                      Submit Request
                    </button>
                  </footer>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
