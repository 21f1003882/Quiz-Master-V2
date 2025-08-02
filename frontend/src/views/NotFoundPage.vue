<template>
    <div class="text-center mt-5">
      <h1>404 - Page Not Found</h1>
      <p>Sorry, the page you were looking for does not exist.</p>
      <router-link :to="{ name: 'Home' }" class="btn btn-primary">Go Home</router-link>
    </div>
  </template>
  
  <script setup>
  // No script needed for simple 404
  </script>