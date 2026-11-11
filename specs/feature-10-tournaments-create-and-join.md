# Feature 10 – Tournaments: create and join

## Why
Players can only play the practice game alone. This feature lets a group play together: one person creates a tournament and the others join it with a code. It is also the base for the next tournament features (ready, closing a day, leaderboard), which cannot start until tournaments and stands exist.

## What
- A signed-in player creates a tournament with a name (trimmed, not empty, max 40 characters). The tournament starts at day 1 and gets a random 6-character code (uppercase letters and digits), unique across tournaments.
- Creating a tournament does not join it: the organiser joins with the code like everyone else.
- A player joins by entering the code. Lowercase and spaces around the code are accepted.
- Each player who joins gets a stand: seat in join order (1, 2, 3...), €100.00 cash, not ready, and one row per product in `PRODUCTS` with stock 0 and price equal to its reference price.
- A join is refused, with a clear message and no change to the database, when: the code does not exist, the tournament is past day 1, or the player has already joined.
- Rules in logic.py, reading and writing in db.py (the join is one transaction), screens in app.py. No table is changed.

## Out of scope
- Playing the tournament: buying stock, setting prices, ready, closing a day, the shared market rule and the leaderboard. These are separate features.
- Leaving a tournament, deleting a tournament, or the organiser removing players.
- A maximum number of players.
- Keeping a separate reference price per stand: the catalogue in `PRODUCTS` stays the source of truth.
- Testing simultaneous joins. The transaction protects them, but this is a known limit.
- Any change to the tables.

## Done when
- New tests cover: creating a tournament (day 1, valid unique code), invalid names, joining with seat 1, 2, 3, the exact starting stand (€100.00, not ready, 3 products with stock 0 and reference price), lowercase and spaced code accepted, and the three refusals leaving the database unchanged.
- All tests pass with `uv run pytest`, old and new, and the old tests were not modified.
- In the app, I can create a tournament, see its code, join it with that code from my account, and see my stand.
- Entering a wrong code shows a clear error and nothing is saved.
- The diff only touches logic.py, db.py, app.py, tests and this spec. No table changed.
- The PR passes the GitHub check and is reviewed by a teammate.
