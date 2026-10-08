I couldn't find an upload validator in this repo, so I haven't written any tests.

- The Python source is only `src/ledger/balance.py` and `src/ledger/client.py`.
- A search for "upload", "extension", "max_size" and "valid" across the `.py` files returned nothing.
- The only test file is `tests/test_balance.py`, which tests `balance`.

Writing tests against a validator I can't see would mean guessing its name, its signature, the size limit, the allowed extensions and how it signals rejection (an exception type or a return value). Tests built on those guesses would either fail or check nothing real.

Could you tell me one of these?
- **Where it lives:** the file or module, if it's in another branch or directory. It may be uncommitted, since git status only shows an untracked parent directory.
- **Or the intended behavior:** if the validator doesn't exist yet and you want tests first, give me the interface and rules. These are the function name, the size limit, the allowed extensions and the rejection mechanism.

Once I have that, I'll follow the existing `tests/test_*.py` style. That means plain functions with docstrings and no new framework. I'll parametrize the bad extensions and cover the oversized case at the boundary, one byte under the limit and one byte over. Then I'll run the suite.
