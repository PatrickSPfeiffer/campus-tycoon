# Feature 3: three products

## Why
The business sells a small catalogue, so the player decides what to stock
and how to price each product. (First release: at least three products.)

## What
Implements the catalogue and the "by product" parts of CT01–CT04 (scenarios A1–A5).
- [ ] The catalogue has three products with a fixed unit cost and reference price:
      Café €2.00 / €4.00, Croissant €1.50 / €3.00, Water €0.50 / €1.20.
- [ ] Cash and day are shared; stock and selling price are kept per product.
      A new game starts with €100, day 1, every stock at 0 and every price at its reference.
- [ ] Buying names a product. An unknown product is rejected and nothing changes.
      The other buying rules stay as in feature 1.
- [ ] Setting a price names a product and changes only that product.
      The other price rules stay as in feature 2.
- [ ] Trading one day applies CT R1–R3 to each product and shows units sold, revenue,
      COGS and gross profit by product and in total. Each day is recorded once.
- [ ] Stock, prices and each day's results by product are saved and loaded after a restart.
- [ ] The screen shows stock and price by product, lets the player choose the product
      when buying and setting a price, shows the total cost before buying (CT02),
      and shows the day's results by product and in total.

## Out of scope
Days 2–5 and the end of the run, starting a new run, the player adding or removing
products, changing costs or reference prices, upgrading old databases.

## Done when
1. New game: €100, day 1; Café, Croissant and Water have stock 0 and prices €4.00, €3.00, €1.20.
2. Buy 10 Café and 10 Croissant → cash €65, stock 10 / 10 / 0.
   Buying an unknown product is rejected; cash and stock stay the same.
   Setting the price of an unknown product is rejected; prices stay the same.
3. Set Croissant to €3.50 → Café stays €4.00. Restart → both prices kept.
4. With €65, 10 Café at €4.00, 10 Croissant at €3.50 and no Water, trade one day:
   Café sells 10 (revenue €40, COGS €20, profit €20); Croissant sells 5 (revenue €17.50,
   COGS €7.50, profit €10); Water sells 0. Totals: 15 units, revenue €57.50, COGS €27.50,
   profit €30. Cash €122.50, stock 0 / 5 / 0, day 2.
5. Restart after check 4 → same cash, stock, prices and day; day 1 has exactly one
   result per product.
6. The tests of features 1 and 2, updated only to name the product, still pass with
   exactly the same numbers.
7. All tests green, on branch feature-3-three-products, pushed.
