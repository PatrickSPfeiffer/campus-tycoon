# Feature: one tournament at a time

Owner: Filippo Venturini · Branch: `tournament-pages` · Reviewer: Patrick

## Why

The Tournaments page draws every running tournament as a full card, one under the other, in
joining order. After joining a new tournament ("20") the player has to scroll past all the old
ones to find it, and every card is read from the database at each click.

## What

1. **Tournaments page:** Create a tournament and Join a tournament, then "Tournaments in
   progress": one compact row per running tournament, **newest first** (name, code, day, and
   "Playing · Ready", "Playing · Not ready" or "Organiser"), each with an "Open" button. Finished
   tournaments stay at the bottom in the closed "Finished tournaments (N)" expander, as today.
2. **One tournament page:** "Open" (or the address `?page=tournaments&tournament=<id>`) shows only
   that tournament card, with an "All tournaments" button to go back. Creating or joining a
   tournament opens it directly; the success message shows above the card.
3. Only tournaments the player joined or organises can be opened; any other id, or a value that is
   not a number, shows the Tournaments page.
4. Rules: `logic.newest_first(rows)` (by id, newest first) and
   `logic.find_tournament(rows, value)` (the row whose id is the number in `value`, else None).

## Out of scope

- Rules, `db.py`, tables, the tournament card itself.

## Done when

1. `newest_first` puts the highest id first and keeps every row.
2. `find_tournament` finds a listed id given as text or number, and returns None for an id not in
   the list, for text that is not a number, and for no value.
3. The app opens a single tournament from the address, has an "All tournaments" button and an
   "Open" button, and lists running tournaments with `newest_first`.
4. All existing tests still pass.
