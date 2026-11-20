# Feature: live order total

Owner: Filippo Venturini · Branch: `tournament-clarity` (same pull request) · Reviewer: Patrick

## Why

Under "Buy from the supplier" the player types how many Café, Croissant and Water to buy, but
the screen does not say what the order costs: they have to multiply each supplier price by the
quantity in their head. The fields were inside a form, so nothing could update while typing.
The original brief (CT02) asks to show the total cost of a purchase.

## What

1. In Practice and in each tournament card, part 2 "Plan day N" is its own small
   `st.fragment` (`practice_plan`, `tournament_plan`) without a form. Typing a quantity or a price
   reruns only that part: no database read, so it is quick.
2. Under the buy side, `order_total` shows at once:
   - nothing typed: "Type how many to see the total cost."
   - an order: "Total €X · cash after buying €Y" (teal), using `logic.order_cost`;
   - more than the cash: "Total €X: more than your cash (€Z)." (red). Buying is still refused by
     `logic.buy_many` / `logic.buy_tournament_stock_many`, as today.
3. Under the sell side: "Prices are saved." or "Prices changed: press Save selling prices."
4. Buy stock and Save selling prices are normal buttons; after them the page reruns, so cash,
   stock and part 3 are current, and the How many fields start again from 0.
5. Practice: "Trade day N" still refuses to trade while quantities are typed but not bought, or
   prices are changed but not saved (it reads the fields from session state).
6. Tournament: Ready and Close day now stay together in a small form (part 3); the Coffee machine
   button is a normal button.
7. Spacing: the tournament part 1 boxes no longer have the tall minimum height that Practice
   needs for the loan field.

## Out of scope

- Rules, `logic.py`, `db.py`, tables.

## Done when

1. `practice_plan` and `tournament_plan` are fragments and both call `order_total`.
2. `order_total` uses `logic.order_cost`, and no form contains the How many fields any more.
3. All existing tests still pass.
