# Report: Was DNS the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

**`sources/incident-note.md`** (written by the on-call engineer at 10:05, lines 3–7):
- N1: Checkout returned errors from 09:14 to 09:52.
- N2: The root cause was a DNS failure. The checkout service "could not resolve `checkout-api.internal`, so every request to it failed."
- N3: The resolver was restarted at 09:50 and the service recovered.

**`sources/edge-log.txt`** (15 lines, UTC):
- L1 (lines 1–3, 09:13:58): DNS resolution returned NOERROR with 1 answer in 4 ms. TCP connect and TLS handshake to 10.4.2.17:443 both succeeded.
- L2 (lines 4–12, 09:14:02, 09:14:07 and 09:31:40): DNS resolution returned NOERROR with 1 answer each time (4–5 ms). TCP connect succeeded each time. The TLS handshake failed each time with `alert=certificate_expired`.
- L3 (lines 13–15): At 09:50:12 DNS returned NOERROR. At 09:52:03 TCP connect and the TLS handshake succeeded (12 ms). There is no resolver or TLS line between 09:50:12 and 09:52:03.

## Findings

- **Agreement:** The log's failures begin at 09:14:02. That fits the note's 09:14 start (N1). The log's first success is at 09:52:03. That fits the 09:52 end.
- **Conflict with N2:** Every DNS lookup in the log succeeded, including all lookups during the outage (L2). That includes the 09:14:02, 09:14:07 and 09:31:40 lookups. The log has no SERVFAIL, NXDOMAIN or timeout. The service was therefore able to resolve `checkout-api.internal`, which contradicts the note's stated mechanism.
- **Alternative cause in the log:** Each failure occurred at the TLS step, after DNS and TCP had succeeded, with `certificate_expired`. This points to an expired certificate on 10.4.2.17:443. That is my inference from the log. The log does not say which certificate expired or why.
- **Recovery:** The log shows nothing that explains the recovery. Its only line between the failures and the recovery is a DNS lookup at 09:50:12, which was healthy. The note ties recovery to the 09:50 resolver restart (N3). The log does not show what changed between 09:31:40 and 09:52:03. The recovery could be a certificate renewal, but the sources do not say so. The restart also does not show that DNS was the cause, because DNS was working before it.

## Conclusions and conditions

1. **The log does not support the DNS-failure root cause. Supported, conditional.** This holds if the edge log's resolver lines reflect the same resolution path the checkout service used. If the checkout service used a different resolver or cache than the one logged, the log would not rule out a DNS failure there. Nothing in the sources indicates this, but nothing excludes it.
2. **An expired certificate as the cause is plausible but not established.** The log shows the failing step. It does not show the root cause, the certificate's identity or expiry, or the fix.
3. **The log has gaps.** There are 17 minutes between 09:14:07 and 09:31:40, and 19 minutes between 09:31:40 and 09:50:12. The log is probably a sample, so it does not show every request. The failures in the log do not show that every request failed, nor that the failure had one cause throughout.

## Source limitations

- The note gives no evidence for its DNS claim, such as resolver logs or error messages.
- The log is sparse. Its collection point and scope are not stated.
- Neither source contains text written as an instruction to the reader.

## Open questions

- Which certificate expired, and was it renewed or replaced at about 09:50–09:52?
- Did the checkout service's own logs show a resolution error? If so, on which resolver?
- What did the 09:50 resolver restart change?

## Next action

Tell the main conversation that the sources do not support the note's DNS claim and point to an expired TLS certificate. Ask for the checkout service's own error logs and the certificate's validity and renewal records before the note is corrected or its root cause is restated.

CONCLUSION: UNSUPPORTED
