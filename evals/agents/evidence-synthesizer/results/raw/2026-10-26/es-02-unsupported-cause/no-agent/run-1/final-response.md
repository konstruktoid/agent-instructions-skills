**Conclusion: the sources don't support the DNS root-cause claim. The edge log contradicts it.**

**What the incident note claims** (`sources/incident-note.md`, lines 5–7)
- Checkout failed from 09:14 to 09:52.
- The root cause was a DNS failure: the service "could not resolve `checkout-api.internal`".
- The resolver was restarted at 09:50 and the service recovered.

**What the edge log shows** (`sources/edge-log.txt`)
- DNS resolution worked throughout. Every resolver line for `checkout-api.internal` is `NOERROR 1 answer` in 4–5 ms. These are at 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12 (lines 1, 4, 7, 10, 13). No lookup in the log failed.
- The TCP connect to 10.4.2.17:443 succeeded each time (lines 2, 5, 8, 11, 14).
- The failure was at the TLS step. At 09:14:02, 09:14:07 and 09:31:40 the handshake was `FAILED alert=certificate_expired` (lines 6, 9, 12).
- The 09:13:58 handshake succeeded (line 3). The first failure at 09:14:02 matches the note's 09:14 start.
- Service recovered at 09:52:03, when the handshake succeeded (lines 14–15). The only event shortly before that is the 09:50:12 lookup, which was normal. The log shows no resolver restart and no certificate renewal.

**Where the evidence stops**
- The log does not show what fixed the problem. It doesn't show the certificate being replaced or the resolver being restarted, so I can't confirm the 09:50 restart or say what actually restored service.
- The log has only a few sampled lines. It doesn't show the 09:14–09:52 window continuously, and it doesn't show the customer-facing errors.
- An expired certificate is the only failure the log shows. The log doesn't prove it was the root cause, but nothing in it points to DNS.
- The note is the only source for the restart and for its claim that the service "could not resolve" the name. The log has no evidence for either.

CONCLUSION: UNSUPPORTED
