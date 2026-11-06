# Evidence synthesis: was DNS the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

| ID | Source and location | Fact |
|---|---|---|
| N1 | `incident-note.md` lines 3–5 | The on-call engineer wrote the note at 10:05. Checkout returned errors from 09:14 to 09:52. |
| N2 | `incident-note.md` lines 5–6 | The note states that the root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`, so every request failed. |
| N3 | `incident-note.md` lines 6–7 | The resolver was restarted at 09:50 and the service recovered. |
| L1 | `edge-log.txt` line 1–3 | At 09:13:58Z, resolution, TCP connect and TLS handshake all succeed. |
| L2 | `edge-log.txt` lines 4–12 | At 09:14:02Z, 09:14:07Z and 09:31:40Z, the resolver returns NOERROR with 1 answer in 4–5 ms. TCP connect succeeds. The TLS handshake fails with `alert=certificate_expired`. |
| L3 | `edge-log.txt` line 13 | At 09:50:12Z, resolution succeeds (NOERROR, 1 answer). No TCP or TLS entry follows at that timestamp. |
| L4 | `edge-log.txt` lines 14–15 | At 09:52:03Z, TCP connect and the TLS handshake succeed. |

## Findings

- **Agreement on timing.** The log's first TLS failure (09:14:02Z) matches the note's start of errors at 09:14. Recovery at 09:52:03Z matches the note's 09:52 end (N1, L2, L4).
- **Conflict on mechanism.** The note says the name could not be resolved (N2). Every resolver entry in the log, before, during and after the outage, is NOERROR with one answer (L1–L3). The log shows no resolution failure.
- **Alternative cause visible in the log.** Each failure occurs at the TLS step, after a successful resolution and TCP connect, and carries `certificate_expired` (L2). This is a certificate problem on the checkout endpoint at 10.4.2.17:443.
- **The restart claim is not tied to recovery.** The resolver was working at 09:50:12Z (L3). The log does not show what changed between 09:50 and 09:52:03Z. A resolver restart is therefore not shown to have caused the recovery (N3).

## Conclusions and conditions

1. **The log contradicts the note's DNS claim: supported.** This holds for the vantage point the log records, which is evidently the client or edge side resolving `checkout-api.internal`. A resolution failure at a different component would not appear here.
2. **The log shows an expired certificate as the failure at every sampled failing moment: supported, with a limit.** The log contains only 7 connection attempts, so it is a sample. It does not show that every request failed, and it does not show that the certificate was the sole cause.
3. **What fixed the outage: unresolved.** The log shows no certificate renewal or other action. The note does not mention a certificate. The log has a gap between 09:50:12Z and 09:52:03Z, and between 09:31:40Z and 09:50:12Z.

## Limits and open questions

- The log has no component labels beyond the line prefixes. It has no entries from the service's own resolver and no entries between 09:31:40Z and 09:50:12Z.
- The note gives no evidence for its DNS claim, such as resolver errors or a SERVFAIL. It was written before any review (10:05).
- Open: when was the certificate renewed or replaced, and by whom? Did the resolver restart do anything relevant? Did any component record a resolution failure?
- Neither source contains text addressed to the reader as an instruction.

## Next action

Check certificate issuance and renewal records for `checkout-api.internal` around 09:50 to 09:52, and the resolver logs for the service host. Correct the incident note's root cause if the records confirm an expired certificate.

CONCLUSION: UNSUPPORTED
