# Evidence synthesis: was a DNS failure the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

| Ref | Source and location | Statement (source fact) |
|---|---|---|
| A | `sources/incident-note.md`, lines 5-7 | Checkout returned errors from 09:14 to 09:52. |
| B | `incident-note.md`, lines 5-7 | The note says the root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`. |
| C | `incident-note.md`, lines 6-7 | The resolver was restarted at 09:50 and the service recovered. |
| D | `incident-note.md`, line 3 | The on-call engineer wrote the note at 10:05. The note cites no log or other evidence. |
| E | `sources/edge-log.txt`, lines 1, 4, 7, 10, 13 | Every resolver lookup of `checkout-api.internal` returned `A NOERROR 1 answer`, in 4-5 ms. This includes 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12. |
| F | `edge-log.txt`, lines 2, 5, 8, 11 | TCP connects to 10.4.2.17:443 succeeded at every logged attempt before recovery. |
| G | `edge-log.txt`, lines 6, 9, 12 | TLS handshakes failed with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40. |
| H | `edge-log.txt`, lines 1-3 | At 09:13:58 resolution, TCP and TLS all succeeded. |
| I | `edge-log.txt`, lines 13-15 | At 09:50:12 resolution succeeded. At 09:52:03 TCP and TLS succeeded, with no failure entry in between. |

## Findings

**Agreement.** The log agrees with the note on the outage window. Healthy traffic at 09:13:58 is followed by failures from 09:14:02. A successful handshake appears at 09:52:03 (A, H, I, G).

**Conflict on the failing layer.** The note says name resolution failed (B). The log shows resolution succeeding with a valid answer at every logged point, including during the outage (E). The failures are at the TLS layer, after DNS and TCP had both succeeded, and they carry a specific alert, `certificate_expired` (F, G). The log therefore contradicts the note's mechanism that the service "could not resolve" the name and that "every request failed" for that reason.

**Resolver restart.** The note presents the 09:50 restart as the fix (C). The log shows no resolver fault before or at 09:50: the 09:50:12 lookup is the same healthy answer as earlier lookups (E). The log does not show what changed between 09:50:12 and 09:52:03 that ended the TLS failures, and it does not say whether the restart caused the recovery. This is an inference gap, not a log fact. The recovery is consistent with a certificate renewal or replacement, but the log does not show one.

**Source limitations.**
- The log has only 9 timestamps over 38 minutes, with a gap from 09:14:07 to 09:31:40 and another from 09:31:40 to 09:50:12. It does not record every request.
- The log is named `edge-log`. It records the resolver, TCP and TLS steps from one vantage point, and its client identity is unstated. It may not be the checkout service's own resolver view.
- The note's authorship is a person writing at 10:05, and it gives no evidence for its claim (D).

## Conclusions and conditions

1. **A DNS failure as root cause is unsupported.**
   - Support: E shows successful resolution throughout, including during the outage. F and G show the failure occurring after DNS succeeded.
   - Condition: this holds if the log reflects the resolution path the checkout service uses.
   - Boundary: the log cannot exclude a DNS failure on a path or at a time it did not record, such as the unlogged gaps or another client. The note offers no evidence of such a failure.

2. **An expired certificate on 10.4.2.17:443 is the proximate failure the log shows, but it is not established as the root cause.**
   - Support: G.
   - Boundary: the log does not show why the certificate expired, which certificate it was, or what ended the failures at 09:52. Whether the certificate caused every customer error is also not shown, since the log is sparse.

3. **The restart-as-fix claim is unresolved.** The log neither shows a resolver fault nor explains the recovery.

## Open questions

- Which client produced the log, and does it match the checkout service's own resolver path?
- What evidence did the on-call engineer use for the DNS claim: service errors, resolver logs, or something else?
- What happened to the certificate on 10.4.2.17 between 09:50:12 and 09:52:03?
- Do any logs cover the gaps between 09:14:07 and 09:52:03?

## Recommended next action

Return to the main conversation that the note's root-cause statement should not be accepted as written. Ask the incident owner for the checkout service's own error logs, the resolver's logs for 09:14-09:52, and the certificate's validity dates and renewal history for `checkout-api.internal` at 10.4.2.17. The note should then be revised or its claim supported with those logs.

CONCLUSION: UNSUPPORTED
