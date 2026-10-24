I couldn't find a worker pool in this repo. There are only three Python files, and none of them use threads:

- `src/ledger/client.py`: `get()` makes a transport call and retries it up to `MAX_ATTEMPTS = 3` times, all on one thread.
- `src/ledger/balance.py`: `balance()` adds up entry amounts for one account.
- `tests/test_balance.py`: tests for `balance()`.

I searched for `threading`, `ThreadPoolExecutor`, `concurrent.futures` and `multiprocessing` and got no matches. The pool might be in another repo or branch, or not committed yet. If you tell me where it is, I'll go through that code.

Until then, here's how the GIL usually affects a thread-based pool:

- **Work that waits on I/O (network, disk, sockets) runs well in parallel.** CPython releases the GIL while a thread waits on I/O, so threads overlap. If `client.get()` were run from a pool, its transport calls would speed up roughly in line with the number of threads.
- **Pure-Python CPU work does not run in parallel.** Only one thread executes Python bytecode at a time. Something like `balance()` over a large list would get no faster with more threads, and could get slightly slower from the switching between threads. Use `ProcessPoolExecutor` for this kind of work. NumPy and similar libraries are an exception because they release the GIL inside their C code.
- **The GIL does not make your code thread-safe.** It only keeps the interpreter's own internals consistent. Steps like `counter += 1`, check-then-set on a dict, or "read the balance, then write it back" can still be interrupted partway. Shared mutable state still needs a `threading.Lock` or a `queue.Queue`.
- **Free-threaded builds (3.13t and later) remove the GIL.** On those builds, CPU-bound threads really do run in parallel. Any race condition the GIL happened to hide becomes much more likely to show up, so code that relied on it can break.
