# Tournament upgrades

## Why

In a tournament every stand sells at the same reference prices, so the only choices are what to buy and what to charge. A one-time upgrade adds an investment decision: pay cash now to sell at better prices on the remaining days. (Project list: "Upgrades", Medium, low priority. The rules are in docs/team-brief.md, section "Upgrades".)

## What

1. **Catalogue.** There is one upgrade for now, defined in one place in `logic.py` (a constant `UPGRADES`): "Coffee machine", cost €30.00, it raises the Café reference price of the buyer's stand from €4.00 to €5.00. Adding another upgrade later means adding an entry, not new rules. The practice game has no upgrades.

2. **Buying.** `buy_tournament_upgrade(db_path, player, tournament_id, upgrade)` lets a player buy an upgrade for their own stand on any day, as long as they have not pressed Ready that day and the tournament is not complete. On success the stand's cash goes down by the cost (rounded to 2 decimals), the stand owns the upgrade from now on, and the new cash is returned.

3. **Refusals.** A refusal raises ValueError with a clear message, and nothing changes (no cash, no upgrade). The checks are made in this order: unknown tournament; tournament complete; player has not joined (same messages as buying stock); player already Ready (same message as buying stock after Ready); unknown upgrade ("Unknown upgrade."); already owned ("You already have this upgrade."); not enough cash (same message as buying stock without enough cash). Having exactly enough cash is accepted: cash becomes 0.00.

4. **Effect on sales.** An upgrade changes one input of the sales rule: the reference price of that product at that stand (the Coffee machine: Café €4.00 to €5.00). This feature does not change the rule that turns prices and stock into units sold. Each stand passed to the sales rule may carry an optional "reference" number (the reference price of the product for that stand); when it is missing the catalogue reference price is used, so existing callers do not change. The effect starts the day the upgrade is bought and lasts until the end of the tournament. Other stands and other products keep the catalogue reference price. With the per-stand rule used today by `tournament_units_sold` (10 units at or below the reference price, 5 up to twice the reference price, 0 above), Café at 4.00 gives 10 units; 5.00 gives 10 (5 without the upgrade); 8.00 gives 5; 10.00 gives 5 (0 without); 10.01 gives 0. Sales are still capped by stock. When the shared-market rule (`market_sales`) is in main, it must read the same "reference" input: budget customers then pay at most the stand's reference price and premium customers at most twice that price, as in the team brief. The numbers in the tests are fixed at that moment, against the rule that is in main.

5. **Final gain (decision).** An upgrade is a cost, not an asset. Its price leaves cash when it is bought, and a leftover upgrade is worth 0 at the end. The final gain stays final cash + leftover stock at cost − 100 (CT R4). `final_result` and `tournament_ranking` do not change. A player who only buys the Coffee machine ends with a gain of −30.00; the upgrade pays off only if it brings back more than its price. Tournament stands always start with €100.00 (the difficulty levels apply to the practice game only).

6. **What the player sees.** `tournament_upgrades(db_path, player, tournament_id)` returns the names of the upgrades owned by the player's stand, in alphabetical order; it is refused for an unknown tournament and for a player who has not joined (same messages as the other functions). In a tournament screen that is not complete, while the player is not Ready, an "Upgrades" block lists each upgrade with its cost and effect: a Buy button if the stand does not own it, "Owned" if it does. Refusals are shown as messages, like for the other actions. app.py never reads the database.

7. **Storage.** A stand's upgrades are stored in a new table `stand_upgrades`: tournament_id INTEGER NOT NULL, player TEXT NOT NULL, upgrade TEXT NOT NULL, PRIMARY KEY (tournament_id, player, upgrade). The owner of the data structure (Patrick) approved this table on 14 November 2026 and asked that this feature adds it: one `CREATE TABLE IF NOT EXISTS` in `create_tables` (so existing databases, including the hosted one, get the table the next time they are opened) and its description in `docs/data-model.md`, under "Tournament tables". No existing table or column changes. The primary key also makes the database refuse a second purchase.

## Delivery in two steps

1. Everything except the effect on sales: the table, buying, `tournament_upgrades`, the "Upgrades" block on the screen, and the unchanged ranking.
2. The effect on sales, built on top of the shared-market rule once it is in main.

It is one pull request, kept as a draft until step 2 is done: merging step 1 alone would let players pay for an upgrade that does nothing.

## Out of scope

- More upgrades than the Coffee machine; selling or refunding an upgrade; upgrades that change unit cost, stock or the practice game.
- The shared-market rule itself (`market_sales`, another feature): this feature only gives it each stand's "reference".
- Weather, loans, charts, the CSV report, UI polish, and any change to the final ranking.
- Any table change other than `stand_upgrades`.

## Done when

1. Tests in `tests/test_tournament_upgrades.py` are written first and fail at first. They cover: a successful purchase (cash, ownership, returned cash); exact cash; each refusal in the order above with nothing changed; the same upgrade is independent for another player and for another tournament; the effect on the day close for Café at the five prices above while other products are untouched; stands without "reference" behave as before; a ranking gain of −30.00 when the only action is the purchase; the output of `tournament_upgrades`. The tests about the effect on sales are added in step 2.
2. `uv run pytest` passes, with all existing tests unmodified.
3. By hand with two players: one buys the Coffee machine and both price Café at 5.00; after closing the day the buyer sells 10 units and the other 5; the screen shows the upgrade as owned; a second purchase, a purchase without cash and a purchase after Ready are refused with a clear message.
4. The diff touches only `logic.py`, `db.py` (including `create_tables`), `app.py`, `docs/data-model.md`, the tests and this spec.
5. The pull request passes the "Tests" check.
