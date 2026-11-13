# Feature 11 — Tournaments: ready, close day and ranking

## Why
After feature 10, players can create and join a tournament but cannot play it. This feature lets each player buy stock and set prices for the day, say they are done (Ready), lets the day close, and ranks the players after day 5, so a tournament can be played from day 1 to the end.

## What
- A player who has a stand in a tournament can buy stock and set prices for the current day on their own stand (tables stands and stand_products). The validation and the error messages are the same as the practice game: quantity is a positive whole number and the cost cannot exceed the stand's cash; price is a number, more than 0, with at most 2 decimals. It is refused after the player pressed Ready, or when the tournament is complete.
- A player presses Ready when done. After Ready, they cannot change their decisions until the day closes. Pressing Ready twice is refused with a clear message.
- The day closes automatically when the last player who joined presses Ready (every player who joined is Ready), or when the organiser presses "Close day now". Only the organiser can close a day early, and the organiser does not need to have joined the tournament. A tournament with no players cannot be closed.
- When a day closes, every stand sells with its current prices and stock, including players who are not Ready. The sale is calculated by one new function in logic.py that takes the prices and stock of every stand and returns the units sold per stand and product. For now it applies the practice rule per stand (logic.demand: 10 / 5 / 0 customers, limited by stock). Revenue, cost of goods sold (units sold times unit_cost) and gross profit are rounded with round(value, 2).
- Closing a day, in one transaction: one row per day, player and product is saved in tournament_results; each stand's cash and stock are updated; every stand becomes not Ready; tournaments.day increases by 1.
- When day 5 closes, tournaments.day becomes 6 and the tournament is complete: no buying, pricing, Ready or closing is possible any more.
- A completed tournament shows the final ranking, players ordered by overall gain = cash + leftover stock valued at unit_cost - 100, rounded to 2 decimals (the same rule as logic.final_result in the practice game). If two players have the same gain, the one with the lower seat comes first.
- A member of the tournament, or its organiser, can see the list of players in seat order with their Ready state, also after the tournament is complete. Anyone else is refused. This is a read-only function in logic.py so that app.py never reads the database.
- A player can only act on their own stand. Every refused action (unknown tournament, not a member, already Ready, completed tournament, non-organiser closing early, invalid quantity or price, not enough cash, ranking requested before the tournament is complete) shows a clear message and changes nothing in the database.
- Rules in logic.py, reading and writing in db.py (using db.open_database), screens in app.py. No table is changed.

## Out of scope
- The shared market rule: until it exists, each stand sells with the practice rule. It is another feature.
- Changing the practice game or its functions (buy, set_price, trade_day, final_result stay as they are).
- Weather, upgrades, loans, charts, the CSV report and the UI polish.
- Undoing Ready, leaving or deleting a tournament, removing players, a time limit for the day.
- Any change to the tables.

## Done when
- New tests in tests/test_feature_11.py cover: buying and setting a price on a tournament stand (accepted, invalid, not enough cash), Ready accepted, Ready twice refused, buying or pricing after Ready refused, action by a non-member refused, closing when all are Ready, organiser closing early, non-organiser closing early refused, closing with no players refused, a non-Ready player still selling at close, results rows saved per day, player and product, cash, stock and ready updated, day moving from 1 to 6, closing a completed tournament refused, ranking order including a tie, and every refused action leaving the database unchanged.
- All tests pass with `uv run pytest`, old and new, and the old tests were not modified.
- In the app, I can buy, set prices, press Ready, see who is Ready, close a day as organiser, and see the ranking after day 5.
- The diff only touches logic.py, db.py, app.py, tests and this spec. No table changed.
- The PR passes the GitHub check and is reviewed by a teammate.
