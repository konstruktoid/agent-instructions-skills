I don't have a file-writing tool in this session, so the script is below for you to save as `load/checkout.js`. I haven't run it.

**What I found in the repo:** a `checkout` Deployment (`ghcr.io/example/checkout:1.2.0`) in `k8s/deployment.yml`. Nothing in the repo shows its route, port, request body or auth. The URL, path and payload below are my guesses, and you can override each one with an environment variable.

```javascript
// load/checkout.js
// Run: k6 run -e BASE_URL=https://staging.example.com load/checkout.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const CHECKOUT_PATH = __ENV.CHECKOUT_PATH || '/api/checkout';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

const checkoutFailures = new Rate('checkout_failures');
const checkoutDuration = new Trend('checkout_duration', true);

export const options = {
  scenarios: {
    checkout_ramp: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 50 },   // warm up
        { duration: '2m', target: 100 },
        { duration: '2m', target: 200 },  // ramp to peak
        { duration: '5m', target: 200 },  // hold at 200 VUs
        { duration: '1m', target: 0 },    // ramp down
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],                    // <1% errors
    http_req_duration: ['p(95)<500', 'p(99)<1500'],    // ms
    checkout_failures: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

function buildOrder() {
  return {
    cartId: `cart-${__VU}-${__ITER}`,
    items: [
      { sku: 'SKU-1001', quantity: 1 + Math.floor(Math.random() * 3) },
      { sku: 'SKU-2002', quantity: 1 },
    ],
    currency: 'USD',
    paymentMethod: { type: 'test_card', token: 'tok_visa' },
  };
}

export default function () {
  const headers = {
    'Content-Type': 'application/json',
    'Idempotency-Key': `${__VU}-${__ITER}-${Date.now()}`,
  };
  if (AUTH_TOKEN) headers.Authorization = `Bearer ${AUTH_TOKEN}`;

  const res = http.post(`${BASE_URL}${CHECKOUT_PATH}`, JSON.stringify(buildOrder()), {
    headers,
    tags: { endpoint: 'checkout' },
  });

  const ok = check(res, {
    'status is 200/201': (r) => r.status === 200 || r.status === 201,
    'has order id': (r) => {
      try {
        const body = r.json();
        return Boolean(body && (body.orderId || body.id));
      } catch (_) {
        return false;
      }
    },
  });

  checkoutFailures.add(!ok);
  checkoutDuration.add(res.timings.duration);

  sleep(1 + Math.random() * 2); // 1–3s think time between checkouts
}
```

**How it runs:** load climbs to 200 virtual users over 5 minutes, holds there for 5 minutes, then drops to zero over 1 minute. k6 exits with an error code if more than 1% of requests fail, or if response times go over 500 ms at the 95th percentile or 1.5 s at the 99th. That lets you use it as a pass/fail gate in CI.

**Before running it:**
- **Point it at a non-production environment.** Each run creates real checkout requests, so it could place orders or charge a payment provider. The payload assumes a test-mode card token (`tok_visa`), and the `Idempotency-Key` header prevents duplicate orders when a request is retried.
- **Match the payload and response to your API.** Replace the `buildOrder()` fields and the `orderId`/`id` check with whatever your checkout endpoint actually accepts and returns.
- **Tune the thresholds.** The 500 ms / 1.5 s and 1% values are starting guesses, not your actual service targets.

If you tell me the real route and request body, or point me to the checkout service's source, I can match the script to them.
