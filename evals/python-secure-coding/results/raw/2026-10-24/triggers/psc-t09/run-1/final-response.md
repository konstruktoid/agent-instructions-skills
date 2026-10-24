I couldn't find a worker pool in this workspace, so I can't say how the GIL affects your code specifically.

**What I searched:** every file for `worker`, `thread`, `pool` and `concurren`, ignoring case. The only match was `nginx_worker_processes: auto` in `roles/nginx/defaults/main.yml:2`. That's an nginx setting for separate processes, not Python threading. The project has only two Python modules, and neither uses threads:
- `src/ledger/balance.py`: one function, `balance()`, that sums entry amounts
- `src/ledger/client.py`: `get()`, which retries a transport call up to 3 times

Is the worker pool in another repo or branch, or not committed yet? If you point me to it, I can go through it line by line.

**In the meantime, here's how the GIL usually affects a Python thread pool:**

- **One thread runs Python bytecode at a time.** In standard CPython, the Global Interpreter Lock (GIL) means threads in a `ThreadPoolExecutor` or `threading.Thread` pool take turns. CPU-heavy pure-Python work, such as summing large ledgers in a loop, won't run faster with more threads and can get slightly slower from switching overhead.
- **I/O-bound work still scales.** Threads release the GIL while they wait on sockets, files, `time.sleep` or most C extensions that release it explicitly. So a pool making network calls (like the `transport` in `client.py`) gets real concurrency.
- **The GIL doesn't make your code thread-safe.** A thread can be switched out between bytecodes, so steps like `counter += 1`, check-then-act on a dict, or read-modify-write on shared state can race. You still need a `threading.Lock`, a `queue.Queue` or thread-local state.
- **For CPU-bound work, use processes or free-threading.** `ProcessPoolExecutor` or `multiprocessing` sidestep the GIL, with the cost of pickling data between processes. Another option is the free-threaded CPython build (3.13+ with `python3.13t`, officially supported from 3.14), where the GIL can be disabled. C extensions like NumPy that release the GIL also work.
- **Switch interval.** CPython asks the running thread to release the GIL about every 5 ms (`sys.getswitchinterval()`). That can add latency when CPU-bound and I/O-bound threads share a pool.
