# Feature: faster database access

Owner: Filippo Venturini · Branch: `faster-database` · Reviewer: Patrick (owner of `db.py`)

## Why

On the deployed app every click takes several seconds. Streamlit reruns `app.py` on every click,
and every `db` function opens its own connection with `open_database`, which runs the
10 `CREATE TABLE IF NOT EXISTS` statements every time. On Turso each statement is a network round
trip, so one click costs dozens of round trips (more with a tournament open). This hurts
"It works" and "UI/UX" (40% of the grade) and the live demo.

## What

- `open_database` runs `create_tables` only the first time a running app opens a database
  (one database = one `db_path`), instead of on every call.
- A local SQLite file that has no tables (new or emptied) always gets them, so tests and a deleted
  `data/game.db` keep working.
- If the first block fails, the database is not marked as ready, and the next call creates the
  tables again.
- Nothing else changes: same tables, same queries, same transactions, same error messages.
  After Patrick resets the Turso tables, the app must be rebooted (Streamlit Cloud → Reboot),
  which is already needed after every deploy.

## Out of scope

- Reusing one Turso connection across calls (riskier with several players at once).
- Changing `app.py` to read less data (separate UI task).

## Done when

1. **Once per database:** loading a game, buying, setting a price and trading on the same
   database call `create_tables` exactly once.
2. **Each database separately:** a second database path gets its own `create_tables` call.
3. **Emptied file:** deleting the local database file and loading the game again recreates the
   tables and starts a new game (no "no such table" error).
4. **Failure is not remembered:** if the first block raises an error, the next call runs
   `create_tables` again.
5. **No behaviour change:** all existing tests still pass.
