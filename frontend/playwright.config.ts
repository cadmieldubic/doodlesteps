import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

const projectRoot = fileURLToPath(new URL('..', import.meta.url));
process.env.PLAYWRIGHT_BROWSERS_PATH ??= join(projectRoot, 'work', 'playwright');

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: { timeout: 8_000 },
  fullyParallel: false,
  workers: 1,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  outputDir: join(projectRoot, 'work', 'playwright-results'),
  reporter: [
    ['list'],
    ['html', { outputFolder: join(projectRoot, 'work', 'playwright-report'), open: 'never' }],
  ],
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    reducedMotion: 'reduce',
  },
  projects: [
    { name: 'desktop-chromium', use: { viewport: { width: 1280, height: 900 } } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 5'], deviceScaleFactor: 1 } },
  ],
  webServer: [
    {
      command: 'backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000',
      cwd: projectRoot,
      url: 'http://127.0.0.1:8000/api/health',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
      env: { OPENAI_API_KEY: '' },
    },
    {
      command: 'pnpm dev --port 5173 --strictPort',
      cwd: join(projectRoot, 'frontend'),
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
  ],
});
