I don't have file-write access in this session, so here's the k6 script — save it as `k6/checkout.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // warm up
    { duration: '3m', target: 200 },  // ramp to peak
    { duration: '5m', target: 200 },  // hold at peak
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800'],
  },
};

export default function () {
  const payload = JSON.stringify({
    cartId: `cart-${__VU}-${__ITER}`,
    items: [{ sku: 'SKU-1', quantity: 1 }],
    paymentMethod: 'card',
  });

  const res = http.post(`${BASE_URL}/checkout`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(res, {
    'status is 200 or 201': (r) => r.status === 200 || r.status === 201,
  });

  sleep(1);
}
```

Run it with `k6 run k6/checkout.js -e BASE_URL=http://your-checkout-host`. The workspace's `k8s/deployment.yml` shows a `checkout` service, but there's no route/schema info here, so adjust the payload shape and endpoint path (`/checkout`) to match your actual API contract.
