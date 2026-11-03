# Evidence synthesis: was DNS the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

- **Incident note** (`sources/incident-note.md`, lines 3–7). The on-call engineer wrote it at 10:05. It makes these claims:
  - Checkout errored from 09:14 to 09:52.
  - The root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`, so every request failed.
  - The resolver was restarted at 09:50 and the service recovered.
- **Edge log** (`sources/edge-log.txt`, lines 1–15). It holds timestamped resolver, TCP, and TLS entries for `checkout-api.internal` and 10.4.2.17:443. The note and the log are the only two sources.

## Findings

Source facts:

1. Every resolver entry returns `NOERROR` with 1 answer in 4–5 ms (lines 1, 4, 7, 10, 13). That covers 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12. No resolver failure appears anywhere in the log.
2. TCP connects to 10.4.2.17:443 succeed each time, in 3 ms (lines 2, 5, 8, 11, 14).
3. The TLS handshake succeeded at 09:13:58 (line 3). It failed with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12).
4. The first failure comes 4 seconds after the last good handshake, at the start of the stated outage window (09:14).
5. The only resolver entry after 09:31:40 is at 09:50:12 (line 13), and it is a normal success. The next entry is a TCP connect and TLS handshake that both succeed at 09:52:03 (lines 14–15). That matches the end of the outage window. The log has no entry showing what changed between 09:31:40 and 09:52:03.

Inference connecting the facts:

- The name resolved correctly throughout, to the same address. The log therefore contradicts the note's mechanism that the service "could not resolve" the name.
- The failures occur at the TLS layer and name an expired certificate. That is a more direct explanation of the failures than DNS.

## Conclusions and conditions

- **The DNS root-cause claim is unsupported.**
  - It holds on the condition that the edge log is a faithful record of the resolution path the checkout service used.
  - The log is an edge-side record. It does not show the checkout service's own resolver calls, so a failure on a different resolver path is not excluded. The note names no such path and gives no error text or log excerpt, so the claim has no evidence in the sources.
- **The note's recovery narrative is not corroborated.** The resolver restart at 09:50 appears nowhere in the log. The only resolver entry near that time (09:50:12) is an ordinary success. The log also contains no record of a certificate renewal. I do not conclude that the restart did nothing, because the log does not show what restored service.
- **The sources do not establish an alternative root cause.** They show the proximate failure was an expired certificate on the TLS handshake. They say nothing about why the certificate expired or how it was fixed, so the expired certificate cannot be called the root cause on this evidence alone.

## Open questions

1. What did the checkout service's own logs report during the outage? Did they show resolution errors, TLS errors, or both?
2. When did the certificate on 10.4.2.17 expire, and what was replaced or renewed before 09:52:03?
3. What did the 09:50 resolver restart consist of, and why did the note's author link it to recovery?
4. What happened between 09:31:40 and 09:52:03? The log has no entries in that interval apart from the 09:50:12 resolver lookup.

## Recommended next action

The main conversation should not accept the DNS root cause in the incident note. It should ask the author for the evidence behind the DNS claim and obtain certificate expiry and renewal records for 10.4.2.17 and the checkout service's own logs. The note should be corrected or supported once those are in hand.

CONCLUSION: UNSUPPORTED
