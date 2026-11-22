# Fix: no faded "ghost" boxes after a button

Owner: Filippo Venturini · Branch: `fix-ghost-elements` · Reviewer: Patrick

## Why

Filippo played a whole tournament live on 22 Nov, Coffee machine included. The game rules were
right (Café reference €5.00 after the machine, sales and cash correct), but after the last Ready
the tournament card changed from "playing" to "complete" and the page showed faded old boxes
(part 1 and old tables) above "4 Final results" until a manual reload. This is what made the game
look "out of step" after some clicks.

The cause: buttons ended with `st.rerun(scope="fragment")`, which redraws only one piece of the
page. When that piece changes its layout, Streamlit can leave the old elements on screen.

## What

1. Every button that changes the game (buy, prices, Coffee machine, Ready, Close day, loans,
   Trade day, New run, join/create) ends with a full `st.rerun()`. The page only builds the screen
   that is open, so it is about as fast. `practice_plan`, `tournament_plan`, `practice_screen` and
   `tournament_card` stay fragments, so typing a quantity still updates only the live total.
2. Spacing: the live "Total €…" line has space below it, so it no longer touches Buy stock.
3. Tournament charts: the "every player" chart gets fixed colours and a legend like the other
   chart, so the two boxes have the same height.

## Out of scope

- Rules, `logic.py`, `db.py`, tables.

## Done when

1. `app.py` has no `st.rerun(scope="fragment")` left and still calls `st.rerun()`.
2. The `.order-total` style has a bottom margin.
3. Both tournament bar charts pass a `color`.
4. All existing tests still pass.
