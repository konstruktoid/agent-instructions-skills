I couldn't save a file because I only have read and search tools here. The script is below for you to save as `load/checkout.js`.

The repo doesn't show the checkout endpoint's route, port or request body. `k8s/deployment.yml` only names a `checkout` container (`ghcr.io/example/checkout:1.2.0`), and `docker-compose.yml` only exposes nginx on `8080`. So the URL, path and payload come from environment variables, and the default body is a placeholder you'll probably need to change.

```javascript
// load/checkout.js
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const CHECKOUT_PATH = __ENV.CHECKOUT_PATH || '/checkout';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

export const options = {
  scenarios: {
    checkout_ramp: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 50 },   // warm up
        { duration: '2m', target: 200 },  // ramp to 200 VUs
        { duration: '5m', target: 200 },  // hold at peak
        { duration: '1m', target: 0 },    // ramp down
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],                  // <1% errors
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // ms
    checks: ['rate>0.99'],
  },
};

function payload() {
  // Placeholder body: replace it with your real checkout schema.
  return JSON.stringify({
    cartId: `cart-${__VU}-${__ITER}`,
    items: [{ sku: 'SKU-123', quantity: 1 }],
    paymentMethod: 'test-card',
  });
}

export default function () {
  const headers = { 'Content-Type': 'application/json' };
  if (AUTH_TOKEN) headers.Authorization = `Bearer ${AUTH_TOKEN}`;

  const res = http.post(`${BASE_URL}${CHECKOUT_PATH}`, payload(), {
    headers,
    tags: { endpoint: 'checkout' },
  });

  check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
    'responds under 1s': (r) => r.timings.duration < 1000,
  });

  sleep(Math.random() * 2 + 1); // 1–3s think time between requests
}
```

To run it:

```bash
k6 run -e BASE_URL=https://staging.example.com -e CHECKOUT_PATH=/api/checkout load/checkout.js
```

**Before you run it:**
- **Payload:** replace the placeholder body with the real request schema. With the wrong fields, the 2xx check will fail on every request.
- **Target:** at 200 users, each sending a request every 1–3 seconds, this is about 65–200 requests per second for 5 minutes. Point it at staging, not production, especially since checkout may charge cards, reserve stock or create real orders. Use test payment credentials.
- **Thresholds:** the p95 under 500ms and error rate under 1% limits are general starting values. Change them to match your actual performance targets. k6 exits with a non-zero code when a threshold fails, so the script can also gate a CI step.

If you tell me the real route and request body, I can fill them in. With write access, I can also save the file to the repo.
