import React, { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext(null);

let toastId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const success = useCallback((msg) => addToast(msg, 'success'), [addToast]);
  const error = useCallback((msg) => addToast(msg, 'error'), [addToast]);
  const info = useCallback((msg) => addToast(msg, 'info'), [addToast]);
  const warning = useCallback((msg) => addToast(msg, 'warning'), [addToast]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ success, error, info, warning }}>
      {children}

      {/* Toast container */}
      <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-3 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`
              pointer-events-auto animate-slide-down max-w-sm w-full
              px-5 py-3.5 rounded-xl shadow-2xl border backdrop-blur-md
              flex items-start gap-3 cursor-pointer transition-all duration-300
              hover:scale-[1.02]
              ${toast.type === 'success'
                ? 'bg-emerald-50/90 border-emerald-200 text-emerald-800'
                : toast.type === 'error'
                ? 'bg-rose-50/90 border-rose-200 text-rose-800'
                : toast.type === 'warning'
                ? 'bg-amber-50/90 border-amber-200 text-amber-800'
                : 'bg-sky-50/90 border-sky-200 text-sky-800'
              }
            `}
            onClick={() => removeToast(toast.id)}
          >
            {/* Icon */}
            <span className="text-lg flex-shrink-0 mt-0.5">
              {toast.type === 'success' && '✓'}
              {toast.type === 'error' && '✕'}
              {toast.type === 'warning' && '⚠'}
              {toast.type === 'info' && 'ℹ'}
            </span>
            <p className="text-sm font-medium leading-snug">{toast.message}</p>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
