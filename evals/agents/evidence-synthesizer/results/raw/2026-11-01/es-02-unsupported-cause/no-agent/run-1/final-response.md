The sources don't support the note's claim. The edge log contradicts it.

**What the incident note says** (`sources/incident-note.md`)
- Checkout returned errors from 09:14 to 09:52.
- The note gives the root cause as a DNS failure: the checkout service "could not resolve `checkout-api.internal`".
- It says the resolver was restarted at 09:50 and the service recovered.

**What the edge log shows** (`sources/edge-log.txt`)
- **DNS worked throughout.** Every resolver lookup of `checkout-api.internal` returned `NOERROR` with 1 answer in 4–5 ms (lines 1, 4, 7, 10, 13). That includes the lookups at 09:14:02, 09:14:07 and 09:31:40, which fall inside the outage window. No lookup failed.
- **The TCP connection worked.** Every connect to 10.4.2.17:443 succeeded (lines 2, 5, 8, 11, 14).
- **The failure was in the TLS handshake.** Starting at 09:14:02Z, the handshake failed with `alert=certificate_expired` (lines 6, 9, 12). The handshake at 09:13:58 was fine (line 3).
- **Recovery came with a successful handshake.** The handshake succeeded at 09:52:03 (line 15), which matches the note's end of outage at 09:52.

**Reconciling the two**
- The log supports the note's timing, including the 09:14 start and the 09:52 recovery.
- It doesn't support the DNS cause. Name resolution succeeded in every sample, and the failures match an expired certificate on the endpoint.
- The note's "resolver was restarted at 09:50" has no corroboration in the log. The only 09:50 entry is a normal successful lookup (line 13). The log doesn't show a restart or any change in resolver behaviour. It also doesn't show what happened to the certificate between 09:31 and 09:52, such as a renewal.

**Where the evidence stops**
- The log is a sample of 15 lines. It has no entries between 09:31:40 and 09:50:12, and it has no application-side or customer-facing error records.
- It doesn't say whether the certificate expiry was the root cause or a symptom of something else, and it doesn't say what fixed it.
- The sources do show that DNS resolution was not failing at the sampled times, so they give no evidence for the note's stated cause.

CONCLUSION: UNSUPPORTED
