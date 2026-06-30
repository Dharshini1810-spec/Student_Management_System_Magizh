import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Wraps routes that require authentication.
 * - If not authenticated → redirects to /login
 * - If authenticated but must_change_password → redirects to /change-password
 * - If requiredRole is set, checks user role (Super Admin always passes)
 */
export default function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, loading, user, mustChangePassword } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4 animate-fade-in">
          <div className="w-10 h-10 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
          <p className="text-sm text-slate-500 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Force password change on first login
  if (mustChangePassword && location.pathname !== '/change-password') {
    return <Navigate to="/change-password" replace />;
  }

  // Role check
  if (requiredRole) {
    const userRole = user?.role;
    const allowed =
      userRole === 'SUPER_ADMIN' ||
      (Array.isArray(requiredRole)
        ? requiredRole.includes(userRole)
        : userRole === requiredRole);

    if (!allowed) {
      return <Navigate to="/" replace />;
    }
  }

  return children;
}
