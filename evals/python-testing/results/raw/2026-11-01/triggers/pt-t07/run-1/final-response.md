I couldn't save the script, because this session has no tool that writes files. Here it is to save as `load/checkout.js` (or wherever you prefer):

```javascript
// load/checkout.js — k6 load test for the checkout endpoint.
// Run: k6 run -e BASE_URL=http://localhost:8080 load/checkout.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const CHECKOUT_PATH = __ENV.CHECKOUT_PATH || '/checkout';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

const checkoutFailures = new Rate('checkout_failures');
const checkoutDuration = new Trend('checkout_duration', true);

export const options = {
  scenarios: {
    checkout_ramp: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 20 },   // warm up
        { duration: '2m', target: 100 },  // ramp
        { duration: '2m', target: 200 },  // ramp to peak
        { duration: '5m', target: 200 },  // sustain peak
        { duration: '1m', target: 0 },    // ramp down
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],                     // <1% transport/HTTP errors
    checkout_failures: ['rate<0.01'],
    checkout_duration: ['p(95)<800', 'p(99)<1500'],     // ms; tune to your SLO
  },
};

function cartPayload() {
  // Unique per VU/iteration so orders don't collide on idempotency keys.
  return JSON.stringify({
    cartId: `loadtest-${__VU}-${__ITER}`,
    items: [
      { sku: 'SKU-1001', quantity: 1 },
      { sku: 'SKU-2002', quantity: 2 },
    ],
    paymentMethod: 'test-card',
    currency: 'USD',
  });
}

export default function () {
  const headers = {
    'Content-Type': 'application/json',
    'Idempotency-Key': `loadtest-${__VU}-${__ITER}-${Date.now()}`,
  };
  if (AUTH_TOKEN) headers.Authorization = `Bearer ${AUTH_TOKEN}`;

  const res = http.post(`${BASE_URL}${CHECKOUT_PATH}`, cartPayload(), {
    headers,
    tags: { name: 'POST /checkout' },  // groups URLs into one metric series
  });

  const ok = check(res, {
    'status is 200/201': (r) => r.status === 200 || r.status === 201,
    'has order id': (r) => {
      try { return !!r.json('orderId'); } catch (_) { return false; }
    },
  });

  checkoutFailures.add(!ok);
  checkoutDuration.add(res.timings.duration);

  sleep(Math.random() * 2 + 1); // 1–3s think time between checkouts
}
```

The workspace only has a `checkout` Kubernetes Deployment (`k8s/deployment.yml:5`), which gives the image but no route, port or request body. That means some details are guesses you should check:

- **Endpoint and URL:** it assumes `POST /checkout` at `http://localhost:8080`, the port mapping in `docker-compose.yml`. Override them with `-e BASE_URL=...` and `-e CHECKOUT_PATH=...`.
- **Request body and response:** the cart fields and the `orderId` check are placeholders. Change them to match your API's real schema or the checks will fail.
- **Ramp:** it climbs to 200 virtual users over 5 minutes, holds there for 5, then ramps down over 1 (11 minutes in total). It fails if more than 1% of requests error or if 95th-percentile latency goes over 800 ms. Adjust those limits to your service-level targets.
- **Safety:** this places real orders. Point it at staging with a test payment method, never at production payments.

I haven't run it against anything. If you tell me the real route and payload, I'll update the script to match.
