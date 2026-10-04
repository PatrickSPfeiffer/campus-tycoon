# First feature: buy stock, trade one day, reload

## Why
The player can buy stock, trade for one day, see whether they made a profit,
and continue later without losing progress.

## What
Implements part of CT01, CT02, CT04 and rules CT R1–R3, R5 (scenarios A1, A3, A5).
- [ ] A new game starts with €100 cash, 0 stock, day 1.
- [ ] One product: Café, unit cost €2.00, reference price €4.00. Selling price is fixed at €4.00.
- [ ] Buying takes a positive whole quantity. Cost = quantity × unit cost.
- [ ] A purchase that costs more than the cash is rejected; cash and stock stay unchanged.
- [ ] Demand follows CT R1: price ≤ reference → 10; ≤ 2× reference → 5; above → 0.
- [ ] Trading one day: units sold = min(demand, stock). Cash increases by units sold × price
      (the purchase is NOT deducted again). Stock decreases. Day goes up by 1.
- [ ] The day's result shows units sold, revenue, cost of goods sold and gross profit.
- [ ] Cash, stock, day and the day's result are saved in SQLite and loaded when the app starts.

## Out of scope
The other two products, setting prices, days 2–5 and the end of the run,
starting a new run with confirmation, the full history view.

## Done when
1. New game: buy 10 → €80 and 10 units. Then buy 41 (€82) → rejected, still €80 and 10 units.
   Buying 0, -5 or 2.5 units is rejected; cash and stock stay unchanged.
2. Trade with 10 units at €4 → sold 10, revenue €40, COGS €20, gross profit €20,
   cash €120, stock 0, day 2.
3. Stop the app (Ctrl+C) and start it again → cash €120, stock 0, day 2,
   and day 1 appears exactly once in the results.
4. Demand for prices €4, €4.01, €8, €8.01 is 10, 5, 5, 0.
5. With 3 units, trading sells 3: cash €106, stock 0. With 15 units, trading sells 10: cash €110, stock 5.
6. All tests green, on branch `first-feature`, pushed.
