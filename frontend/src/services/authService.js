// frontend/src/services/authService.js
import axios from 'axios';
import apiClient from './apiClient'; 



const authService = {
  login(credentials) {
    return apiClient.post('/auth/login', credentials);
  },
  register(userInfo) {
     return apiClient.post('/auth/register', userInfo);
  },
  forgotPassword(email) {
      return apiClient.post('/auth/forgot-password', { email });
  }
};


export default authService;

