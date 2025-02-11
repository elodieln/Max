import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configuration du Vite
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/generate-pdf': 'http://localhost:5000', // Proxy vers ton backend Express
    }
  }
});
