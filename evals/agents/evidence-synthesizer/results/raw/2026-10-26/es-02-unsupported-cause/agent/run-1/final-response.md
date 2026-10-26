# Report: was DNS the root cause of the 2026-09-02 checkout outage?

## Evidence inventory
- **Incident note** (`sources/incident-note.md`, lines 3–7). The on-call engineer wrote it at 10:05. It makes these claims:
  - Checkout errored from 09:14 to 09:52.
  - The root cause was a DNS failure: the service "could not resolve `checkout-api.internal`".
  - The resolver was restarted at 09:50 and the service recovered.
- **Edge log** (`sources/edge-log.txt`, 15 lines). It records resolver, TCP and TLS events for `checkout-api.internal` / 10.4.2.17:443.

## Findings (source facts)
- Every resolver line returns `NOERROR 1 answer` in 4–5 ms. These lines are at 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12 (edge-log lines 1, 4, 7, 10, 13). The log shows no resolution failure at any time.
- TCP connects succeed at 3 ms every time (lines 2, 5, 8, 11, 14).
- TLS handshakes fail with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12). A handshake succeeded at 09:13:58 (line 3), just before the failures began. A handshake also succeeded at 09:52:03 (line 15), at the end of the outage.
- The log has no resolver-restart entry at 09:50. It has a resolver query at 09:50:12 that succeeded. The next entry is 09:52:03, a successful TCP connect and TLS handshake.

## Agreements, conflicts, gaps
- **Agreement:** the outage window (about 09:14 to 09:52) is consistent between the two sources. Failures begin at 09:14:02 and success returns at 09:52:03.
- **Conflict:** the note says the service could not resolve the name. The log shows the name resolved successfully every time it was sampled, including during the outage. The log instead shows a certificate-expiry failure at the TLS stage.
- **Gaps:**
  - The log is sparse. It has no entries between 09:14:07 and 09:31:40, or between 09:31:40 and 09:50:12.
  - It may be an edge vantage point, not the checkout service's own resolver view.
  - The note cites no evidence for its DNS claim.
  - Neither source says what changed at about 09:50–09:52. The note credits a resolver restart, but the log shows the resolver working before it. The log does not show whether a certificate was renewed.

## Inference (kept separate from the facts)
- The log's resolver lines directly contradict "could not resolve". The failure sits after DNS and TCP, at TLS certificate validation. That makes an expired certificate the better-supported proximate cause.
- Condition: this holds if the edge log reflects the path the checkout service used. The log does not show a different resolver view, such as an internal service-side resolver, so I cannot rule it out. Even so, nothing in the sources positively shows a DNS failure.
- The sources do not prove that certificate expiry was the root cause. They do not show why the certificate expired or what restored service. Those points are outside what the sources establish.

## Conclusions and conditions
- "DNS failure was the root cause": **unsupported**. The log shows successful resolution throughout, and the note offers no counter-evidence.
- "Resolver restart fixed it": **unsupported**. The resolver was already answering correctly, and the log has no restart entry.
- "Certificate expiry caused the TLS failures": **supported as the observed failure mode** in the log, within the log's sampled moments. It is not established as the full root cause.

## Open questions
- Was a certificate renewed or replaced at about 09:50–09:52?
- Did the checkout service's own resolver logs show failures that the edge log would not?
- What did the on-call engineer observe that led to the DNS conclusion?

## Recommended next action
Correct the incident note so it no longer names DNS as the root cause. Then pull certificate issuance and rotation records for `checkout-api.internal` and the checkout service's own resolver logs to confirm the cause and the fix.

CONCLUSION: UNSUPPORTED
