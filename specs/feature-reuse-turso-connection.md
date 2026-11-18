# Feature: reuse the Turso connection during a click

Owner: Filippo Venturini · Branch: `reuse-turso-connection` · Reviewer: Patrick (owner of `db.py`)

## Why

Even after "create tables once" (PR #36), one click on the live app can take a minute. Every
`db` function opens a **new** Turso connection (network handshake + `SELECT 1` check) and closes
it. One click runs about 70 of them, and more for every tournament the player joined
(each tournament reads weather, status, upgrades and stands, and the stand list is read again
for every tournament). Opening the connection is the slow part.

## What

- When the app uses Turso, `open_database` reuses the same connection for all the calls of one
  click, instead of opening a new one each time.
- One connection per Streamlit thread (each player's script run has its own), so two players
  never share a connection.
- A connection unused for more than `REUSE_SECONDS` (5 s) is closed and a fresh one is opened, so a
  click never starts on a connection that Turso may have dropped while the player was idle.
- After a network error the connection is closed and forgotten; the next call opens a new one.
  The player still sees "Database unavailable", as today.
- Local SQLite (laptops and tests) is unchanged: a new connection per call.
- Same tables, queries, transactions and error messages.

## Out of scope

- Changing `app.py` to read less data (separate UI task).
- Sharing one connection between players.

## Done when

1. **One connection per click:** loading, buying, setting a price, trading and reading results in
   the same thread open one Turso connection, and the result is correct (cash €120.00).
2. **Idle connection is replaced:** after more than `REUSE_SECONDS` without use, the next call
   opens a new connection and closes the old one.
3. **Network error:** a "Hrana: `http error" during a call raises `DatabaseUnavailable`, closes that
   connection, and the next call opens a new one that works.
4. **Each thread separately:** a call from another thread opens its own connection.
5. **Local unchanged:** with local SQLite every call still opens and closes its own connection.
6. **No behaviour change:** all existing tests still pass.
