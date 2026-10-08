I couldn't save the file because the Write tool is disabled in this session. Here is the script. Save it as `loadtest/checkout.js`, a new directory so it stays apart from the pytest files in `tests/`.

```javascript
// k6 load test for the checkout endpoint.
//
// Run:
//   k6 run -e BASE_URL=http://localhost:8080 loadtest/checkout.js
//
// Env:
//   BASE_URL       service root (default http://localhost:8080)
//   CHECKOUT_PATH  endpoint path (default /checkout)
//   AUTH_TOKEN     optional bearer token

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const CHECKOUT_PATH = __ENV.CHECKOUT_PATH || '/checkout';

const checkoutFailures = new Rate('checkout_failures');
const checkoutDuration = new Trend('checkout_duration', true);

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // warm up
    { duration: '2m', target: 200 },  // ramp to peak
    { duration: '3m', target: 200 },  // hold at peak
    { duration: '1m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800', 'p(99)<1500'],
    checkout_failures: ['rate<0.01'],
  },
};

export default function () {
  // Unique per iteration so the service doesn't dedupe orders.
  const payload = JSON.stringify({
    cartId: `cart-${__VU}-${__ITER}`,
    items: [{ sku: 'SKU-123', quantity: 1 }],
    paymentMethod: 'test-card',
  });

  const headers = { 'Content-Type': 'application/json' };
  if (__ENV.AUTH_TOKEN) {
    headers.Authorization = `Bearer ${__ENV.AUTH_TOKEN}`;
  }

  const res = http.post(`${BASE_URL}${CHECKOUT_PATH}`, payload, {
    headers,
    tags: { name: 'checkout' },
  });

  const ok = check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });

  checkoutFailures.add(!ok);
  checkoutDuration.add(res.timings.duration);

  sleep(Math.random() * 2 + 1); // 1-3s think time
}
```

I haven't run it, because k6 and a target service weren't available here.

- **Ramp:** the load goes 0 → 50 → 200 VUs, holds 200 for 3 minutes, then ramps down.
- **Placeholders:** the repo doesn't define a checkout endpoint. The only match is the `checkout` image in `k8s/deployment.yml`. The `/checkout` path, the JSON payload and the bearer-token auth are my guesses, so adjust them to the real API contract.
- **Thresholds:** p95 under 800 ms, p99 under 1500 ms, and an error rate under 1%. These are also guesses, so tune them to your SLOs.
- **Where to run it:** point `BASE_URL` at a staging environment. Checkout creates orders and may charge payments, so don't aim 200 VUs at production.
