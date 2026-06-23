import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, Outlet } from 'react-router-dom';
import client from './api/client';

// Layout Component
function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header / Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold text-lg shadow-sm shadow-brand-500/50">
                M
              </div>
              <span className="font-semibold text-lg text-slate-800 tracking-tight">
                SMS Magizh
              </span>
            </div>
            
            <nav className="flex space-x-8">
              <Link 
                to="/" 
                className="text-slate-600 hover:text-brand-600 transition-colors text-sm font-medium"
              >
                Dashboard
              </Link>
              <a 
                href="/api/v1/docs" 
                target="_blank" 
                rel="noreferrer" 
                className="text-slate-600 hover:text-brand-600 transition-colors text-sm font-medium"
              >
                API Documentation
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400">
          &copy; {new Date().getFullYear()} Student Management System - Foundation Setup. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

// Home Component
function Home() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Queries the backend /health endpoint on mount
    client.get('/health')
      .then((res) => {
        setHealth(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-brand-800 to-brand-600 rounded-2xl p-8 md:p-12 text-white shadow-lg shadow-brand-900/10">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">
          Student Management System Foundation
        </h1>
        <p className="mt-3 text-brand-100 max-w-2xl text-base md:text-lg">
          The foundation project architecture is ready. The environment config, DB connections, ORM mapper, routing, and HTTP helpers are configured.
        </p>
      </div>

      {/* Grid status cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* API Health Check Card */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-800">Backend Connectivity</h2>
            <p className="text-slate-500 text-sm mt-1">Status check of the FastAPI and PostgreSQL backend services.</p>
          </div>
          
          <div className="mt-6">
            {loading ? (
              <div className="flex items-center space-x-2 text-slate-400">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-brand-500 border-t-transparent"></div>
                <span className="text-sm font-medium">Checking services...</span>
              </div>
            ) : error ? (
              <div className="flex items-center space-x-2 text-rose-500 bg-rose-50 border border-rose-100 p-3 rounded-lg">
                <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse"></span>
                <span className="text-sm font-semibold">Backend Unreachable ({error.code})</span>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-emerald-600 bg-emerald-50 border border-emerald-100 p-3 rounded-lg">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-sm font-semibold text-emerald-800">
                    System healthy
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs font-semibold text-slate-600 bg-slate-50 p-3 rounded-lg">
                  <div>API Server: <span className="text-emerald-600 font-bold uppercase">{health?.services?.api}</span></div>
                  <div>Database: <span className="text-emerald-600 font-bold uppercase">{health?.services?.database}</span></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Tech Stack Info */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800">Technology Stack</h2>
          <p className="text-slate-500 text-sm mt-1">Foundation components initialized in the codebase.</p>
          
          <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <span className="font-semibold text-slate-400 block mb-1">Backend</span>
              <span className="text-slate-800 font-medium">FastAPI & Uvicorn</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <span className="font-semibold text-slate-400 block mb-1">Database ORM</span>
              <span className="text-slate-800 font-medium">SQLAlchemy (2.0)</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <span className="font-semibold text-slate-400 block mb-1">Migrations</span>
              <span className="text-slate-800 font-medium">Alembic Versioning</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <span className="font-semibold text-slate-400 block mb-1">Security</span>
              <span className="text-slate-800 font-medium">JWT Ready Payload</span>
            </div>
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100 col-span-2">
              <span className="font-semibold text-slate-400 block mb-1">Frontend Setup</span>
              <span className="text-slate-800 font-medium">React, Vite, Tailwind CSS, Axios, React Router</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// NotFound Component
function NotFound() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center text-center">
      <h2 className="text-6xl font-black text-slate-300">404</h2>
      <p className="text-xl font-bold text-slate-700 mt-4">Page Not Found</p>
      <p className="text-slate-400 text-sm mt-2 max-w-sm">
        The requested page does not exist or has been removed.
      </p>
      <Link 
        to="/" 
        className="mt-6 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold transition-colors shadow-md shadow-brand-500/20"
      >
        Go back home
      </Link>
    </div>
  );
}

// App Routing Configuration
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
