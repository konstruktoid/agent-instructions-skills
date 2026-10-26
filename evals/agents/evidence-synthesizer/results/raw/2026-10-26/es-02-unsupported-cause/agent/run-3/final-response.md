# Evidence synthesis: was DNS failure the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

- **Incident note** (`sources/incident-note.md`, lines 3–7). The on-call engineer wrote it at 10:05. It makes these claims:
  - Checkout returned errors from 09:14 to 09:52.
  - The root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`.
  - The resolver was restarted at 09:50, and the service recovered.
  - The note cites no evidence for any of these claims.
- **Edge log** (`sources/edge-log.txt`, lines 1–15). Each connection attempt logs a resolver, TCP and TLS step.
  - Resolver lines (1, 4, 7, 10, 13) all show `checkout-api.internal A NOERROR 1 answer`, taking 4–5 ms. This includes lines 4, 7 and 10 at 09:14:02, 09:14:07 and 09:31:40, which fall inside the outage window.
  - TCP connects to 10.4.2.17:443 succeed in every logged attempt (lines 2, 5, 8, 11, 14).
  - The TLS handshake succeeded at 09:13:58 (line 3).
  - The TLS handshake failed with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12).
  - The handshake succeeded again at 09:52:03 (line 15).

## Findings

1. **Source fact: DNS resolved during the outage.** Name resolution returned NOERROR with an answer at every logged point in the window (edge-log lines 4, 7, 10). This contradicts the note's statement that the service "could not resolve" the name.
2. **Source fact: the failure was at the TLS layer.** The connection reached the host over TCP, and the TLS handshake then failed with `certificate_expired`. The first failure is at 09:14:02, which matches the note's 09:14 start. The handshake worked at 09:13:58, just before.
3. **Source fact: the log shows no resolver change.** It has a resolver query at 09:50:12 that returned NOERROR, like the earlier ones. It records no restart and no earlier resolution failure. The note's 09:50 restart is therefore uncorroborated by the log.
4. **Source fact: recovery came after the restart.** The first successful handshake is at 09:52:03 (line 15), and the log shows no step in between. The log does not say what changed between 09:31:40 and 09:52:03. It does not show a certificate renewal, and it does not rule one out.
5. **Inference: the cause was probably an expired certificate.** The log's only failure signal is `certificate_expired`, and resolution and TCP were healthy. This is an inference. The log does not name which certificate expired or why the handshake recovered at 09:52.
6. **Inference: the recovery fits the restart only by timing.** The note links the recovery to the resolver restart, but the log shows nothing that connects the two. Resolution was healthy both before and after the restart.

## Conclusions and conditions

- **The claim that DNS failure was the root cause is unsupported.** The edge log contradicts it directly: the resolver answered successfully throughout the outage window, and the logged failures are TLS certificate expiry. The note gives no contrary evidence of its own.
  - This holds provided the edge log is representative of what the checkout service saw. The log has gaps, with entries at only 09:13:58, 09:14:02, 09:14:07, 09:31:40, 09:50:12 and 09:52:03.
  - The log may be from the edge and not from the checkout service's own resolver. That is a boundary on the conclusion, and I found nothing in the sources that settles it.
- **The certificate-expiry explanation is not established.** The sources suggest it but do not prove it. They give no certificate details, no renewal record and no application error logs.

## Open questions

- Which certificate expired, and when was it renewed or replaced before 09:52:03?
- Did the checkout service use the same resolver as the edge log's? Does a service-side log show a resolution failure?
- What did the 09:50 resolver restart do, and what evidence led the on-call engineer to a DNS diagnosis?

## Recommended next action

The main conversation should treat the note's DNS root cause as unsupported by the available evidence. It should ask for certificate issuance and renewal records for `checkout-api.internal` and for the checkout service's own resolver logs. These would confirm or rule out the expired-certificate explanation. Until then, the note should not be cited as established.

CONCLUSION: UNSUPPORTED
