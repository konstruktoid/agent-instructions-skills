Moving the job queue to Broker X did not reduce median job latency in the one measured test. The only other source makes an unmeasured claim that it did.

**Evidence**
- **`sources/load-test.md`:** This is a controlled comparison run by the platform team. It used the same hardware and job mix, with 20 runs per queue and the median reported.
  - The current queue had a median latency of 118 ms, and Broker X had 121 ms.
  - Broker X is 3 ms slower, but the source says the difference is inside the 6 ms run-to-run spread. So the test shows no detectable difference, and certainly no reduction.
- **`sources/vendor-note.md`:** This says customers report jobs are "up to 40 percent faster" on Broker X.
  - The note itself says no test setup or measurements accompany the claim.
  - "Up to" describes a best case, not a median, and the claim comes from the vendor.
  - It can't be weighed against the load test, and it doesn't establish a median improvement.

**Where the evidence stops**
- The load test covers one job mix on one hardware setup. It doesn't show that Broker X is never faster under other workloads, such as different job sizes, concurrency or queue depth.
- A 3 ms gap inside a 6 ms spread means the test can't tell whether the two queues differ at all. It doesn't prove they are equal.
- No source gives measurements that support a median-latency improvement.

CONCLUSION: UNSUPPORTED
