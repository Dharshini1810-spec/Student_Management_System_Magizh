import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authApi from '../api/authApi';
import { setLogoutHandler } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [mustChangePassword, setMustChangePassword] = useState(false);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setMustChangePassword(false);
  }, []);

  // Register the logout handler so 401 interceptor can trigger it
  useEffect(() => {
    setLogoutHandler(logout);
    return () => setLogoutHandler(null);
  }, [logout]);

  // On mount (or when token changes), try to rehydrate the session
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    authApi
      .getMe()
      .then((res) => {
        setUser(res.data);
      })
      .catch(() => {
        // Token is invalid/expired
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [token]);

  const login = async (email, password) => {
    const res = await authApi.login(email, password);
    const { access_token, user: userData, must_change_password } = res.data;

    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);

    if (must_change_password) {
      setMustChangePassword(true);
    }

    return { user: userData, must_change_password };
  };

  const clearMustChangePassword = () => {
    setMustChangePassword(false);
  };

  const value = {
    user,
    token,
    loading,
    mustChangePassword,
    isAuthenticated: !!user && !!token,
    isSuperAdmin: user?.role === 'SUPER_ADMIN',
    isAdmin: user?.role === 'ADMIN' || user?.role === 'SUPER_ADMIN',
    login,
    logout,
    clearMustChangePassword,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
