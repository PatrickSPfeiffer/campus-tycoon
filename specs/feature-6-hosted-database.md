# Feature 6: hosted database

## Why
The deployed app restarts after every merge and when it sleeps, and SQLite on its
temporary disk loses everything. Tournaments need data that persists and is shared
by all players. (Team brief, layer 1.)

## What
- [ ] When the secrets TURSO_DATABASE_URL and TURSO_AUTH_TOKEN are available,
      db.py stores all data in that Turso database. Otherwise it uses the local SQLite
      file data/game.db, as today.
- [ ] The secrets are read with st.secrets or environment variables, never written in the code.
- [ ] All database code stays in db.py. app.py only catches the "database unavailable" error and shows it with st.error. Adding the library changes pyproject.toml and uv.lock. The tables, the SQL and logic.py stay the same.
- [ ] The library is Turso's sqlite3-compatible Python package (libsql), added with uv
      and pinned in uv.lock.
- [ ] If the Turso database cannot be reached, the app shows a clear message saying the
      database is unavailable, instead of a crash.
- [ ] Tests never connect to Turso: they keep using a temporary local SQLite database.
- [ ] With only one of the two settings, db.py raises the "database unavailable" error.
      An empty value counts as missing.
- [ ] Environment variables are read first, then st.secrets.
- [ ] Any exception while connecting to Turso becomes the "database unavailable" error.
      Only connecting is wrapped, so other bugs are not hidden.
- [ ] While connecting, any exception becomes the "database unavailable" error. During a
      save, only libsql's network error becomes the "database unavailable" error, and the
      action saves nothing; other errors during a save are not caught.
- [ ] If libsql reads rows differently from sqlite3, only the row-reading code in db.py
      changes; the SQL stays the same.
- [ ] The message never shows the Turso URL or the token.
- [ ] The quick check right after connecting counts as part of connecting.
- [ ] .streamlit/secrets.example.toml lists the two secret names with placeholder values, so teammates know which secrets exist. Teammates without the secrets use local SQLite.

## Out of scope
Sign-in and player accounts, new tables or columns, moving old local data to Turso,
a separate database for development, offline mode or local copies of the remote database.

## Done when
1. The 21 existing tests pass unchanged.
2. Choosing the database: with no Turso settings, db.py picks the local file; with both
   settings, it picks Turso. (Tested with fake settings, without connecting.)
3. A failed Turso connection raises a clear "database unavailable" error that the app
   can show. (Tested with a fake connection that fails.)
4. By hand, on the laptop with the secrets: buy, set a price, trade a day, stop the app,
   start it again: everything is kept, and the Turso dashboard shows the tables.
5. By hand, on the deployed app after the merge: play a day, reboot the app from
   Streamlit (Manage app → Reboot app): everything is kept.
6. All tests green, on branch feature-6-hosted-database, pushed.
