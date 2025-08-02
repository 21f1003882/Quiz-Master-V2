import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';
import router from '@/router';
import apiClient from '@/services/apiClient';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('authToken') || null,
    user: JSON.parse(localStorage.getItem('authUser')) || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isAdmin: (state) => state.user?.roles?.includes('admin') || false,
    username: (state) => state.user?.username || '',
  },

  actions: {
    setTokenAndRedirect(token) {
      if (!token) {
        console.error("setTokenAndRedirect called with no token.");
        return;
      }
      const decoded = jwtDecode(token);
      this.accessToken = token;
      this.user = {
        username: decoded.username,
        roles: decoded.roles
      };
      localStorage.setItem('authToken', token);
      localStorage.setItem('authUser', JSON.stringify(this.user));
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      router.push(this.isAdmin ? { name: 'AdminDashboard' } : { name: 'UserDashboard' });
    },

    async login(credentials) {
      const response = await apiClient.post('/auth/login', credentials);
      const token = response.data.access_token;
      this.setTokenAndRedirect(token);
    },

    async register(regInfo) {
      const response = await apiClient.post('/auth/register', regInfo);
      return response.data;
    },

    logout() {
      this.accessToken = null;
      this.user = null;
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
      delete apiClient.defaults.headers.common['Authorization'];
      router.push({ name: 'Login' });
    },

    checkAuth() {
      const token = localStorage.getItem('authToken');
      if (token) {
        this.accessToken = token;
        this.user = JSON.parse(localStorage.getItem('authUser'));
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }
    },

    async getSecretQuestion(email) {
      const response = await apiClient.post('/auth/forgot-password/get-question', { email });
      return response.data;
    },

    async resetPassword(resetData) {
      const response = await apiClient.post('/auth/forgot-password/reset', resetData);
      return response.data;
    }
    
  },
});

