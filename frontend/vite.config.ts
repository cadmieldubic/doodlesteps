import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1', port: 5173, strictPort: true,
    proxy: { '/api': 'http://127.0.0.1:8000' },
    // Polling also detects edits when local sandbox filesystem events are unavailable.
    watch: { usePolling: true, interval: 500 },
  },
  test: {
    environment: 'jsdom', setupFiles: ['./src/test/setup.ts'], include: ['src/**/*.test.{ts,tsx}'], css: true,
    // Worker threads also run inside restricted local environments that cannot fork test processes.
    pool: 'threads', maxWorkers: 1, fileParallelism: false,
  },
});
