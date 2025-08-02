// frontend/src/services/apiClient.js
import axios from 'axios';

// Create the Axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error("Axios Request Interceptor Error:", error);
    return Promise.reject(error);
  }
);


apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Received 401 Unauthorized. Logging out and redirecting.");
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
      
      if (window.location.pathname !== '/login') {
           window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);


export default apiClient;
