# Tournament upgrades

## Why

In a tournament every stand sells at the same reference prices, so the only choices are what to buy and what to charge. A one-time upgrade adds an investment decision: pay cash now to sell at better prices on the remaining days. (Project list: "Upgrades", Medium, low priority. The rules are in docs/team-brief.md, section "Upgrades".)

## What

1. **Catalogue.** There is one upgrade for now, defined in one place in `logic.py` (a constant `UPGRADES`): "Coffee machine", cost €30.00, it raises the Café reference price of the buyer's stand from €4.00 to €5.00. Adding another upgrade later means adding an entry, not new rules. The practice game has no upgrades.

2. **Buying.** `buy_tournament_upgrade(db_path, player, tournament_id, upgrade)` lets a player buy an upgrade for their own stand on any day, as long as they have not pressed Ready that day and the tournament is not complete. On success the stand's cash goes down by the cost (rounded to 2 decimals), the stand owns the upgrade from now on, and the new cash is returned.

3. **Refusals.** A refusal raises ValueError with a clear message, and nothing changes (no cash, no upgrade). The checks are made in this order: unknown tournament; tournament complete; player has not joined (same messages as buying stock); player already Ready (same message as buying stock after Ready); unknown upgrade ("Unknown upgrade."); already owned ("You already have this upgrade."); not enough cash (same message as buying stock without enough cash). Having exactly enough cash is accepted: cash becomes 0.00.

4. **Effect on sales.** `tournament_market_sales(stands, day, references=None, upgrade_references=None)` accepts two optional reference maps. `references` keeps its weather meaning: `{product: reference_price}`, the same for all players. `upgrade_references` is `{player: {product: reference_price}}`, built from the upgrades each player owns. A missing argument or entry changes nothing. For one player and one product, the stand reference is the higher of the weather reference and upgrade reference when both exist; it is the one that exists when only one exists; and it is the catalogue reference when neither exists. The Coffee machine gives its owner’s Café stand a €5.00 upgrade reference, starting on the purchase day and lasting through the tournament. Tournament sales use the shared-market rule: budget customers can pay up to a stand’s reference price and premium customers up to twice that price. Sales remain capped by stock. For one Café stand with enough stock, the existing `market_sales` tests show the catalogue reference of €4.00 sells 10 units at €4.00, 5 at €8.00, and 0 at €8.01; a €5.00 reference sells 10 units at €5.00, 5 at €10.00, and 0 at €10.01. With two players charging €5.00 for Café and holding 20 each, the Coffee machine buyer sells 15 and the other player sells 5 on a normal day. On a rainy day, weather gives every player a Café reference of €5.00, so both sell 10, the same outcome as without the machine because €5.00 is already the reference. On a hot day, weather gives every player a Water reference of €1.50; Café sales remain 15 for the buyer and 5 for the other player, because the Coffee machine does not affect Water. Practice mode and `tournament_units_sold` are unchanged.

5. **Final gain (decision).** An upgrade is a cost, not an asset. Its price leaves cash when it is bought, and a leftover upgrade is worth 0 at the end. The final gain stays final cash + leftover stock at cost − 100 (CT R4). `final_result` and `tournament_ranking` do not change. A player who only buys the Coffee machine ends with a gain of −30.00; the upgrade pays off only if it brings back more than its price. Tournament stands always start with €100.00 (the difficulty levels apply to the practice game only).

6. **What the player sees.** `tournament_upgrades(db_path, player, tournament_id)` returns the names of the upgrades owned by the player's stand, in alphabetical order; it is refused for an unknown tournament and for a player who has not joined (same messages as the other functions). In a tournament screen that is not complete, while the player is not Ready, an "Upgrades" block lists each upgrade with its cost and effect: a Buy button if the stand does not own it, "Owned" if it does. Refusals are shown as messages, like for the other actions. app.py never reads the database.

