import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import AppLayout from './components/AppLayout';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import CreateUserPage from './pages/CreateUserPage';
import UserDetailPage from './pages/UserDetailPage';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';

import ChangePasswordPage from './pages/ChangePasswordPage';
import NotificationsPage from './pages/NotificationsPage';
import DailyContentPage from './pages/DailyContentPage';
import StudentNotesPage from './pages/StudentNotesPage';
import ReportsPage from './pages/ReportsPage';
import ActivityPage from './pages/ActivityPage';
import TodosPage from './pages/TodosPage';
import ProjectsPage from './pages/ProjectsPage';
import AttendancePage from './pages/AttendancePage';
import ReferralLinksPage from './pages/ReferralLinksPage';

function NotFound() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center text-center px-4">
      <h2 className="text-6xl font-black text-white/20">404</h2>
      <p className="text-xl font-bold text-white/80 mt-4">Page Not Found</p>
      <p className="text-white/40 text-sm mt-2 max-w-sm">
        The page you are looking for does not exist or has been moved.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex px-4 py-2 bg-gradient-to-r from-brand-600 to-purple-600 hover:from-brand-700 hover:to-purple-700 text-white rounded-lg text-sm font-semibold transition-all shadow-lg shadow-brand-500/20"
      >
        Go back home
      </Link>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="users" element={<ProtectedRoute requiredRole={['SUPER_ADMIN', 'ADMIN']}><UsersPage /></ProtectedRoute>} />
              <Route path="users/new" element={<ProtectedRoute requiredRole="SUPER_ADMIN"><CreateUserPage /></ProtectedRoute>} />
              <Route path="users/:id" element={<UserDetailPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="notifications" element={<NotificationsPage />} />
              <Route path="daily-content" element={<DailyContentPage />} />
              <Route path="students/:studentId/notes" element={<StudentNotesPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="activity" element={<ActivityPage />} />
              <Route path="todos" element={<TodosPage />} />
              <Route path="projects" element={<ProjectsPage />} />
              <Route path="attendance" element={<AttendancePage />} />
              <Route path="referral-links" element={<ReferralLinksPage />} />
            </Route>

            <Route
              path="/change-password"
              element={
                <ProtectedRoute>
                  <ChangePasswordPage />
                </ProtectedRoute>
              }
            />
            <Route path="/login" element={<LoginPage />} />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
