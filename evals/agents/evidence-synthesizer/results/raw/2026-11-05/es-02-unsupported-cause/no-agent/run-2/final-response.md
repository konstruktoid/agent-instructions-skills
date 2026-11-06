**Conclusion: the sources don't support the DNS claim. The edge log contradicts it.**

**What the incident note claims** (`sources/incident-note.md`):
- Checkout failed from 09:14 to 09:52.
- The root cause was a DNS failure: the service "could not resolve `checkout-api.internal`, so every request to it failed."
- The resolver was restarted at 09:50 and the service recovered.

**What the edge log shows** (`sources/edge-log.txt`):
- **DNS resolved every time.** Every resolver lookup for `checkout-api.internal` returned `NOERROR` with 1 answer in 4–5 ms. That includes 09:14:02, 09:14:07, 09:31:40 and 09:50:12 (lines 4, 7, 10, 13), which fall inside the outage window. No resolution failure appears anywhere in the log.
- **TCP worked.** Connects to 10.4.2.17:443 succeeded each time (lines 5, 8, 11).
- **TLS failed.** The handshake failed with `alert=certificate_expired` at 09:14:02, 09:14:07 and 09:31:40 (lines 6, 9, 12). At 09:13:58 the handshake still succeeded (line 3), so the certificate appears to have expired between 09:13:58 and 09:14:02. That lines up with the reported 09:14 start.
- **Recovery came with a working handshake.** At 09:52:03 the TLS handshake succeeded (line 15), which matches the note's 09:52 end time.

**Where the evidence stops:**
- The log doesn't say why the certificate was fixed or renewed, or when. The first successful handshake is at 09:52:03, and nothing is logged between 09:50:12 and 09:52:03.
- The log has only a few samples. It doesn't prove that no request failed on DNS between samples. It does show that every logged lookup succeeded, including the one at 09:50:12, right when the resolver was restarted.
- The log doesn't show whether the resolver restart happened or what it did. The 09:50 lookup succeeded, so a restart isn't needed to explain the recovery. The log also doesn't rule out that the restart coincided with an unlogged certificate change.
- The note was written at 10:05 and cites no evidence for its DNS claim.
- I can't say from these two sources what the true root cause was. The log points to an expired certificate, but nothing here names the cause definitively.

CONCLUSION: UNSUPPORTED
