import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically inject bearer tokens
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to parse response bodies and handle token expiry
client.interceptors.response.use(
  (response) => {
    // Unwraps the standard success response envelope {status, message, data}
    return response.data;
  },
  (error) => {
    const response = error.response;
    
    // Format error fields using the standard backend envelope
    const formattedError = {
      message: response?.data?.error?.message || error.message || 'An error occurred',
      code: response?.data?.error?.code || 'NETWORK_ERROR',
      status: response?.status || 500,
      details: response?.data?.error?.details || null,
    };
    
    // If a request returns 401 (Unauthorized), purge the stale token
    if (response?.status === 401) {
      localStorage.removeItem('token');
    }
    
    return Promise.reject(formattedError);
  }
);

export default client;
