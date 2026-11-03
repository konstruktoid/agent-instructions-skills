I couldn't find a worker pool in this repo, so I can't tell you how the GIL affects your specific code. There's no Python code here that uses `threading`, `concurrent.futures`, `multiprocessing` or a pool of any kind. The only Python is:

- `src/ledger/client.py`: a synchronous `get()` that calls a `transport` up to 3 times.
- `src/ledger/balance.py`: a `sum()` over ledger entries.
- `tests/test_balance.py`

The rest of the repo is Go, Terraform, Ansible, CI configs and a shell script. The pool may be in another repo or branch. If you point me to it, I can go through it line by line.

Here's how the GIL usually affects a threaded worker pool in CPython:

**What the GIL does**
- Only one thread runs Python bytecode at a time in a process. The running thread gives up the GIL every 5 ms by default (`sys.setswitchinterval`) and whenever it blocks.
- Blocking I/O releases the GIL: socket reads, file I/O, `time.sleep`, most C extensions that wait on the network. So does a lot of numpy, hashlib, zlib and similar C code.

**What that means for a `ThreadPoolExecutor`-style pool**
- **I/O-bound jobs** (HTTP calls, DB queries, something like `transport(path)` in `client.py`): threads work well. While one thread waits on the network, the others run, so throughput goes up roughly with pool size until the remote side or connection limits become the bottleneck.
- **CPU-bound pure-Python jobs** (e.g. running `balance()` over big lists): threads don't give you parallelism. You get about single-core throughput, sometimes a bit less because threads compete for the GIL. Use `ProcessPoolExecutor`, push the hot loop into C or numpy, or use a free-threaded build.
- **Free-threaded CPython (3.13t / 3.14t, PEP 703)**: with the GIL disabled, CPU-bound threads do run in parallel. Your C extensions need to support it, and single-threaded code runs a bit slower.

**What the GIL does not do**
- It doesn't make your code thread-safe. It only keeps the interpreter's internal state consistent. A thread switch can happen between bytecodes, so compound operations like `counter += 1`, check-then-set on a dict, or appending and then reading a shared list can race. Protect shared state with `threading.Lock`, or have workers return results instead of mutating shared objects.
- Single operations on built-ins (`list.append`, `dict[k] = v`) are effectively atomic in standard CPython. That's an implementation detail, and free-threaded builds don't guarantee it the same way.

Quick check for your pool: if per-job wall time stays flat as you add threads but CPU sits at about 100% of one core, you're GIL-bound and should switch to processes.
