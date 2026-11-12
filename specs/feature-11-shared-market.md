# Feature 11: shared-market rule (M1–M3)

## Why
In a tournament all players share the same customers, so prices and stock become a real
competition: the cheapest stand sells first. This is the rule that turns the solo game into
a price war (docs/team-brief.md, "The shared market"). It is a pure function, so it needs no
database and can be built and tested before the tournament screens exist.

## What
- [ ] A new function in logic.py: `market_sales(product, stands, day)`.
      - `product`: a catalogue name (`Café`, `Croissant` or `Water`). An unknown product is rejected.
      - `stands`: a list with one entry per player in the tournament, each a dict
        `{"player": email, "seat": joining order 1, 2, 3…, "price": selling price, "stock": units}`.
      - `day`: the day being closed, 1–5.
      - It returns a dict `{player: units_sold}` with every player in it (0 if they sold nothing).
      - It does not change the `stands` list it receives, and it never reads or writes the database.
- [ ] **M1.** There are 10 customers per player: half *budget* (pay at most the reference
      price), half *premium* (pay at most twice the reference price).
- [ ] **M2.** Budget customers buy first, then premium customers. Each customer buys one unit
      from the cheapest stand they can afford that still has stock. A stand never sells more
      than its stock.
- [ ] **M3.** Stands with the same price share those customers one at a time, in turn,
      in joining order, skipping a stand that has run out of stock (so its customers go to the
      other tied stands). The turn starts with the player whose turn it is that day:
      seat 1 on day 1, seat 2 on day 2, and so on, starting again after the last seat.
      If that player is not in the tie, the next tied player in joining order starts.
      Budget and premium customers each start again from the player whose turn it is.
- [ ] With one player, the function gives exactly the practice rule: 10 units at or below
      the reference price, 5 up to twice the reference price, 0 above (limited by stock).

## Out of scope
Revenue, COGS, cash and saving results (M4: the tournament close-day feature does that with
the existing rules), connecting the rule to the tournament screens, any change to app.py, db.py
or the tables, changing the practice game.

## Done when
1. One player, Café (reference €4), stock 20: price €4.00 sells 10, €8.00 sells 5,
   €8.01 sells 0. Price €4.00 with stock 3 sells 3.
2. Team-brief example, Café, day 1: Ana (seat 1) €3.50 with 15 units, Bruno (seat 2)
   €6.00 with 10 units → Ana 15, Bruno 5.
3. Tie and rotation, Café, three players: A (seat 1) and B (seat 2) at €4.00 with 20 units,
   C (seat 3) at €9.00 with 20 units.
   Day 1 → A 16, B 14, C 0. Day 2 → A 14, B 16, C 0.
   Day 3 (C's turn, C not in the tie, so A starts) → A 16, B 14, C 0.
4. Stock runs out in a tie, Café, day 1: A (seat 1) €4.00 with 3 units, B (seat 2) €4.00
   with 20 units → A 3, B 17.
5. A player with no stock sells 0 and the customers go to the next cheapest stand.
6. An unknown product is rejected. The `stands` list is unchanged after the call.
7. All old tests pass unchanged; all tests green with `uv run pytest`, on branch
   feature-11-shared-market, pushed, pull request reviewed by a teammate.
