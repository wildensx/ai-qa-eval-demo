import { test, expect } from '@playwright/test';

test('answer cites its source and keeps the documented shape', async ({ request }) => {
  const response = await request.post('/ask', { data: { question: 'When does online check-in open?' } });
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(Object.keys(body).sort()).toEqual(['abstained', 'answer', 'citations', 'flags']);
  expect(body.citations).toEqual(['checkin']);
  expect(body.answer).toContain('36 hours');
});

test('requests without a valid key are rejected', async ({ request }) => {
  const response = await request.post('/ask', {
    data: { question: 'When does online check-in open?' },
    headers: { 'X-API-Key': 'wrong' },
  });
  expect(response.status()).toBe(401);
});

for (const question of ['', 'hi', 'x'.repeat(501)]) {
  test(`invalid question is rejected (length ${question.length})`, async ({ request }) => {
    const response = await request.post('/ask', { data: { question } });
    expect(response.status()).toBe(422);
  });
}
