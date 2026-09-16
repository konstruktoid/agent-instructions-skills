`business_days_between` is added and wired up. Files changed:

- `src/tempo/calendar.py` — added `business_days_between(start, end)`, built on the existing `is_weekend`/`is_holiday` helpers. Also fixed `is_holiday`, which compared a `date` object directly against the `HOLIDAYS` list of ISO strings and so never matched anything — a latent bug that would've made the new function's holiday exclusion silently inert.
- `src/tempo/__init__.py` — exported `business_days_between` alongside the other helpers.
- `tests/test_calendar.py` — added coverage for `is_holiday` (confirming the fix) and `business_days_between` (weekend/holiday skipping, start-date inclusion/exclusion, `end <= start` returning 0), matching the file's existing parametrize/docstring style.

Verification: `uv run pytest` (13 passed), `uv run ruff check .` and `ruff format --check .` (clean). I confirmed the two new tests fail against the unfixed `is_holiday` before reapplying the fix. `ty check` was not usable as a gate here — it's a pre-existing issue unrelated to this change: run bare, it walks up past this nested workspace into the parent monorepo and reports unrelated errors there; scoped to `src tests`, it fails to resolve the `tempo` import even on the unmodified baseline, since nothing in this repo configures `[tool.ty]`'s src root. The README only documents `pytest` as the check, which passes.

You'll want to `/clear` before starting anything unrelated.
