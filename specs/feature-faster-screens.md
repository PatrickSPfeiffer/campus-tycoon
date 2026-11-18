# Feature: faster screens

Owner: Filippo Venturini · Branch: `faster-screens` · Reviewer: any team member

## Why

After #36 and #37 the database part of a click is much cheaper, but a click on the live app still
waits several seconds. Streamlit reruns the whole of `app.py` on every click, and also when the
player only changes a product in a menu or a number in a field:

- all three tabs run, so a click in Practice also reads every tournament;
- every tournament card reads the database about 11 times, plus once more for every tournament
  the player joined (the card reads the whole list of stands again);
- buying or setting a price needs a click to choose the product and another to confirm, and each
  of them is a full rerun.

On Turso each read is a network round trip, so the waiting grows with every tournament joined.

## What

1. **Only the open tab runs.** The tabs track which one is open (`on_change="rerun"`), and only
   the content of the open tab is built.
2. **A click reruns only its own area.** The Practice screen and each tournament card are
   `st.fragment`s. Their buttons rerun only that fragment (`st.rerun(scope="fragment")`).
   The practice status numbers (Cash, Progress, Loan) move into the Practice screen, so they
   stay correct.
3. **Forms instead of live fields.** Buying and setting prices use `st.form`: one field per
   product, one button. Typing in a field does not rerun anything.
   - `logic.buy_many(db_path, player, quantities)` and
     `logic.buy_tournament_stock_many(db_path, player, tournament_id, quantities)` buy several
     products at once. `quantities` maps product → units; 0 means "not this product".
   - `logic.set_prices(db_path, player, prices)` and
     `logic.set_tournament_prices(db_path, player, tournament_id, prices)` set several prices at
     once. `prices` maps product → price.
   - The same checks as the single-product functions apply, to every product, **before anything
     is saved**: if one product is refused, nothing changes. A buy with every quantity at 0 is
     refused with "Choose a quantity of at least 1 for one product.". The total cost of all the
     products is compared with the cash.
4. **One read per tournament card instead of eleven.**
   `logic.tournament_screen(db_path, player, tournament_id, fetch)` returns everything a card
   shows: name, code, organiser, day, weather, the player's cash, stock and prices, the players
   and who is ready, the player's upgrades and, when the tournament is complete, the ranking.
   It runs at most 5 database statements, whatever the number of players or of tournaments
   joined. `logic.my_tournaments(db_path, player)` lists the player's tournaments with one
   statement.
5. Same rules, tables, messages and access checks as today. The old single-product functions
   stay (tests and other code use them).

## Out of scope

- New screens or new information (tournament day results, Refresh button: separate feature).
- Moving or restyling cards beyond what the forms need (separate UI feature).
- Changes to `db.py` or to the tables.

## Done when

1. **Buy many (practice):** buying 10 Café and 5 Water at once costs €22.50 and saves the stock;
   0 for a product leaves it unchanged.
2. **Buy many refused:** all quantities 0, a negative or non-whole quantity, an unknown product,
   a total above the cash, or a complete run are refused, and nothing changes.
3. **Set prices (practice):** several prices are saved at once; one invalid price (0, 3 decimals,
   above €1000) refuses all of them.
4. **Tournament buy and prices:** the same as 1–3 for a tournament stand, plus the existing
   refusals: not a member, already Ready, tournament complete.
5. **Tournament screen:** returns the same day, cash, stock, prices, players, ready flags,
   upgrades and ranking as the old functions; refuses a player who has not joined.
6. **Few reads:** `tournament_screen` runs at most 5 statements, also for a player who joined 5
   tournaments; `my_tournaments` runs 1.
7. **Lazy screens:** `app.py` builds tabs with `on_change="rerun"`, and the Practice screen and
   the tournament card are `st.fragment`s.
8. **No behaviour change:** all existing tests still pass.
