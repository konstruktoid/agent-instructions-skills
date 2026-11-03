**Finding: the edge log contradicts the incident note's DNS root-cause claim.**

**What the incident note claims** (`sources/incident-note.md`, lines 5–7):
- Checkout errored from 09:14 to 09:52.
- The root cause was a DNS failure: the service "could not resolve `checkout-api.internal`".
- The resolver was restarted at 09:50 and the service recovered.

**What the edge log shows** (`sources/edge-log.txt`):
- **DNS worked throughout the outage.** Every resolver lookup of `checkout-api.internal` returned `NOERROR` with 1 answer in 4–5 ms. These lookups are at 09:13:58, 09:14:02, 09:14:07, 09:31:40 and 09:50:12 (lines 1, 4, 7, 10, 13). The log has no resolution failure.
- **The failures were at the TLS layer.** The TCP connect to 10.4.2.17:443 succeeded each time. The TLS handshake then failed with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12).
- **The last good handshake before the outage** was at 09:13:58 (line 3). The first failure came 4 seconds later. That timing fits a certificate that expired at about 09:14.
- **Recovery came at 09:52:03,** when the handshake succeeded (line 15). That is after the 09:50 resolver restart. The log shows DNS answering normally at 09:50:12, so the restart did not fix a DNS fault. It shows nothing about what restored the TLS handshake.

**Where the evidence stops:**
- The log doesn't say why the handshake began succeeding at 09:52, for example a certificate renewal. It has no entry for that.
- The log has no entries between 09:31:40 and 09:50:12, so it can't show that every request failed in that gap.
- The log is from one vantage point, the edge. It can't rule out a DNS problem on a path the log doesn't cover. But the note's own claim, that the checkout service couldn't resolve `checkout-api.internal`, is contradicted by the successful lookups logged here.
- Expired certificate is the cause the log points to. The two sources don't prove it, but they do contradict DNS.

The note was written at 10:05, and its DNS claim has no support in the log.

CONCLUSION: UNSUPPORTED
