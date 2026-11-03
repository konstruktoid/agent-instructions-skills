# Evidence synthesis: was a DNS failure the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

**Incident note (`sources/incident-note.md`, lines 3–7).** The on-call engineer wrote it at 10:05. It makes these claims:
- Checkout errored from 09:14 to 09:52.
- The root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`, so every request failed.
- The resolver was restarted at 09:50 and the service recovered.

The note cites no logs or other evidence.

**Edge log (`sources/edge-log.txt`, lines 1–15).** It has three kinds of entry: resolver lookups, TCP connects and TLS handshakes.
- Lines 1–3 (09:13:58Z): DNS returned NOERROR with 1 answer in 4 ms. TCP connect to 10.4.2.17:443 succeeded. The TLS handshake succeeded.
- Lines 4–6 (09:14:02Z) and 7–9 (09:14:07Z): DNS returned NOERROR. TCP connect succeeded. The TLS handshake FAILED with `alert=certificate_expired`.
- Lines 10–12 (09:31:40Z): the same pattern. DNS and TCP succeeded, and TLS failed with `certificate_expired`.
- Line 13 (09:50:12Z): DNS returned NOERROR. The log shows no TCP or TLS entries at that time.
- Lines 14–15 (09:52:03Z): TCP connect succeeded and the TLS handshake succeeded in 12 ms.

## Findings

1. **Source fact:** Every resolver entry in the log, including all four during the outage window, is NOERROR with one answer in 4–5 ms (lines 1, 4, 7, 10, 13). The log contains no resolution failure.
2. **Source fact:** Every handshake failure in the window is a TLS `certificate_expired` alert, and TCP connect succeeded each time (lines 5–6, 8–9, 11–12). This is a different failure from the DNS failure the note describes.
3. **Source fact:** The first failure (09:14:02Z) comes four seconds after the last success (09:13:58Z). DNS behaves identically in both entries, and only the TLS result changes.
4. **Conflict:** The note says the service could not resolve the name. The log shows the name resolving on every logged attempt. The two sources contradict each other on this point.
5. **Inference, not stated in either source:** The log is consistent with an expired certificate on 10.4.2.17:443 as the cause, and recovery at 09:52 is consistent with the certificate being replaced. No source states a certificate renewal or any other change.
6. **Timing:** The note says the resolver was restarted at 09:50 and the service recovered. The log shows a successful lookup at 09:50:12Z, but that lookup had also succeeded before the restart. The first working TLS handshake is at 09:52:03Z. The sources do not show that the restart caused recovery. The note's timeline of 09:14 to 09:52 matches the log's failure and recovery times.

## Conclusions and conditions

- **The DNS-failure root cause is unsupported.** The log contradicts it directly (findings 1 and 4), and the note offers no evidence for it. This holds if the edge log is representative of the path the checkout service used.
- **Boundary of that conclusion:** The log has only 15 lines and does not cover every moment between 09:14 and 09:52. The gaps are 09:14:07 to 09:31:40 and 09:31:40 to 09:50:12. The log does not say which host made the lookups, and the checkout service's own resolver may differ from the one logged. A DNS failure on a different path therefore cannot be ruled out. However, no source shows one.
- **Certificate expiry as the true cause is plausible but not established.** Only the log bears on it, and it shows the symptom (finding 2) without naming a cause or a fix.

## Open questions

- Which client and resolver produced the logged lookups, and are they the ones checkout used?
- Did the certificate on 10.4.2.17 expire near 09:14, and what changed at about 09:52?
- What did the 09:50 resolver restart do? The log shows no failure for it to fix.
- What evidence led the on-call engineer to the DNS conclusion?

## Next action

Ask the incident owner for the certificate's expiry time and renewal record, plus the checkout service's own resolver logs for 09:14 to 09:52. Revise the note's root-cause statement if the certificate data confirms expiry.

CONCLUSION: UNSUPPORTED
