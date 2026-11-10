# Feature 7: data structure for players and tournaments

## Why
Today the database holds one game for everyone. Each player needs their own practice
game, and tournaments need tables that the teammates building them can rely on.
(Team brief, layer 1. The owner of the data structure designs every table here.)

## What
- [ ] Practice tables, each with a player column:
      players (email PRIMARY KEY, name);
      games (player PRIMARY KEY, cash, day);
      products (player, product, stock, price; PRIMARY KEY (player, product));
      results (player, day, product, units_sold, revenue, cogs, gross_profit;
      PRIMARY KEY (player, day, product)).
- [ ] Tournament tables, created but not used yet:
      tournaments (id INTEGER PRIMARY KEY, name, code UNIQUE, organiser, day);
      stands (tournament_id, player, seat, cash, ready; PRIMARY KEY (tournament_id, player),
      UNIQUE (tournament_id, seat));
      stand_products (tournament_id, player, product, stock, price;
      PRIMARY KEY (tournament_id, player, product));
      tournament_results (tournament_id, day, player, product, units_sold, revenue, cogs,
      gross_profit; PRIMARY KEY (tournament_id, day, player, product)).
      seat is the joining order (1, 2, 3…), used by rule M3 and the ranking.
- [ ] Every column in the tournament tables is NOT NULL. Types: name, code, organiser and
      player TEXT; day, seat, stock and ready INTEGER (ready is 0 or 1); cash and price REAL.
- [ ] Every practice function in logic.py takes the player (their email) and only reads or
      changes that player's rows. One player's actions never change another player's game.
- [ ] The first time a player's game is loaded, the player is added to players, with the
      part of the email before "@" as their name, and gets a new practice game.
      "@" is not required: a player without "@" gets the whole text as their name.
- [ ] A player must be non-empty text of at most 254 characters; otherwise the action is
      rejected and nothing is saved. A player that is not text (such as None or a number)
      or is only spaces is rejected too.
- [ ] Until sign-in exists (feature 8), app.py uses one fixed player, "guest".
- [ ] docs/data-model.md describes every table and column, so teammates know where things
      are stored without changing the structure.
- [ ] All database code stays in db.py. The game rules in logic.py do not change.

## Out of scope
Sign-in, creating or joining tournaments, ready / close day, ranking, the shared market,
seeing other players' games, upgrading old databases (the old Turso data is deleted by hand).

## Done when
1. New database: Ana's game starts with €100, day 1, stock 0 and reference prices,
   and Ana is in players.
2. Ana buys 10 Café (€80); Bruno's game is still €100 with no stock. Bruno sets Croissant
   to €3.50; Ana's Croissant is still €3.00.
3. Ana trades a day; Bruno is still on day 1 with no results. Bruno starts a new run;
   Ana's game and results are unchanged.
4. Restart: Ana and Bruno each get their own saved game back.
5. An empty player, or one longer than 254 characters, is rejected and nothing is saved.
6. A new database has the four tournament tables, empty. A second tournament with the
   same code, or two stands with the same seat in one tournament, is rejected by the database.
7. The existing tests, updated only to name a player, pass with exactly the same numbers.
8. All tests green, on branch feature-7-data-structure, pushed.
