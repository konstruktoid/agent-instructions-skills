# Report: was DNS the root cause of the 2026-09-02 checkout outage?

## Evidence inventory

**`sources/incident-note.md`**
- Lines 5–8: Checkout returned errors from 09:14 to 09:52.
- Lines 5–8: The note says the root cause was a DNS failure, because the checkout service could not resolve `checkout-api.internal`.
- Lines 5–8: The resolver was restarted at 09:50 and the service recovered.
- Line 3: The on-call engineer wrote it at 10:05.
- The note gives no log excerpt, query output or other evidence for the DNS claim.

**`sources/edge-log.txt`**
- Lines 1, 4, 7, 10 and 13: Every resolver lookup of `checkout-api.internal` returned `NOERROR` with 1 answer, in 4–5 ms. This includes lookups at 09:14:02, 09:14:07 and 09:31:40, which fall inside the outage window.
- Lines 2, 5, 8 and 11: Every TCP connect to 10.4.2.17:443 succeeded.
- Lines 6, 9 and 12: From 09:14:02 on, the TLS handshake failed with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40.
- Lines 1–3: At 09:13:58, just before the outage, the handshake succeeded.
- Lines 14–15: At 09:52:03 the TLS handshake succeeded.
- Line 13: The 09:50:12 resolver lookup was normal. It shows no resolver change, and no resolver restart appears in the log.

## Findings

1. **Source fact:** Name resolution worked during the outage. Every logged lookup, including those at 09:14:02, 09:14:07 and 09:31:40, returned a valid answer (edge-log lines 4, 7, 10). This contradicts the note's statement that the service "could not resolve" the name (note line 5).
2. **Source fact:** The failures in the log occur at the TLS layer, with `certificate_expired`, after DNS and TCP had succeeded (edge-log lines 4–6, 7–9, 10–12).
3. **Source fact:** The failures begin at 09:14:02, which matches the note's 09:14 start time. The log's first failure is the first sign of trouble.
4. **Source fact:** The log shows no resolver restart, and the log has no entry between 09:50:12 and 09:52:03. The note's 09:50 restart is therefore uncorroborated. The recovery shown at 09:52:03 is a successful handshake, but the log does not say why it recovered.
5. **Inference:** The log is consistent with an expired certificate as the cause, but that is not established. A certificate renewal or rotation around 09:50–09:52 would fit, but the log does not record one.

## Conclusions and conditions

- **The DNS root-cause claim is unsupported.** It is contradicted by successful resolutions during the outage. The condition is that the log is a faithful record of the lookups checkout actually made. If the checkout service used a different resolver or cache than the one logged, the log would not speak to that path.
- **The alternative cause, an expired certificate, is supported as a proximate failure mechanism, but not as a root cause.** The log shows what failed, not why the certificate expired or what changed at recovery.
- **The recovery explanation is unresolved.** The sources neither confirm nor refute that the resolver restart caused the recovery. The log shows no DNS fault for a restart to fix.

## Limits and gaps

- The log has only 12 entries in the outage window, with gaps from 09:14:07 to 09:31:40 and from 09:31:40 to 09:50:12. It does not show every request or customer error.
- The log does not say which component produced it. The filename suggests an edge vantage point, and the note does not say the checkout service's own resolver view matches it.
- There is no record of a certificate renewal, a resolver restart, or the checkout service's own error messages.

## Open questions

- What was done between 09:50 and 09:52 (certificate renewal, rotation, or service restart)?
- Does checkout use the same resolver as the one logged?
- What evidence led the on-call engineer to conclude DNS was at fault?

## Recommended next action

Ask the author for the evidence behind the DNS claim. Pull the certificate's `notAfter` date and any change records for 09:50–09:52 to confirm or rule out expiry as the cause. Revise the incident note unless DNS evidence turns up.

CONCLUSION: UNSUPPORTED
