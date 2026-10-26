The sources don't support the claim. The edge log contradicts it: DNS resolved normally throughout, and the failures were TLS certificate-expiry errors.

**What the incident note says** (`sources/incident-note.md`)
- Checkout failed from 09:14 to 09:52.
- The root cause was a DNS failure: the checkout service "could not resolve `checkout-api.internal`", so every request failed.
- Restarting the resolver at 09:50 is credited with the recovery.

**What the edge log shows** (`sources/edge-log.txt`)
- **DNS worked every time it was logged.** Every `resolver checkout-api.internal A` line returns `NOERROR 1 answer` in 4–5 ms. That covers 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12, including during the outage window (lines 1, 4, 7, 10, 13). I found no resolution failure in the log.
- **The failures are at the TLS layer.** TCP connects to 10.4.2.17:443 succeed (3 ms). The TLS handshake then fails with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12). The 09:13:58 handshake succeeded (line 3), so the failure begins between 09:13:58 and 09:14:02, which fits the note's 09:14 start.
- **Recovery is not tied to the resolver restart.** The log has no restart event. The only resolver line near 09:50 (line 13) is an ordinary successful lookup. The next handshake, at 09:52:03, succeeds (lines 14–15). That matches the note's 09:52 end, but the log doesn't say what changed. The expired certificate was probably replaced, but that is an inference, not something the log records.

**Where the evidence stops**
- The log is sparse: 5 resolver lookups in about 36 minutes. It can't rule out a DNS failure at an unlogged moment. It does show DNS succeeding at the start, middle and end of the window, and it shows an independent failure that explains the errors seen.
- The log comes from one vantage point. It doesn't show what the checkout service itself saw, so the note's claim that the service "could not resolve" the name isn't directly tested. The note gives no supporting evidence for that claim.
- Neither source records the restart, the certificate renewal, or what the customer-facing errors were. The actual root cause (certificate expiry) is what the log points to, but I can't confirm it from these two sources alone.

CONCLUSION: UNSUPPORTED
