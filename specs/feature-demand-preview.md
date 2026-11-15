# Demand preview (practice game)

## Why
In the practice game the player sets prices and stock but only sees the result after
pressing "Trade one day". A preview shows, before trading, how many units each product
will sell with the current price and stock, so pricing becomes an informed decision
(CT03: "show the demand rule so players can make informed decisions"). UI/UX criterion.

## What
- [ ] A new function in logic.py: `demand_preview(game)`. It takes a practice game
      (the dict returned by load_game) and returns, for each product in PRODUCTS,
      {"price": current price, "demand": demand(price, reference price),
       "stock": current stock, "will_sell": the smaller of demand and stock}.
      It uses logic.demand(); the rule is never copied anywhere else.
- [ ] It only reads the game: it never changes the game and never touches the database.
- [ ] In app.py, the practice "Products" table shows two more columns, "Demand at this
      price" and "Will sell", taken from demand_preview. While the run is complete the
      preview is not shown.
- [ ] Practice game only: the tournament screens do not show it, because in a tournament
      sales depend on the other players' prices.

## Out of scope
Tournaments, changing the demand rule, charts, any database or table change.

## Done when
1. New game (stock 0, reference prices): every product has demand 10 and will_sell 0.
2. Café €4.00 with 20 units → demand 10, will_sell 10. Croissant €3.50 with 3 units →
   demand 5, will_sell 3. Water €2.41 with 10 units → demand 0, will_sell 0.
3. Boundaries for Water (reference €1.20) with 20 units: €1.20 → 10, €1.21 → 5,
   €2.40 → 5, €2.41 → 0.
4. demand_preview does not change the game it receives (same dict after the call).
5. All existing tests pass unchanged.
6. By hand: after setting a price or buying, the Products table shows the new
   "Demand at this price" and "Will sell" values; trading one day sells exactly the
   "Will sell" units.
7. On branch feature-demand-preview, pushed, pull request reviewed by a teammate.
