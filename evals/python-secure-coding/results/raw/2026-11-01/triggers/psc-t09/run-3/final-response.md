I couldn't find a worker pool in this workspace, so I can't explain how the GIL affects *your* code yet.

**What I searched:** every file for `threading`, `ThreadPoolExecutor`, `concurrent.futures`, `multiprocessing`, `worker`, `pool`, `thread`, `lock`, `async` and `queue`. There are only two Python modules, `src/ledger/balance.py` and `src/ledger/client.py`, plus `tests/test_balance.py`, and none of them match. The only hit for "worker" anywhere is `nginx_worker_processes: auto` in `roles/nginx/defaults/main.yml:2`. That's an Nginx setting, not Python. The worker pool may be in another repo or branch, or it may not have been committed yet.

**How the GIL generally affects a thread-based pool:**

- **CPU-bound tasks don't run in parallel.** In standard CPython, only one thread runs Python bytecode at a time. A `ThreadPoolExecutor` doing hashing, parsing or number-crunching in pure Python will be about as fast as running the tasks one after another, or slower because of switching overhead. For that kind of work, use `ProcessPoolExecutor`/`multiprocessing`, or C extensions that release the GIL (NumPy, hashlib on large buffers).
- **I/O-bound tasks do benefit.** Threads release the GIL while they wait on sockets, files, `time.sleep` or database calls. A pool of threads making HTTP or DB requests overlaps that waiting time and scales well.
- **The GIL doesn't make your code thread-safe.** It protects the interpreter's own internals, not your logic. Steps like `counter += 1`, check-then-set, or reading and then updating a shared dict can still interleave between threads. You still need `threading.Lock`, `queue.Queue`, or to avoid sharing state at all. This matters most for anything like balance updates.
- **Free-threaded Python (3.13t/3.14t)** can turn the GIL off. CPU-bound threads then really do run in parallel, and races that rarely showed up before become much more likely. Code that leaned on the GIL to hide those races will break more often.

If you point me to the pool (a file path, branch or repo), I can go through its actual locking, task types and shared state. One thing I can check here: whether `src/ledger/client.py` or `balance.py` are called from threads somewhere else. If so, I can look for shared mutable state in them.
