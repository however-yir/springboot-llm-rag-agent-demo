import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: Number(__ENV.VUS || 20),
  duration: __ENV.DURATION || '30s',
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05']
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost/api/java';
const JWT_TOKEN = __ENV.JWT_TOKEN || '';

export default function () {
  const payload = JSON.stringify({
    user_id: 'k6-user',
    session_id: `k6-session-${__VU}`,
    message: '请给出学习周报建议',
    department: 'cs'
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${JWT_TOKEN}`
    }
  };

  const res = http.post(`${BASE_URL}/api/v1/chat`, payload, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'contains answer': (r) => r.body && r.body.includes('answer')
  });

  sleep(1);
}
