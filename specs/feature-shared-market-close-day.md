# Shared market at day close

## Why
market_sales (specs/feature-11-shared-market.md) decides each stand's sales when all players
share the same customers, but closing a tournament day still uses the old per-stand rule
(tournament_units_sold): every stand sells as if it were alone. This feature makes the
tournament a real price war: the day close uses the shared-market rule (team brief, M1–M3).

## What
- [ ] A new function in logic.py: `tournament_market_sales(stands, day)`. `stands` is what
      db.get_tournament_stands returns ({player: {"player", "seat", "stock": {product: units},
      "price": {product: price}, ...}}). For each product in PRODUCTS it calls market_sales with
      one entry per stand ({"player", "seat", "price", "stock"} for that product) and the day.
      It returns {player: {product: units_sold}}, the same shape as tournament_units_sold.
- [ ] `_close_tournament_day` uses `tournament_market_sales(stands, day)` instead of
      `tournament_units_sold(stands)`. Revenue, COGS, cash and stock stay as today (M4).
- [ ] A stand that carries an optional "reference" per product is out of scope here: the
      upgrades feature adds it. Without it market_sales uses the catalogue reference price.

## Out of scope
Removing tournament_units_sold or its tests, upgrades, screens (app.py), database or table changes.

## Done when
1. Team-brief example through a real day close: two players, Café, day 1. Ana (seat 1) €3.50
   with 15 units, Bruno (seat 2) €6.00 with 10 units, no other stock. After the organiser closes
   the day: Ana sold 15 (revenue €52.50, cash €152.50, stock 0), Bruno sold 5 (revenue €30.00,
   cash €130.00, stock 5).
2. Undercutting: Ana €3.90 with 20 Café, Bruno €4.00 with 20 Café, day 1 → Ana sells 20,
   Bruno 0 (the old rule gave 10 each).
3. The tournament day sets the turn: A (seat 1) and B (seat 2) at €4.00 with 20 Café,
   C (seat 3) at €9.00 with 20 Café. Closing day 1 → A 16, B 14, C 0. With the tournament
   set to day 2 before closing (same stock) → A 14, B 16, C 0.
4. tournament_market_sales returns every player and every product (0 when nothing is sold).
5. All existing tests pass unchanged (the close-day tests in tests/test_feature_11.py give
   the same numbers with the shared market).
6. On branch feature-shared-market-close-day, pushed, pull request reviewed by a teammate.
