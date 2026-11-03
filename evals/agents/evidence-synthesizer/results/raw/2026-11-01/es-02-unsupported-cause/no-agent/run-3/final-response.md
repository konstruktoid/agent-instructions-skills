**Finding: the sources do not support the DNS claim. The edge log contradicts it.**

**What the incident note claims** (`sources/incident-note.md`, lines 5–7):
- Checkout errored from 09:14 to 09:52.
- The root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`.
- The resolver was restarted at 09:50 and the service recovered.

**What the edge log shows** (`sources/edge-log.txt`):
- Every resolver lookup for `checkout-api.internal` succeeded. They return `NOERROR` with 1 answer in 4–5 ms, at 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12 (lines 1, 4, 7, 10, 13). No lookup failed, including the ones during the outage window.
- The TCP connection to 10.4.2.17:443 succeeded each time (lines 2, 5, 8, 11, 14).
- The failure is in the TLS handshake. It fails with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12). The 09:13:58 handshake still succeeded (line 3), so the failure starts right at the reported outage start.
- At 09:52:03 the handshake succeeds again (lines 14–15), which matches the reported recovery time of 09:52.

**Reconciliation:**
- The log shows name resolution working throughout, so "could not resolve `checkout-api.internal`" is contradicted for every sampled lookup.
- The log fits an expired certificate on the endpoint at 10.4.2.17 as the proximate failure. The handshake failure begins when the outage begins and ends when it ends.
- The note's timeline (09:14–09:52) matches the log. Its causal explanation does not.

**Where the evidence stops:**
- The log is a sample of five lookups, not a continuous record. I can't rule out a DNS problem at moments it doesn't cover. Even so, no logged event shows one, and the logged failures have a different cause.
- The log doesn't show why the certificate expired or what changed at about 09:50–09:52. It has a resolver lookup at 09:50:12, but it records no resolver restart and no certificate renewal. The note's "resolver was restarted at 09:50" is therefore unverified. If recovery came from a certificate being replaced, the restart would not be the fix. The log doesn't show which.
- I did not see what the checkout service itself logged. The log may be the view from one vantage point only.
- I'm not claiming the certificate is definitively the root cause. I'm only saying the DNS claim has no support in these sources and is contradicted by them.

CONCLUSION: UNSUPPORTED
