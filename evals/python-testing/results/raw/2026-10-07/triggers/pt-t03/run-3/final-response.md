I didn't write any tests, because I couldn't find an upload validator in this repository.

- **What the repo contains:** the Python source is `src/ledger/balance.py` and `src/ledger/client.py`. The only test file is `tests/test_balance.py`.
- **What I searched for:** I searched every file for "upload", "validat", "extension" and "max_size" and got no matches.

I don't want to guess at the validator's interface, such as its function name, size limit, allowed extensions, or whether it raises or returns an error. Tests built on a guess would probably fail against the real code or check the wrong behaviour.

Could you tell me one of these?
- The file or module where the validator lives. It may be on another branch or in another repo, since I'm on `eval-harness-delegation`.
- Or, if it doesn't exist yet, the rules you want it to enforce. I can write the validator and its tests together.

Once I can see it, I'll read `tests/test_balance.py` and match its style. Then I'll add rejection tests for oversized files, bad extensions, and any other failure paths the code has. I'll run the full suite and `ruff` and `ty` on the new test file.
