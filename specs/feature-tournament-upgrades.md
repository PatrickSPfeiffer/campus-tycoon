# Tournament upgrades

## Why

In a tournament every stand sells at the same reference prices, so the only choices are what to buy and what to charge. A one-time upgrade adds an investment decision: pay cash now to sell at better prices on the remaining days. (Project list: "Upgrades", Medium, low priority. The rules are in docs/team-brief.md, section "Upgrades".)

## What

1. **Catalogue.** There is one upgrade for now, defined in one place in `logic.py` (a constant `UPGRADES`): "Coffee machine", cost €30.00, it raises the Café reference price of the buyer's stand from €4.00 to €5.00. Adding another upgrade later means adding an entry, not new rules. The practice game has no upgrades.

2. **Buying.** `buy_tournament_upgrade(db_path, player, tournament_id, upgrade)` lets a player buy an upgrade for their own stand on any day, as long as they have not pressed Ready that day and the tournament is not complete. On success the stand's cash goes down by the cost (rounded to 2 decimals), the stand owns the upgrade from now on, and the new cash is returned.

3. **Refusals.** A refusal raises ValueError with a clear message, and nothing changes (no cash, no upgrade). The checks are made in this order: unknown tournament; tournament complete; player has not joined (same messages as buying stock); player already Ready (same message as buying stock after Ready); unknown upgrade ("Unknown upgrade."); already owned ("You already have this upgrade."); not enough cash (same message as buying stock without enough cash). Having exactly enough cash is accepted: cash becomes 0.00.

4. **Effect on sales.** When a day closes, a stand that owns the upgrade uses the upgrade's reference price for that product in the demand rule (10 units at or below the reference price, 5 units up to twice the reference price, 0 above). It works the same day it is bought. Other stands and other products keep the catalogue reference price. `tournament_units_sold(stands)` keeps its output; each stand may carry an optional "reference" mapping product to reference price, and when it is missing the catalogue price is used, so existing callers do not change. Example for Café: price 4.00 gives 10 units; 5.00 gives 10 (5 without the upgrade); 8.00 gives 5; 10.00 gives 5 (0 without); 10.01 gives 0. Sales are still capped by stock.

5. **Final gain (decision).** An upgrade is a cost, not an asset. Its price leaves cash when it is bought, and a leftover upgrade is worth 0 at the end. The final gain stays final cash + leftover stock at cost − 100 (CT R4). `final_result` and `tournament_ranking` do not change. A player who only buys the Coffee machine ends with a gain of −30.00; the upgrade pays off only if it brings back more than its price.

6. **What the player sees.** `tournament_upgrades(db_path, player, tournament_id)` returns the names of the upgrades owned by the player's stand, in alphabetical order; it is refused for an unknown tournament and for a player who has not joined (same messages as the other functions). In a tournament screen that is not complete, while the player is not Ready, an "Upgrades" block lists each upgrade with its cost and effect: a Buy button if the stand does not own it, "Owned" if it does. Refusals are shown as messages, like for the other actions. app.py never reads the database.

7. **Storage.** A stand's upgrades are stored in a new table `stand_upgrades`: tournament_id INTEGER NOT NULL, player TEXT NOT NULL, upgrade TEXT NOT NULL, PRIMARY KEY (tournament_id, player, upgrade). The table is added by the owner of the data structure (AGENTS.md). This feature creates and changes no table itself, and the code that uses the table starts once the table is in main. The primary key also makes the database refuse a second purchase.

## Out of scope

- More upgrades than the Coffee machine; selling or refunding an upgrade; upgrades that change unit cost, stock or the practice game.
- The shared-market rule: when it arrives it must read each stand's "reference" in the same way.
- Weather, loans, charts, the CSV report, UI polish, and any change to the final ranking.
- Any table change other than `stand_upgrades`, which belongs to the owner of the data structure.

## Done when

1. Tests in `tests/test_tournament_upgrades.py` are written first and fail at first. They cover: a successful purchase (cash, ownership, returned cash); exact cash; each refusal in the order above with nothing changed; the same upgrade is independent for another player and for another tournament; the effect on the day close for Café at the five prices above while other products are untouched; stands without "reference" behave as before; a ranking gain of −30.00 when the only action is the purchase; the output of `tournament_upgrades`.
2. `uv run pytest` passes, with all existing tests unmodified.
3. By hand with two players: one buys the Coffee machine and both price Café at 5.00; after closing the day the buyer sells 10 units and the other 5; the screen shows the upgrade as owned; a second purchase, a purchase without cash and a purchase after Ready are refused with a clear message.
4. The diff touches only `logic.py`, `db.py`, `app.py`, the tests and this spec, plus, from the owner of the data structure, `create_tables` and `docs/data-model.md`.
5. The pull request passes the "Tests" check.
