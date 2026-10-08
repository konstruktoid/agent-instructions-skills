I couldn't save the file because the Write tool is disabled in this session. Here is the script, ready to save as `loadtests/checkout.js`. I haven't run it.

```js
// k6 load test for the checkout endpoint.
//
// Run:
//   k6 run -e BASE_URL=http://checkout:8080 loadtests/checkout.js
//
// Environment:
//   BASE_URL       service base URL   (default http://localhost:8080)
//   CHECKOUT_PATH  checkout route     (default /checkout)
//   AUTH_TOKEN     optional bearer token

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const CHECKOUT_PATH = __ENV.CHECKOUT_PATH || '/checkout';

const checkoutFailures = new Rate('checkout_failures');

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '3m', target: 200 }, // ramp to peak
    { duration: '5m', target: 200 }, // hold at peak
    { duration: '2m', target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800', 'p(99)<1500'],
    checkout_failures: ['rate<0.01'],
  },
};

export default function () {
  const payload = JSON.stringify({
    cartId: `cart-${__VU}-${__ITER}`,
    items: [{ sku: 'SKU-1001', quantity: 1 + (__ITER % 3) }],
    paymentMethod: 'test-card',
  });

  const headers = { 'Content-Type': 'application/json' };
  if (__ENV.AUTH_TOKEN) {
    headers.Authorization = `Bearer ${__ENV.AUTH_TOKEN}`;
  }

  const res = http.post(`${BASE_URL}${CHECKOUT_PATH}`, payload, { headers });

  const ok = check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });
  checkoutFailures.add(!ok);

  sleep(1 + Math.random() * 2); // think time
}
```

- **Ramp:** the test goes to 50 virtual users over 2 minutes, then to 200 over 3 minutes. It holds 200 for 5 minutes and ramps down over 2 minutes.
- **Thresholds:** the test fails if more than 1% of requests fail, or if p95 latency is over 800 ms or p99 is over 1500 ms. These numbers are placeholders, so adjust them to your SLOs.
- **Assumptions:** the repo doesn't define the checkout route, port or request schema. I assumed `POST /checkout` on port 8080, with a JSON body of `cartId`, `items` and `paymentMethod`. Change `CHECKOUT_PATH` and the payload to match the real API.
- **Safety:** point this at a staging or test environment, since each request submits a checkout.

If you'd like me to write it to disk, enable the Write tool or tell me where to put it.
