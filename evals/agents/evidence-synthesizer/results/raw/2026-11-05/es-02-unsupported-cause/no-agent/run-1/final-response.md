**Conclusion: the sources don't support the DNS claim. The edge log contradicts it.**

**What the incident note claims** (`sources/incident-note.md`, lines 5–7)
- Checkout errored from 09:14 to 09:52.
- The root cause was a DNS failure: the checkout service could not resolve `checkout-api.internal`.
- The resolver was restarted at 09:50 and the service recovered.

**What the edge log shows** (`sources/edge-log.txt`)
- **DNS worked throughout the outage.** Every resolver lookup for `checkout-api.internal` returned `NOERROR` with 1 answer in 4–5 ms. That includes lines 4, 7, 10 and 13, which fall inside the outage window.
- **TCP worked.** Each connect to 10.4.2.17:443 succeeded (lines 5, 8, 11).
- **TLS failed.** At 09:14:02, 09:14:07 and 09:31:40 the handshake failed with `alert=certificate_expired` (lines 6, 9, 12). Before that, at 09:13:58, the handshake succeeded (line 3).
- **Recovery was a successful handshake at 09:52:03** (lines 14–15). This matches the note's end time.

**Where the evidence stops**
- The log points to an expired certificate on 10.4.2.17 as the failure mechanism. It doesn't say why the certificate expired or how it was fixed. Nothing in it shows a certificate renewal.
- The log has no entries between 09:31:40 and 09:50:12. It also has no resolver restart event. The note's 09:50 restart is therefore unverified, though the 09:50:12 lookup is consistent with it.
- The log doesn't show customer-facing errors or the checkout service's own view. It only shows the lookup, connect and handshake steps for one endpoint. The note's claim that the service "could not resolve" the name has no support in it.
- The recovery at 09:52 came after the restart at 09:50. That order may be why the note blamed DNS. But the log shows resolution was already succeeding before the restart, so the restart isn't shown to be the fix. The log doesn't establish what changed to clear the certificate error.
- Whether any DNS problem existed elsewhere, such as in the checkout service's own resolver path, isn't covered by these sources. The edge log's lookups were healthy, and nothing else here suggests a DNS fault.

CONCLUSION: UNSUPPORTED
