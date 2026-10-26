**Finding: the edge log contradicts the note's DNS root-cause claim.**

**What the incident note says** (`sources/incident-note.md`, lines 5–7):
- Checkout errored from 09:14 to 09:52.
- The root cause was a DNS failure: the service could not resolve `checkout-api.internal`.
- The resolver was restarted at 09:50 and the service recovered.

**What the edge log shows** (`sources/edge-log.txt`):
- DNS resolved every time it was tried. Lines 1, 4, 7, 10 and 13 are all `resolver checkout-api.internal A NOERROR 1 answer`, at 4–5 ms. These cover 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12. That includes the whole outage window and the moment the note says the resolver was restarted.
- TCP connections to 10.4.2.17:443 succeeded (lines 2, 5, 8, 11, 14).
- The TLS handshake failed with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12). It had succeeded at 09:13:58 (line 3).
- The first success after the outage is at 09:52:03 (lines 14–15), a TCP connect plus a TLS handshake that worked.

**Reconciling the two:**
- The log points to an expired certificate on the checkout endpoint as the failure mechanism. DNS was healthy throughout, so "could not resolve" is contradicted for every attempt the log records.
- The timing fits the certificate explanation. The handshake worked at 09:13:58 and failed from 09:14:02. That matches the note's 09:14 start.
- The 09:50:12 resolver query was a normal NOERROR, and the log shows no sign of a resolver fault before it.

**Where the evidence stops:**
- The log is sparse. It has 5 sampled resolver lookups and nothing between 09:31:40 and 09:50:12, so it can't rule out a brief DNS failure in a gap. It does show no DNS failure in any recorded lookup.
- It doesn't say why the outage ended. There is no record of a certificate renewal or rotation. The log shows only that the handshake worked by 09:52:03.
- The note doesn't cite any evidence for its DNS claim. The log is a record from the edge and not from the checkout service's own resolver. So the log shows resolution working at the edge, not necessarily what the checkout service saw.
- The log doesn't directly record customer-facing errors. It records the connection-level failures that explain them.

CONCLUSION: UNSUPPORTED
