# Fix: buttons as callbacks (ghost boxes, second part)

Owner: Filippo Venturini · Branch: `fix-ghost-callbacks` · Reviewer: Patrick

## Why

After `fix-ghost-elements` was merged, a live test on 23 Nov still showed a ghost: after
"Buy Coffee machine" the card showed part 1 twice (old cash €100.00 above, new cash €70.00 below),
both fully visible, until a page reload. So the problem is not the rerun *scope*: it is calling
`st.rerun()` while a fragment is half drawn (the button is in the middle of the card). The
elements already sent by the stopped run stay on screen.

## What

1. Every button inside a fragment (`practice_screen`, `tournament_card`) uses `on_click`: the
   action runs **before** the screen is drawn, and the screen is then drawn once, with the new
   state. No `st.rerun()` inside any fragment. Errors become flash messages (toasts for Buy and
   Save, which are far from the top).
2. Buy stock and Save selling prices move from the small plan fragments to the screen around them
   (still in the part 2 box, under the fields), so after them cash, stock and part 3 are current.
   The plan fragments keep only the fields and the live total.
3. Create and Join on the tournaments list are not in a fragment and keep `st.rerun()`.

## Out of scope

- Rules, `logic.py`, `db.py`, tables.

## Done when

1. No fragment function (or function defined inside one) calls `st.rerun`.
2. `practice_plan` and `tournament_plan` contain no button.
3. All existing tests still pass.
