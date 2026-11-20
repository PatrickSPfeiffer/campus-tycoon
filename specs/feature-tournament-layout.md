# Tournament practice-style layout

## Why

Tournament play should be as easy to follow as Practice while keeping the
tournament rules visible. Tournament sales depend on the prices set by all
players, so Practice's exact-looking `Will sell` and `Expected profit` values
must not be shown as tournament outcomes. We will hide those figures.

## What

- Restructure a player's tournament screen into these numbered sections:
  1. `Your day and money`
  2. `Plan day N`
  3. `Trade day N`
  4. `Results`
- Reuse the Practice layout for each product: supplier card, arrow, customer
  card, then `Buy stock` and `Save selling prices` buttons.
- Keep tournament-specific prices and reference prices, including weather and
  upgrade effects, in the reused layout.
- Put the Coffee machine purchase in section 1, in the position used by
  Practice for `Take a loan`.
- Make the reused layout call tournament operations only:
  `buy_tournament_stock_many`, `set_tournament_prices`, and
  `buy_tournament_upgrade`. Pass operation functions into shared rendering code
  when needed; never call the Practice operations from a tournament screen.
- In section 3, use `Ready` and organiser-only `Close day now` in place of the
  Practice `Trade day` button.
- Keep tournament status, shared-market results, ranking, refresh, and player
  readiness behavior.
- Do not include the AI advisor.

## Out of scope

- Changes to `logic.py`, `db.py`, database tables, or tournament rules.
- Changes to the Practice screen or Practice calculations.
- Adding tournament sales/profit estimates that imply an exact result.
- AI advisor support in tournaments.
- New libraries, migrations, or unrelated visual changes.

## Done when

- The tournament player screen looks like Practice with the four sections and
  supplier → arrow → customer product rows.
- `Buy stock` and `Save selling prices` work through the tournament functions.
- The Coffee machine is in section 1 in the Practice loan position.
- No exact Practice `Will sell` or `Expected profit` figures are presented for
  tournament play.
- All existing tests pass.
- The completed screen is tested by hand with two players, including buying,
  saving prices, readiness, day closing, and results.
