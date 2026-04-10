import type { ChatRequest, ChatResponse, LoginResponse } from '../types';

const JSON_HEADERS = {
  'Content-Type': 'application/json'
};

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch('/api/java/api/v1/auth/login', {
    method: 'POST',
    headers: JSON_HEADERS,
    body: JSON.stringify({ username, password })
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  return response.json() as Promise<LoginResponse>;
}

export async function chat(request: ChatRequest, token: string): Promise<ChatResponse> {
  const response = await fetch('/api/java/api/v1/chat', {
    method: 'POST',
    headers: {
      ...JSON_HEADERS,
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    throw new Error(`Chat failed with status ${response.status}`);
  }

  return response.json() as Promise<ChatResponse>;
}

interface StreamHandlers {
  onToken: (token: string) => void;
  onTrace: (raw: string) => void;
  onDone: (payload: ChatResponse) => void;
}

export async function streamChat(request: ChatRequest, token: string, handlers: StreamHandlers): Promise<void> {
  const response = await fetch('/api/java/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      ...JSON_HEADERS,
      Accept: 'text/event-stream',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok || !response.body) {
    throw new Error(`SSE failed with status ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() ?? '';

    for (const eventChunk of events) {
      const lines = eventChunk.split('\n');
      let eventName = 'message';
      let eventData = '';

      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventName = line.slice(6).trim();
        }
        if (line.startsWith('data:')) {
          eventData += line.slice(5).trim();
        }
      }

      if (eventName === 'token') {
        try {
          const payload = JSON.parse(eventData) as { text: string };
          handlers.onToken(payload.text);
        } catch {
          handlers.onToken(eventData);
        }
      }

      if (eventName === 'trace') {
        handlers.onTrace(eventData);
      }

      if (eventName === 'done') {
        const payload = JSON.parse(eventData) as ChatResponse;
        handlers.onDone(payload);
      }
    }
  }
}
