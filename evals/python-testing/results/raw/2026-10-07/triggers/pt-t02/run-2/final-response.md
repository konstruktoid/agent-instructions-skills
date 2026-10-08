I can't find `parse_manifest` in this workspace, so I haven't written any tests yet. A search for the name, case-insensitive, matched nothing. The only Python files are `src/ledger/balance.py`, `src/ledger/client.py` and `tests/test_balance.py`.

The function may be on another branch or in a file that isn't committed here. I'd rather not invent a signature and write tests against it.

Can you tell me one of these?
- the file or branch that has `parse_manifest`, or
- its signature, the manifest format it parses, and how it should fail on bad input.

Once I have that, I'll read `tests/test_balance.py` for the repo's conventions and match them. Because the function is new and public, I'll cover both the valid cases and the rejection paths. Then I'll run the full suite.
