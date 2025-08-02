// frontend/vite.config.js
import { fileURLToPath, URL } from 'node:url' // Use node:url for modern path resolution
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import path from 'path' // No longer needed if using URL

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
   
  },

  server: {
    port: 5173,
    proxy: {
      
      '/api': {
      
        target: 'http://127.0.0.1:5000', 
        changeOrigin: true, 
        secure: false,      
      }
    }
  }
 
})
