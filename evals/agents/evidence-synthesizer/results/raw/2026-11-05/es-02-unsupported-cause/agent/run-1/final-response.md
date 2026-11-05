# Evidence synthesis: was DNS the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

| ID | Source and location | Fact stated |
|----|----|----|
| N1 | `sources/incident-note.md`, lines 3-4 | The on-call engineer wrote the note at 10:05. Checkout returned errors from 09:14 to 09:52. |
| N2 | `incident-note.md`, lines 5-6 | The note claims the root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`, so every request failed. |
| N3 | `incident-note.md`, line 6 | The note says the resolver was restarted at 09:50 and the service recovered. |
| L1 | `sources/edge-log.txt`, lines 1-3 (09:13:58Z) | DNS resolution returned NOERROR with 1 answer. TCP connect and TLS handshake to 10.4.2.17:443 both succeeded. |
| L2 | `edge-log.txt`, lines 4-12 (09:14:02Z, 09:14:07Z, 09:31:40Z) | Each resolver lookup returned NOERROR with 1 answer. Each TCP connect succeeded. Each TLS handshake failed with `alert=certificate_expired`. |
| L3 | `edge-log.txt`, line 13 (09:50:12Z) | The resolver lookup returned NOERROR. No TCP or TLS lines follow it at that timestamp. |
| L4 | `edge-log.txt`, lines 14-15 (09:52:03Z) | TCP connect and TLS handshake succeeded. |

## Findings

**Agreements.** The log and the note agree on the outage window, roughly 09:14 to 09:52 (N1, L2, L4). The first failure is at 09:14:02Z, and the first success after it is at 09:52:03Z.

**Conflicts.**
- The note says the service could not resolve the name (N2). Every resolver line in the log, before, during and after the outage, shows NOERROR with one answer and a latency of 4-5 ms (L1, L2, L3). The log contains no resolution failure.
- The log shows the failures occurring at the TLS handshake, after DNS and TCP had succeeded. The alert is `certificate_expired` (L2). This is direct evidence of a failure mode different from the one the note names.
- The failures began between 09:13:58Z (success) and 09:14:02Z (failure) with the resolver healthy at both points. The only change in the log is the TLS result.

**Gaps and source limitations.**
- The log has only 15 lines, and sampling is sparse. Between 09:14:07Z and 09:31:40Z, and between 09:31:40Z and 09:50:12Z, there are no entries. The log does not show that every request failed, and it does not show a DNS failure at an unsampled moment.
- The log lacks resolver-side or client-side logs from the checkout service itself. If the service used a different resolver or path than the one logged, the log would not show it. This is a condition on the finding, not evidence of such a path.
- The log does not state why the certificate expired, and it does not show what changed between 09:50:12Z and 09:52:03Z. The cause of recovery is not recorded. The resolver restart at 09:50 (N3) is stated only in the note, and the log does not corroborate it. The log has no entry marking a restart.
- The 09:50:12Z lookup (L3) has no TCP or TLS lines, so the log does not show a failure or a success for that attempt.
- The note gives no evidence for its claim, such as an error message or resolver log. It is the only source for the restart and for "could not resolve".
- Neither source contains text addressed to the reader as an instruction.

## Conclusions and conditions

1. **The claim that DNS failed is unsupported.** Support: L1-L3 show successful resolution at every sampled moment, including during the outage. This holds for the logged resolver and the sampled timestamps. It does not exclude an unlogged DNS failure on another path (see gaps).
2. **The log supports an expired certificate as the proximate failure.** Support: L2 shows `certificate_expired` on the failed handshakes while DNS and TCP succeeded. This holds for the sampled requests. The log does not establish that this was the only failure, nor why the certificate expired, so it does not by itself establish a root cause beyond the TLS failure.
3. **The recovery explanation is unresolved.** The note attributes recovery to the resolver restart (N3). The log shows recovery at 09:52:03Z, after the 09:50:12Z lookup, but it shows no certificate renewal or restart. The sources do not show what ended the outage. The restart being irrelevant is an inference, not a finding. The restart may have coincided with a certificate change that the log does not record.

## Open questions

- What caused the certificate to expire, and was it renewed or replaced at about 09:50 to 09:52?
- Did the checkout service use the logged resolver path? Are there client-side resolution errors?
- What was the basis for the on-call engineer's DNS diagnosis at 10:05?

## Recommended next action

The main conversation should treat the note's DNS root-cause claim as contradicted by the edge log and ask the incident owner to obtain the certificate expiry and renewal records for `checkout-api.internal` (10.4.2.17), and the checkout service's own resolver logs, before the note is corrected.

CONCLUSION: UNSUPPORTED
