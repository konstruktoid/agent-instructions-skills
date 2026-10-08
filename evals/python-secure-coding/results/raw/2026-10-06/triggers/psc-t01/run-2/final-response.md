I haven't written any code yet. There are two things you should know first.

**The skill's reference files were blocked.** The security skill told me to read its coding instructions and `injection.md`, and both reads were denied for lack of permission. I haven't tried to get around that. If you grant read access to the plugin directory, I'll read them before writing anything. Otherwise I'll go ahead from general practice and say so.

**The repo doesn't have what I need to guess safely.** `src/ledger/` only has `balance.py` and `client.py`, which are plain functions. It has no web framework, no Postgres driver or config, and no table definition. These answers decide the code:

1. **Framework:** FastAPI, Flask, Django or something else? Should I add one?
2. **Driver:** psycopg 3, asyncpg, SQLAlchemy or something else? Where does the connection or pool come from?
3. **Table:** What are the table name and columns, and which CSV column maps to which?
4. **Bad rows:** Should one invalid row reject the whole upload (single transaction, all or nothing), or should valid rows be kept and bad ones reported?
5. **Access:** Who may call this? Is there an existing auth mechanism I should use?

I plan to build it with these safeguards:
- A cap on upload size and row count.
- Parsing with the standard `csv` module.
- Validation of the header and each row's types at the boundary.
- Parameterized SQL, with table and column names fixed in code and never taken from the CSV.
- Batched inserts in one transaction.
- Error responses that don't echo raw row data.
