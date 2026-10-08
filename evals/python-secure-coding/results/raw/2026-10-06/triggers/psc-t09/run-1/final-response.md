I couldn't find a worker pool in this repo, so I can't say how the GIL affects it. I searched for `threading`, `ThreadPoolExecutor`, `concurrent.futures`, `multiprocessing`, `queue.Queue`, and for "thread", "worker", "pool", "async", "Lock" and "executor". None of them match any file. The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. The rest of the repo is CI, Docker, Kubernetes, Terraform, Ansible, a shell script and one Go file (`cmd/parser.go`).

The worker pool may be on another branch, in a different repo, or not written yet. If you point me to the file or branch, I'll read it and explain how the GIL affects that code.

In the meantime, here is how the GIL affects a Python thread pool in general:

- **CPU-bound work gets no speedup.** Only one thread runs Python bytecode at a time. Adding threads to a pool doing parsing, hashing, number crunching or similar work won't use more cores. It often runs slightly slower because of contention and context switching. Use `ProcessPoolExecutor` or `multiprocessing` for that kind of work.
- **I/O-bound work does benefit.** Threads release the GIL while blocked on network calls, disk reads, `time.sleep`, and in many C extensions such as hashing and compression. A pool that makes HTTP calls or database queries can run those waits concurrently, which is the case threads suit.
- **The GIL doesn't make your code thread-safe.** A thread can be switched out between bytecodes, so `counter += 1` and check-then-act patterns on shared state still race. You still need `threading.Lock`, `queue.Queue` or similar.
- **Free-threaded builds change this.** Python 3.13 and later offer an optional no-GIL build (PEP 703). On it, CPU-bound threads can run in parallel, but unsynchronized shared state matters even more. Which build you have depends on the interpreter, so check before relying on either behavior.
