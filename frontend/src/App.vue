<template>
  <div>
    <Navbar />
    <main class="container mt-4">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
     </div>
</template>

<script setup>
import Navbar from '@/components/shared/Navbar.vue';
import { useAuthStore } from '@/store/auth';
import { onMounted } from 'vue';

// Check authentication status when the app loads
const auth = useAuthStore();
onMounted(() => {
  auth.checkAuth();
});

</script>

<style>
/* Global styles or import Bootstrap/custom CSS */
@import '@/assets/styles/styles.css'; /* Example if you have base styles */

/* Basic fade transition for routes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Import styles from old styles.css as needed, scoped or globally */
/* e.g. body gradient background */
body {
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
    background: linear-gradient(to bottom right, #d4e4ff, #9ab7f0);
    min-height: 100vh;
    color: #333;
}

/* Make flash messages work if implemented */
.flash-message-container {
   position: fixed; /* Or relative/absolute depending on layout */
   top: 60px; /* Below navbar */
   left: 50%;
   transform: translateX(-50%);
   z-index: 1060; /* Above most content */
   width: auto; /* Adjust as needed */
   max-width: 90%;
}
</style>