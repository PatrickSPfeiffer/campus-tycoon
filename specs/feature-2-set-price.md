# Feature 2: set the selling price

## Why
The player chooses the Café price before trading: a low price sells more units,
a higher price earns more per unit. (CT03)

## What
Implements CT03 and uses CT R1 and R3 (scenarios A2, A3, A5).
- [ ] A new game starts with the selling price at €4.00 (the reference price).
- [ ] The player can set the Café selling price. It must be positive with at most
      2 decimals; otherwise it is rejected and nothing changes.
- [ ] The price is saved immediately and loaded after a restart.
- [ ] Trading uses the saved price: demand follows CT R1, revenue = units sold × price,
      and every money value is rounded to 2 decimals.
- [ ] The screen shows the current price, a price input, a "Set price" button and
      the demand rule. A rejected price shows a message.

## Out of scope
The other two products, days 2–5 and the end of the run, starting a new run,
changing the unit cost or reference price.

## Done when
1. New game: price is €4.00. Buy 10, then set €6.00 → saved. Restart → still €6.00, €80 cash and 10 units.
2. Setting €0, −€1 or €4.001 is rejected; the price stays as it was.
3. €80, 10 units, price €6.00 (demand 5): sells 5, revenue €30, COGS €10,
   gross profit €20, cash €110, stock 5.
4. €80, 10 units, price €9.00 (demand 0): sells 0, cash €80, stock 10, day goes up by 1.
5. €80, 10 units, price €4.01 (demand 5): revenue €20.05, gross profit €10.05, cash €100.05.
6. The 6 tests of feature 1 still pass.
7. All tests green, on branch feature-2-set-price, pushed.
