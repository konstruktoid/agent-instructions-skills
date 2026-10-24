I couldn't find a worker pool in this repo, so there's no threading code here to explain.

**What I searched:**
- Python files using `threading`, `ThreadPoolExecutor`, `concurrent.futures` or `Thread(`: no matches.
- Files with "worker" in the name: none.
- The Python code is just two small modules, and neither one uses concurrency:
  - `src/ledger/balance.py:4`: `balance()` adds up entry amounts for one account in a single synchronous pass.
  - `src/ledger/client.py:6`: `get()` calls a transport up to 3 times and stops at the first result that isn't `None`. It has no threads and no backoff.

The rest of the repo is infrastructure (Terraform, k8s, Ansible, CI configs) plus one Go file, `cmd/parser.go`, which the GIL doesn't affect.

**How the GIL would affect a worker pool, in case it helps:**
- **CPU-bound work** (like `balance()` over a large list) doesn't run in parallel across threads on standard CPython. Only one thread runs Python bytecode at a time, so a thread pool adds overhead and no speedup. Use `ProcessPoolExecutor` or multiprocessing instead.
- **I/O-bound work** (like the network calls `client.get()` presumably makes through `transport`) does benefit from threads. Blocking I/O releases the GIL, so other threads can run while one waits.
- **The GIL doesn't make your code thread-safe.** Compound operations like `x += 1` or check-then-set on a shared dict can still interleave between threads. You still need `threading.Lock` or a `queue.Queue` around shared state.
- **Free-threaded CPython** (3.13t and later, built without the GIL) removes that limit, so CPU-bound threads can run in parallel. It also makes missing locks much more likely to cause real bugs.

If the worker pool is in another repo or branch, or hasn't been committed yet, point me to it and I'll go through how the GIL affects that code specifically.
