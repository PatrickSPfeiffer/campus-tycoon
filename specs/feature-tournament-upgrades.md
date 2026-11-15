# Tournament upgrades

## Why

In a tournament every stand sells at the same reference prices, so the only choices are what to buy and what to charge. A one-time upgrade adds an investment decision: pay cash now to sell at better prices on the remaining days. (Project list: "Upgrades", Medium, low priority. The rules are in docs/team-brief.md, section "Upgrades".)

## What

1. **Catalogue.** There is one upgrade for now, defined in one place in `logic.py` (a constant `UPGRADES`): "Coffee machine", cost €30.00, it raises the Café reference price of the buyer's stand from €4.00 to €5.00. Adding another upgrade later means adding an entry, not new rules. The practice game has no upgrades.

2. **Buying.** `buy_tournament_upgrade(db_path, player, tournament_id, upgrade)` lets a player buy an upgrade for their own stand on any day, as long as they have not pressed Ready that day and the tournament is not complete. On success the stand's cash goes down by the cost (rounded to 2 decimals), the stand owns the upgrade from now on, and the new cash is returned.

3. **Refusals.** A refusal raises ValueError with a clear message, and nothing changes (no cash, no upgrade). The checks are made in this order: unknown tournament; tournament complete; player has not joined (same messages as buying stock); player already Ready (same message as buying stock after Ready); unknown upgrade ("Unknown upgrade."); already owned ("You already have this upgrade."); not enough cash (same message as buying stock without enough cash). Having exactly enough cash is accepted: cash becomes 0.00.

4. **Effect on sales.** The Coffee machine raises the Café reference price for that stand from €4.00 to €5.00. Tournament sales use the shared-market rule: for each product, budget customers can pay up to a stand's reference price and premium customers up to twice that price. Sales remain capped by stock. For one Café stand with enough stock, the existing `market_sales` tests show the catalogue reference of €4.00 sells 10 units at €4.00, 5 at €8.00, and 0 at €8.01; a €5.00 reference sells 10 at €5.00, 5 at €10.00, and 0 at €10.01. In a shared market, the exact units also depend on other stands, their prices and stock, the day, and seat order. The upgrade affects only its owner's Café stand, starting on the purchase day and lasting through the tournament; other stands and products keep their catalogue reference prices. Practice mode and `tournament_units_sold` are unchanged.

5. **Final gain (decision).** An upgrade is a cost, not an asset. Its price leaves cash when it is bought, and a leftover upgrade is worth 0 at the end. The final gain stays final cash + leftover stock at cost − 100 (CT R4). `final_result` and `tournament_ranking` do not change. A player who only buys the Coffee machine ends with a gain of −30.00; the upgrade pays off only if it brings back more than its price. Tournament stands always start with €100.00 (the difficulty levels apply to the practice game only).

6. **What the player sees.** `tournament_upgrades(db_path, player, tournament_id)` returns the names of the upgrades owned by the player's stand, in alphabetical order; it is refused for an unknown tournament and for a player who has not joined (same messages as the other functions). In a tournament screen that is not complete, while the player is not Ready, an "Upgrades" block lists each upgrade with its cost and effect: a Buy button if the stand does not own it, "Owned" if it does. Refusals are shown as messages, like for the other actions. app.py never reads the database.

7. **Storage.** A stand's upgrades are stored in a new table `stand_upgrades`: tournament_id INTEGER NOT NULL, player TEXT NOT NULL, upgrade TEXT NOT NULL, PRIMARY KEY (tournament_id, player, upgrade). The owner of the data structure (Patrick) approved this table on 14 November 2026 and asked that this feature adds it: one `CREATE TABLE IF NOT EXISTS` in `create_tables` (so existing databases, including the hosted one, get the table the next time they are opened) and its description in `docs/data-model.md`, under "Tournament tables". No existing table or column changes. The primary key also makes the database refuse a second purchase.

## Delivery in two steps

1. Everything except the effect on sales: the table, buying, `tournament_upgrades`, the "Upgrades" block on the screen, and the unchanged ranking.
2. **Current work: wire upgrades into tournament sales.** `tournament_market_sales(stands, day, references=None)` accepts an optional `references` dict shaped as `{player: {product: reference_price}}`. For a player and product with no entry, including when `references` is omitted, use the catalogue reference price. This keeps the existing PR #27 tests valid. `_close_tournament_day` builds the dict from the upgrades each player owns using `db.get_tournament_upgrades` and `logic.UPGRADES`, then passes it to `tournament_market_sales`. This makes an upgrade effective on the day it is bought and for the rest of the tournament. `tournament_units_sold` stays unchanged. Practice mode is not affected.

It is one pull request, kept as a draft until step 2 is done: merging step 1 alone would let players pay for an upgrade that does nothing.

## Out of scope

- More upgrades than the Coffee machine; selling or refunding an upgrade; upgrades that change unit cost, stock or the practice game.
- Changes to the shared-market rule itself (`market_sales`); this feature supplies each tournament stand's reference through `tournament_market_sales`.
- Weather, loans, charts, the CSV report, UI polish, and any change to the final ranking.
- Any table change other than `stand_upgrades`.

## Done when

1. Tests in `tests/test_tournament_upgrades.py` are written first and fail at first. They cover: a successful purchase (cash, ownership, returned cash); exact cash; each refusal in the order above with nothing changed; the same upgrade is independent for another player and for another tournament; a ranking gain of −30.00 when the only action is the purchase; and the output of `tournament_upgrades`.
2. `uv run pytest` passes, with all existing tests unmodified.
3. By hand with two players: one buys the Coffee machine and both price Café at €5.00; with the buyer in the first seat on day 1 and enough stock, closing the day sells 15 units for the buyer and 5 for the other player (10 budget customers can buy only from the upgraded stand; the 10 premium customers split evenly). The screen shows the upgrade as owned; a second purchase, a purchase without cash and a purchase after Ready are refused with a clear message.
4. The diff touches only `logic.py`, `db.py` (including `create_tables`), `app.py`, `docs/data-model.md`, `docs/team-brief.md`, the tests and this spec.
5. The pull request passes the "Tests" check.
6. Sales effect tests confirm `tournament_market_sales` uses supplied per-player, per-product references and falls back to catalogue references when the argument or an entry is missing, preserving the PR #27 outcomes. A day closed on the purchase day uses the upgraded Café reference for the buyer only, and later tournament days continue to use it; other players and products are unaffected.
7. Tests confirm `tournament_units_sold` and practice-mode sales are unchanged. Shared-market numeric examples match `market_sales` and `tests/test_shared_market.py`.
