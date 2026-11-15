# Feature: difficulty levels (practice mode)

Owner: Filippo Venturini · Branch: `feature-difficulty-levels`

## Why

A practice run is always the same today. Choosing Easy / Normal / Hard gives players a reason
to play again and makes practice useful before a tournament (Scope).

## What

- `logic.DIFFICULTY_LEVELS = {"Easy": 150.0, "Normal": 100.0, "Hard": 70.0}` (starting cash).
- `logic.new_run(db_path, player, level="Normal")` starts a run with that level's cash,
  no stock, reference prices, day 1, empty history. An unknown level raises ValueError and
  nothing changes.
- A player's very first game is Normal, exactly as today.
- The level is chosen only when starting a new run; it cannot change during a run.
- The final result uses the run's own starting cash (CT R4 with the chosen start):
  gain = final cash + remaining stock at purchase cost − starting cash.
- app.py: a level selector next to "Start a new run"; the current level is shown next to Progress.
- **Database change, approved by Patrick (owner of the data structure) on 12 Nov:**
  `games.start_cash REAL NOT NULL DEFAULT 100.0`, added in this PR to `create_tables` and
  `docs/data-model.md`. Patrick adds the column to the live Turso database before the merge;
  after the merge everyone deletes their local `data/game.db`.

## Out of scope

- Tournaments: every stand still starts with €100 (same conditions for everyone).
- Other differences between levels (prices, costs, demand).
- Upgrading old databases (we reset the data, as AGENTS.md says).

## Done when

1. **Easy:** `new_run(..., "Easy")` → cash 150.00, day 1, stock 0, empty history.
2. **Hard:** `new_run(..., "Hard")` → cash 70.00.
3. **Normal unchanged:** a first game and `new_run(...)` without a level start at 100.00; all existing tests still pass.
4. **Rejected:** `new_run(..., "Impossible")` raises ValueError; cash, day, stock and history are unchanged.
5. **Gain uses the start:** Easy run, buy 10 Café (€20), trade 5 days at €4 → final cash 170.00,
   stock at cost 0.00, gain **20.00** (not 70.00).
6. **Restart:** reopening the database keeps the level's start cash and gives the same final result;
   the value is stored in `games.start_cash`.
7. **Tournament unchanged:** joining a tournament during an Easy practice run still gives a stand with €100.00.

Check: `uv run pytest` is green, also in GitHub Actions on the pull request.
