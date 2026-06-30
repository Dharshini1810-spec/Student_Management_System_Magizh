import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

function DayHeader() {
  const now = new Date();
  const dayName = DAY_NAMES[now.getDay()];
  const monthName = MONTH_NAMES[now.getMonth()];
  const date = now.getDate();
  const year = now.getFullYear();
  const formatted = `${dayName}, ${monthName} ${date}, ${year}`;

  return (
    <div className="flex items-center gap-3 px-6 lg:px-8 py-4 border-b border-white/20 bg-gradient-to-r from-brand-600/90 via-purple-600/90 to-pink-600/90 backdrop-blur-md shadow-lg">
      <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm text-white shadow-inner">
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <div>
        <p className="text-xs font-medium text-white/70 uppercase tracking-wider">Today</p>
        <p className="text-sm font-bold text-white">{formatted}</p>
      </div>
    </div>
  );
}

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Sidebar />
      <main className="flex-1 overflow-x-hidden flex flex-col">
        <DayHeader />
        <div className="flex-1 max-w-7xl mx-auto w-full px-6 lg:px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
