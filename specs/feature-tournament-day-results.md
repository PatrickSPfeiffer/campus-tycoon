# Feature: tournament day results and Refresh

Owner: Filippo Venturini · Branch: `tournament-day-results` · Reviewer: Patrick (new read function in `db.py`)

## Why

The team brief ("What players see") says that after each day every player sees **every stand's
price and units sold per product**, and that a **Refresh** button is enough to follow the other
players. Today:

- after a day closes, only the organiser who pressed "Close day now" sees a short table, with
  only their own sales; the other players see nothing about the market;
- when the last player presses Ready the day closes, but they only see "You are Ready.";
- there is no Refresh button, so a player waiting for the others has to click something else to
  see who is ready or whether the day moved on.

The prices and units of each closed day are already saved in `tournament_results`.

## What

1. `db.get_tournament_results(db_path, tournament_id)`: one read of the saved results with each
   player's seat, ordered by day, seat and product. Read only; no table changes.
2. `logic.tournament_screen` also returns `days`: one entry per closed day, oldest first, each
   with every stand (in seat order) and, per product, the price and the units sold. It shows no
   stock and no cash of the other players. `days` is empty before the first day closes.
   `tournament_screen` still runs at most 5 statements.
3. Each tournament card shows:
   - **Market results:** the last closed day as a table (one row per player, price and units
     sold per product; the player's own row is marked "(you)"); earlier days in a closed
     "Earlier days" expander.
   - a **Refresh** button in the card header that reloads only that card.
4. When the player's Ready closes the day (everyone is ready), they see the same "Day N closed"
   box as the organiser who closes the day early.

## Out of scope

- Live updates without a click (the brief says a Refresh button is enough).
- Showing other players' cash, stock or upgrades.
- Table changes.

## Done when

1. **Results after a day:** after day 1 closes, `tournament_screen(...)["days"]` has day 1 with
   every stand's price and units sold for each product, matching the market rule.
2. **Order:** after two closed days, the days are oldest first and the stands are in seat order.
3. **Nothing before day 1 closes:** `days` is an empty list.
4. **No private data:** a stand in `days` has only player, name, price and units sold.
5. **Still few reads:** with saved results, `tournament_screen` runs at most 5 statements.
6. **Screen:** the tournament card has a Refresh button, and the Ready button shows the closed
   day when it closes it.
7. **No behaviour change:** all existing tests still pass.
