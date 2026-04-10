import { expect, test } from '@playwright/test';

test('core flow: login -> stream chat -> render markdown', async ({ page }) => {
  await page.route('**/api/java/api/v1/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access_token: 'mock-token',
        token_type: 'Bearer',
        expires_in: 7200
      })
    });
  });

  await page.route('**/api/java/api/v1/chat/stream', async (route) => {
    const ssePayload = [
      'event: token',
      'data: {"text":"你好，"}',
      '',
      'event: token',
      'data: {"text":"这是企业级SSE流式返回。"}',
      '',
      'event: done',
      'data: {"session_id":"s001","answer":"你好，这是企业级SSE流式返回。","trace":[],"retrieval_preview":[]}',
      ''
    ].join('\n');

    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      body: ssePayload
    });
  });

  await page.goto('/');
  await page.getByRole('button', { name: '登录获取 JWT' }).click();

  await page.getByPlaceholder('输入问题，例如：请帮我看下下周课程并生成学习周报').fill('请输出本周学习建议');
  await page.getByRole('button', { name: '发送（SSE）' }).click();

  await expect(page.getByText('你好，这是企业级SSE流式返回。')).toBeVisible();
});
