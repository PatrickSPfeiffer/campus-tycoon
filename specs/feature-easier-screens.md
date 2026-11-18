# Feature: easier screens

Owner: Filippo Venturini · Branch: `easier-screens` · Reviewer: Edoardo (UI/UX polish owner)

## Why

Testing the live app as a new player showed where people get stuck:

- Practice shows Selling prices, Loan and Buy side by side, in that order, although a day is
  played as buy → price → trade. The loan, an optional extra, gets as much space as buying.
- "Trade one day" can be pressed with no stock, or with prices that sell nothing, and the player
  only finds out from the result.
- In tournaments, the reference price of a product changes with the weather and with the Coffee
  machine, but the card shows neither, so a player cannot tell which price still sells.
- Finished tournaments stay as large as active ones and push the active ones down.
- The signed-in banner takes a third of a laptop screen before any game data.

## What

1. **Practice order:** a short "Each day: 1 Buy stock · 2 Set prices · 3 Trade one day" line,
   then Buy stock and Selling prices side by side, then Trade one day. AI advisor, Loan and New
   run move into a row of three expanders under the title "More options".
2. **Warnings before trading:** `logic.trade_warnings(stock, prices, references=None)` returns a
   list of short messages, shown above "Trade one day" (practice) and above "Ready"
   (tournament). Trading is still allowed.
   - no stock at all → "You have no stock, so this day sells nothing. Buy stock first."
   - a product with stock priced above twice its reference →
     "{product}: above €{2 × reference}, nobody will buy it."
   - a product with stock priced below its unit cost →
     "{product}: below its unit cost (€{cost}), every sale loses money."
   `references` (product → reference price) replaces the catalogue reference when given.
3. **Reference price today (tournaments):** `logic.stand_references(weather, upgrades)` returns
   the reference price of each product for one stand: the catalogue price, raised by the
   weather (rain: Café €5.00, hot: Water €1.50) and by owned upgrades, taking the higher one — the
   same rule the shared market uses when the day closes. Each tournament product card shows
   "Reference today" and the limits for budget (≤ reference) and premium (≤ 2 × reference)
   customers.
4. **Finished tournaments last:** `logic.split_tournaments(rows)` returns
   `(active, finished)`; a tournament is finished after day 5. Active cards come first;
   finished ones are inside a closed "Finished tournaments (N)" expander.
5. **Compact banner** when signed in (smaller title and padding); the signed-out page keeps the
   large one.
6. **How to play** explains a tournament day: Ready, Refresh, Market results, weather and
   Coffee machine references.

## Out of scope

- Changes to rules, `db.py` or the tables.
- Blocking a trade because of a warning.

## Done when

1. **Warnings:** no stock; a price above twice the reference; a price below the unit cost each
   give their message; a sensible day gives no warning.
2. **References replace the catalogue:** with a Café reference of €5.00, a Café price of €9.00
   gives no warning and €10.01 does.
3. **Stand references:** catalogue without weather or upgrades; rain → Café €5.00; hot → Water
   €1.50; Coffee machine → Café €5.00; rain and Coffee machine → Café €5.00.
4. **Same rule as the market:** for rain and Coffee machine, a stand priced at the reference sells
   to budget customers at the day close (sales match `stand_references`).
5. **Split tournaments:** days 1–5 are active and day 6 is finished, keeping the order.
6. **Screen:** `app.py` calls `trade_warnings`, `stand_references` and `split_tournaments`, and
   Practice has the "More options" expanders for advisor, loan and new run.
7. **No behaviour change:** all existing tests still pass.
