# Feature: tournament layout polish

Owner: Filippo Venturini · Branch: `tournament-layout-polish` · Reviewer: Filippo Bortignon (owner of the tournament layout)

## Why

After #49 the tournament card uses the Practice layout, but on the live app it does not look like
Practice:

- The CSS of the Practice parts, boxes and product lines targets only the `practice_*` keys, so
  the tournament parts get no inner padding: labels touch the borders, the four boxes of part 1
  have different heights, the supplier prices are not teal, the Buy stock button is not teal and
  part 3 is not highlighted.
- "Results" and "Market results" are two headings one after the other, outside any part, and the
  players' list sits at the bottom, far from the Ready button.
- The "Market result" column always shows "At close", which tells the player nothing.
- The confirmation of Buy stock, Save selling prices and Buy Coffee machine is stored but never
  shown, so the player gets no feedback.
- An organiser who does not play has no "Close day now" button any more (it moved inside the
  player-only form).

## What

1. Every Practice style for parts, the four boxes, plan headings, buy/sell sides, the Buy stock
   button, the highlighted part 3 and its main button, and the phone rules, also applies to the
   matching tournament keys (`tournament_part_*`, `tournament_box_*`,
   `tournament_plan_headings_*`, `tournament_buy_side_*`, `tournament_sell_side_*`,
   `t<id>_buy_button`, `tournament_part_trade_*`, `t<id>_ready_button`).
2. Part 2 shows the shared-market rule as a line with the info icon, like Practice:
   "Customers per day: 10 per player and product · half pay up to the reference price, half up to
   twice it · the cheapest stand sells first."
3. The third column of each sell box is "Customers pay up to": "€X / €2X" (budget / premium)
   for that stand's reference today. It is the rule, not a sales estimate.
4. Part 3 "Trade day N" also lists the players and who is ready.
5. A part 4 "Results" holds the day-closed box, Market results (latest day, earlier days in an
   expander) and, after day 5, the ranking. One heading only.
6. Every flash message set in the tournament card is shown: buy, prices, upgrade, ready, close.
7. An organiser who does not play sees the same part 3 with the players and a "Close day now"
   button, and part 4.
8. The Coffee machine box shows "Owned" without a second "Already purchased" line.

## Out of scope

- Changes to `logic.py`, `db.py`, the tables, rules or the Practice screen.

## Done when

1. **Styles:** the CSS has rules for each tournament key listed in What 1.
2. **Feedback:** every `flash(...)` scope used in `tournament_card` is shown with `show_flash`.
3. **Organiser:** `tournament_card` has a plain `st.button` "Close day now" for the organiser who
   does not play, and the form button for the organiser who plays.
4. **Parts:** `tournament_card` calls `part_heading` for parts 1–4, has no "At close" text and no
   separate "Market results" heading.
5. **No behaviour change:** all existing tests still pass.
