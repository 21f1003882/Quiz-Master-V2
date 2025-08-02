<template>
    <div>
      <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
      <form @submit.prevent="handleLogin">
        <div class="form-group mb-3">
          <div class="input-group">
            <span class="input-group-text">🙂</span>
            <input type="text" class="form-control" placeholder="Username or Email" v-model="username" required>
          </div>
        </div>
        <div class="form-group mb-3">
          <div class="input-group">
            <span class="input-group-text">🔑</span>
            <input type="password" class="form-control" placeholder="Password" v-model="password" required>
          </div>
        </div>
        <div class="text-end mb-3">
          <a href="#" data-bs-toggle="modal" data-bs-target="#forgotPasswordModal">Forgot Password?</a>
        </div>
        <div class="pb-2">
          <button type="submit" class="btn btn-dark w-100" :disabled="loading">{{ loading ? 'Logging in...' : 'Login' }}</button>
        </div>
      </form>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useAuthStore } from '@/store/auth';
  
  const auth = useAuthStore();
  
  const username = ref('');
  const password = ref('');
  const loading = ref(false);
  const errorMessage = ref('');
  
  const handleLogin = async () => {
    loading.value = true;
    errorMessage.value = '';
    try {
      await auth.login({ username: username.value, password: password.value });
      // The auth store will handle the redirect on success
    } catch (error) {
      errorMessage.value = error.response?.data?.message || 'Login failed.';
    } finally {
      loading.value = false;
    }
  };
  </script>
  