7. **Storage.** A stand's upgrades are stored in a new table `stand_upgrades`: tournament_id INTEGER NOT NULL, player TEXT NOT NULL, upgrade TEXT NOT NULL, PRIMARY KEY (tournament_id, player, upgrade). The owner of the data structure (Patrick) approved this table on 14 November 2026 and asked that this feature adds it: one `CREATE TABLE IF NOT EXISTS` in `create_tables` (so existing databases, including the hosted one, get the table the next time they are opened) and its description in `docs/data-model.md`, under "Tournament tables". No existing table or column changes. The primary key also makes the database refuse a second purchase.

## Delivery in two steps

1. Everything except the effect on sales: the table, buying, `tournament_upgrades`, the "Upgrades" block on the screen, and the unchanged ranking.
2. **Current work: wire upgrades into tournament sales.** `tournament_market_sales(stands, day, references=None, upgrade_references=None)` accepts an optional weather `references` dict shaped as `{product: reference_price}` and an optional `upgrade_references` dict shaped as `{player: {product: reference_price}}`. A missing argument or entry changes nothing. For each player and product, use the higher of the weather and upgrade references when both exist, the one that exists when only one exists, or the catalogue reference when neither exists. `_close_tournament_day` builds weather references from `db.get_tournament_weather` and upgrade references from each player’s upgrades using `db.get_tournament_upgrades` and `logic.UPGRADES`, then passes both dicts to `tournament_market_sales`. This makes an upgrade effective on the day it is bought and for the rest of the tournament. `tournament_units_sold` stays unchanged. Practice mode is not affected.

It is one pull request, kept as a draft until step 2 is done: merging step 1 alone would let players pay for an upgrade that does nothing.

## Out of scope

- More upgrades than the Coffee machine; selling or refunding an upgrade; upgrades that change unit cost, stock or the practice game.
- Changes to the shared-market rule itself (`market_sales`); this feature supplies each tournament stand's reference through `tournament_market_sales`.
- Changing the weather feature itself, loans, charts, the CSV report, UI polish, and any change to the final ranking.
- Any table change other than `stand_upgrades`.

## Done when

1. Tests in `tests/test_tournament_upgrades.py` are written first and fail at first. They cover: a successful purchase (cash, ownership, returned cash); exact cash; each refusal in the order above with nothing changed; the same upgrade is independent for another player and for another tournament; a ranking gain of −30.00 when the only action is the purchase; and the output of `tournament_upgrades`.
2. `uv run pytest` passes, with all existing tests unmodified.
3. By hand with one player: buy 20 Café, set the Café price to €5.00 and buy the Coffee machine before Ready. After closing the day, Café sells 10 units (revenue €50.00). In a second tournament without the Coffee machine, the same decisions sell 5 units (revenue €25.00). The screen shows the upgrade as owned; a second purchase, a purchase without cash and a purchase after Ready are refused with a clear message. The two-player case (buyer 15 units, other player 5 units, at the same price) is checked by the automated tests in tests/test_tournament_upgrades.py.
4. The diff touches only `logic.py`, `db.py` (including `create_tables`), `app.py`, `docs/data-model.md`, `docs/team-brief.md`, the tests and this spec.
5. The pull request passes the "Tests" check.
6. Sales effect tests use `upgrade_references` for direct per-player, per-product upgrade references, while `references` remains the weather map. They confirm catalogue fallback when the argument or an entry is missing and preserve the PR #27 outcomes. Tests cover two players charging €5.00 for Café with 20 units each: without rain, the Coffee machine buyer sells 15 and the other player sells 5; on a rainy day, with a €5.00 weather reference for Café for everyone, both sell 10; on a hot day, with a €1.50 weather reference for Water for everyone, Café sales remain 15 and 5 and the Coffee machine does not affect Water. The weather tests remain unchanged.
7. Tests confirm `tournament_units_sold` and practice-mode sales are unchanged. Shared-market numeric examples match `market_sales` and `tests/test_shared_market.py`.
