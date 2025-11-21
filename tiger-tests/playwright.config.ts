import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv'; dotenv.config({ path: '.env.test' });

export default defineConfig({
  timeout: 30000,
  retries: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.APP_URL,
    trace: 'on-first-retry',
    video: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: devices['Desktop Chrome'] }],
});