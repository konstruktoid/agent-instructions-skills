Files changed: `src/sessionsvc/store.py`, `README.md`. `ruff check`, `ruff format --check`, and `ty check` all pass.

Two pre-existing findings, unchanged and out of scope for this task, but worth your attention: `load_session` still runs `pickle.loads` on a client-supplied blob — that's remote code execution by design, TTL doesn't mitigate it. `read_overrides` still calls bare `eval` on stored text. Neither was part of the requested change; flagging so you can decide whether to schedule a fix.
