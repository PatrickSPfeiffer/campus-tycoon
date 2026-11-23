# Polish before submission

Owner: Filippo Venturini · Branch: `polish-before-submission` · Reviewer: Patrick

## Why

Full live test on 23 Nov (Practice run to the end with a loan, a whole tournament with the Coffee
machine, Help, phone width). The game is right and no ghost boxes are left; a few details still
look unfinished:

1. Disabled buttons look exactly like active ones: after the run ends, the big orange
   "Run complete" button and Buy stock / Save selling prices look clickable but do nothing.
2. The Help page still says "Market results" (the screen says "Day N results") and does not say
   that the tournament weather changes every day.
3. The two tournament charts have different heights (one has a legend, the other not).
4. When the Practice run is complete, the charts stay folded, while a finished tournament shows
   them open.
5. The loan amount field stays editable after the loan is taken or the run ends.

## What

1. CSS: every disabled button is faded (`opacity`, no glow) with a "not allowed" cursor.
2. Help: "After each day, the Day N results show every stand's price and units sold. The weather
   is drawn for each tournament day, the same for every player: …".
3. Every bar chart has the same fixed `height`.
4. The Practice "Charts and all days" expander is open when the run is complete.
5. The loan field is disabled like the Take loan button.

## Out of scope

- Rules, `logic.py`, `db.py`, tables.

## Done when

1. `inject_css` styles `button:disabled`.
2. The app has no "Market results" text and the Help mentions the weather of each tournament day.
3. Every `st.bar_chart` call passes `height`.
4. The Practice expander uses `expanded=run_complete`; the loan field has `disabled=`.
5. All existing tests still pass.
