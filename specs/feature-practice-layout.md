# Feature: Practice layout, buy side and sell side

## Goal
A first-time player understands the Practice screen without help: where they stand, what they buy from the supplier, what customers pay them, and when to trade. The two prices (supplier price and selling price) can no longer be mixed up.

## Scope
- app.py: practice_screen and its CSS only. The Tournaments, Home and How to play screens do not change.
- logic.py: one new function, expected_profit(game). No other rule changes.
- No change to db.py or the tables.

## New rule: expected_profit(game)
Uses logic.demand_preview(game) (saved prices and current stock).
For each product: round(will_sell × (price − unit_cost), 2). Total: round(sum of the products, 2).
Returns {"by_product": {product: amount}, "total": amount}.
Examples:
- Café stock 10, price 4.00; Croissant stock 5, price 5.00; Water stock 0 → Café 20.00, Croissant 17.50, Water 0.00, total 37.50.
- Café stock 10, price 1.50 (below the €2.00 cost) → Café −5.00 (a loss is shown as a negative number).
- Café stock 10, price 9.00 (above twice the reference) → Café 0.00.
- New game (no stock) → every product 0.00, total 0.00.

## Layout, top to bottom
0. New run bar (first thing on the page): difficulty select, "Start a new run" button, and the same confirmation as today ("Yes, start a new run" / "Cancel"). Same keys as today.
1. Part 1 "Your day and money": four boxes of the same width and height: Cash, Progress ("Day X of 5" or "Run complete", with the level), Loan to repay, and Take a loan (amount input, "You will owe €…", "Take loan" button; same rules, keys and disabled states as today).
   Final result block when the run is complete, as today.
2. Part 2 "Plan day X": headings "Buy from the supplier" (teal) and "Sell to customers" (amber). One line per product: name and "N in stock" | Supplier price (unit cost) and "How many" input | arrow | Reference price | "Your selling price" input | "Will sell" (from demand_preview). Labels and values aligned on every line.
   The demand rule is shown as a visible line (brief CT03), and each sell box shows the Reference price.
   All inputs are inside one form (no rerun while typing). Under the buy side: button "Buy stock" (buys the quantities, as today). Under the sell side: button "Save selling prices" (saves changed prices, as today). Each button does only its own job.
   After "Buy stock", if a typed selling price differs from the saved one, show: "Your new selling prices are not saved yet. Press Save selling prices."
   After a successful buy, the How many inputs go back to 0.
   Widget keys: How many uses practice_buy_<product>_<round>, and the round goes up after every successful buy, trade and new run. Your selling price uses practice_price_<product>_<round>, and the round goes up after a new run. Why: a widget inside a form only resets when its key changes; removing the key from session state is not enough, because the browser sends the old value again.
3. Part 3 "Trade day X": the most visible part (orange border and glow, big primary button "Trade day X"). Shows Will sell (total units from demand_preview), Expected profit (expected_profit total) and Days left after this day. The warnings from logic.trade_warnings appear inside this part. Trading does the same as today, including the result email at the end of the run.
   The Trade button is part of the same form. If any How many is above 0, the day is not traded and the screen says: 'You typed quantities but did not buy them. Press Buy stock first, or set How many to 0.' If a typed selling price differs from the saved one, the day is not traded and the screen says: 'Your new selling prices are not saved yet. Press Save selling prices first.' After a successful trade, the How many inputs go back to 0.
4. Results: the latest day table stays visible; the charts and older days go into an expander "Charts and all days". The CSV download stays when the run is complete.

## When the run is complete
Inputs and the Buy, Save, Loan and Trade buttons are disabled. Final result, New run and Results work as today.

## Phone
Parts stack; each product line can stack (buy side above sell side).

## Manual checks
- New Normal run: Cash €100.00, Day 1 of 5, four boxes the same size.
- Buy 10 Café and 5 Croissant: toast with the cost, stock updates, inputs back to 0, Will sell updates.
- Type a new price, press Buy stock: the "not saved yet" message shows; press Save selling prices: Will sell and Expected profit update.
- Buy more than the cash: error, nothing bought.
- Price 0 or above the maximum: error, no price saved.
- No stock: warning inside part 3, trading still allowed.
- Take a loan of €50: Loan to repay €55.00, Take loan disabled after.
- New run asks for confirmation and resets prices.
- Day 5 traded: Final result, email arrives, inputs disabled, CSV download works.
- Phone width: everything stacks and is readable.

## Out of scope
Changes to the Tournaments, Home or How to play screens; new game rules other than expected_profit; live totals while typing (the inputs stay in a form); changes to db.py or the tables.

## Done when
1. All existing tests pass unchanged, except test_practice_has_more_options_expanders in tests/test_easier_screens.py, which is replaced by a test with the same intent (the Practice screen still offers Loan and New run).
2. New tests for expected_profit cover the four examples above and pass.
3. By hand: every item under "Manual checks" works.
