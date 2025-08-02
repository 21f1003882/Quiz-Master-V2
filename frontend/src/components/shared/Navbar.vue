<template>
    <nav class="navbar navbar-expand-lg navbar-dark mb-4 shadow-sm">
      <div class="container-fluid">
        <router-link class="navbar-brand" :to="{ name: 'Home' }">
            Quiz App
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavContent" aria-controls="navbarNavContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNavContent">
          <ul class="navbar-nav ms-auto">
            <template v-if="auth.isAuthenticated">
              <template v-if="auth.isAdmin">
                <li class="nav-item">
                    <router-link class="nav-link" :to="{ name: 'AdminDashboard' }" active-class="active">Admin Dashboard</router-link>
                </li>
                <li class="nav-item">
                    <router-link class="nav-link" :to="{ name: 'AdminSearch' }" active-class="active">Search</router-link> 
                </li>
                <li class="nav-item">
                    <router-link class="nav-link" :to="{ name: 'AdminSummary' }" active-class="active">Summary</router-link> 
                </li>
                <li class="nav-item">
                    <router-link class="nav-link" :to="{ name: 'AdminAllQuizzes' }" active-class="active">All Quizzes</router-link> 
                </li>
              </template>
              <template v-else>
                <li class="nav-item">
                    <router-link class="nav-link" :to="{ name: 'UserDashboard' }" active-class="active">Dashboard</router-link>
                </li>
                <li class="nav-item">
                    <router-link class="nav-link" :to="{ name: 'UserSummary' }" active-class="active">My Summary</router-link> 
                </li>
              </template>
              <li class="nav-item">
                  <a class="nav-link" href="#" @click.prevent="handleLogout">Logout ({{ auth.username }})</a>
              </li>
            </template>
            <template v-else>
              <li class="nav-item">
                  <router-link class="nav-link" :to="{ name: 'Login' }" active-class="active">Login</router-link>
              </li>
               </template>
          </ul>
        </div>
      </div>
    </nav>
  </template>
  
  <script setup>
  import { useAuthStore } from '@/store/auth';
  import { useRouter } from 'vue-router';
  
  const auth = useAuthStore();
  const router = useRouter();
  
  const handleLogout = () => {
    auth.logout();
    // Pinia store logout action already redirects to Login if needed
    
    router.push({ name: 'Login' });
  };
  </script>
  
  <style scoped>
  /* Add navbar CSS from styles.css here or import globally */
  .navbar {
      background: linear-gradient(135deg, #0b0710 0%, #09101d 100%);
  }
  .navbar .navbar-brand { color: #ced4da; font-weight: 500; }
  .navbar .navbar-brand:hover, .navbar .navbar-brand:focus { color: #f8f9fa; }
  .navbar .navbar-nav .nav-link { color: #adb5bd; }
  .navbar .navbar-nav .nav-link:hover, .navbar .navbar-nav .nav-link:focus { color: #dee2e6; }
  .navbar .navbar-nav .nav-link.active { color: #ffffff !important; font-weight: 500; }
  /* Ensure toggler icon is visible on dark background (navbar-dark helps) */
  </style>