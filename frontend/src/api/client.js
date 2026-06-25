import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let logoutHandler = null;

/**
 * Register a callback that will be invoked when a 401 is received,
 * allowing the AuthContext to clear its state.
 */
export function setLogoutHandler(handler) {
  logoutHandler = handler;
}

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor – inject bearer token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor – unwrap envelope & handle 401
client.interceptors.response.use(
  (response) => {
    // Unwrap the standard success response envelope {status, message, data}
    return response.data;
  },
  (error) => {
    const response = error.response;

    const formattedError = {
      message: response?.data?.error?.message || response?.data?.message || error.message || 'An error occurred',
      code: response?.data?.error?.code || 'NETWORK_ERROR',
      status: response?.status || 500,
      details: response?.data?.error?.details || null,
    };

    // On 401, purge stale token and invoke logout handler
    if (response?.status === 401) {
      localStorage.removeItem('token');
      if (logoutHandler) {
        logoutHandler();
      }
    }

    return Promise.reject(formattedError);
  }
);

export default client;
