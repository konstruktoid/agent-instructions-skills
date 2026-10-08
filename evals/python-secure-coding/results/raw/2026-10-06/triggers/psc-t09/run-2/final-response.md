I couldn't find a worker pool in this repo, so I can't say how the GIL affects it. Here is what I checked:

- **Python files:** the repo has only `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`. None of them use `threading`, `ThreadPoolExecutor`, `concurrent.futures` or `multiprocessing`.
- **Search for "worker" and "Thread":** the only hit is `nginx_worker_processes: auto` in `roles/nginx/defaults/main.yml`. That is an nginx setting, so the GIL doesn't apply to it.
- **Other files:** `cmd/parser.go` is Go, and the rest is infrastructure config.

The worker pool may be on another branch, in a different repo, or not written yet. If you point me to the file or branch, I'll read it and explain how the GIL affects that code.

In the meantime, here is how the GIL affects thread pools in general:

- **CPU-bound work:** threads don't run Python bytecode in parallel. Only one thread holds the GIL at a time, so a pool of N threads gives roughly the throughput of one. It can be slower because of contention and context switching. Use `multiprocessing` or `ProcessPoolExecutor` instead.
- **I/O-bound work:** threads work well. The GIL is released while a thread waits on sockets, files, `time.sleep` and most C extensions that do blocking calls. HTTP calls, DB queries and similar work overlap fine.
- **Shared state:** the GIL does not make your code thread-safe. Operations like `counter += 1` or check-then-update sequences can still race. Use `queue.Queue`, `threading.Lock`, or keep the state per worker.
- **Free-threaded builds:** Python 3.13 and later offer an optional build without the GIL (PEP 703). With it, CPU-bound threads can run in parallel, but the race conditions above become more likely to show up.

`src/ledger/client.py` looks like a client, so if the pool is meant to call it, I can read that file and say whether the work is I/O-bound.
