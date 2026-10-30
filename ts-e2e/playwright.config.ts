import { defineConfig } from '@playwright/test';

const PORT = 8766;

export default defineConfig({
  testDir: './tests',
  reporter: [['list'], ['html', { open: 'never', outputFolder: '../reports/playwright-ts' }]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    extraHTTPHeaders: { 'X-API-Key': 'demo-key' },
    trace: 'retain-on-failure',
  },
  webServer: {
    command: `"${process.env.PYTHON ?? 'python'}" -m uvicorn app.main:app --port ${PORT}`,
    cwd: '..',
    url: `http://127.0.0.1:${PORT}/health`,
    reuseExistingServer: !process.env.CI,
  },
});
