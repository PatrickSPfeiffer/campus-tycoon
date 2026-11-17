# Spec: UI/UX polish and help

## Why
The app works but looks like a prototype: white default background, one long narrow column, small identical buttons, no navigation, no help for new players. The professor asked for a real application. This feature is 20% of the grade (Excel row "UI/UX polish and help").

## What
Only the look and the screen layout change. The rules and the data do not change.
1. Look: a dark espresso theme set in .streamlit/config.toml (dark background, amber accent, readable text), keeping the [client] section and existing showErrorDetails line unchanged. Page title, Material icon and wide layout set with st.set_page_config as the first Streamlit call in app.py.
1b. Design: a layered espresso gradient background; a glass banner with the app name, warm gradient title and tagline; status numbers and bordered areas as glass cards; products as cards with inline SVG icons; large amber-orange gradient primary buttons and outlined secondary buttons; tabs styled as gradient pills. Define the palette as CSS variables in one CSS block. Use Plus Jakarta Sans with a sans-serif fallback and respect reduced-motion preferences.
2. Header: app name and short tagline in the banner; signed-in player and Sign out button in the slim row underneath, with Sign out at the right edge.
3. Navigation: three tabs: Practice, Tournaments, How to play, with Material icons and no emoji. No more single long page.
4. Practice tab: status numbers (Cash, Progress, Loan) in a bordered card; actions (price, loan, buy) in bordered cards side by side; products table next to or above them; "Trade one day" is the main button, full width, placed right after the actions. Results (charts and day tables) in their own area below; new run, advisor and report download grouped and clearly secondary.
5. Tournaments tab: create and join side by side; each tournament in its own bordered card with weather, day, cash, stock and prices, upgrades, players and ready status, then Ready as the main button.
6. Buttons: one main (primary) button per card; secondary buttons stay default; dangerous actions (new run, close day) ask for confirmation.
7. Messages: success and error messages appear next to the button that caused them (toast for quick confirmations), in short plain sentences that say what to do next. No raw Python error text shown to players.
8. How to play: a short section with the goal, the five days, how demand works, loans, tournaments and upgrades, written in plain English.
9. Small fixes found in manual testing: "You are Ready" message must clear when the next day starts; price field must start at the product current price; Buy upgrade button must show Owned immediately; the screen must show the final state right after the last action without a manual refresh.

## Out of scope
- Any change to logic.py, db.py, the tables or the game rules.
- Custom JavaScript, new libraries, or a CSS framework. One single small CSS block (st.markdown inside one function in app.py) is allowed for the banner, cards and buttons that the theme cannot style.
- Live updates without refresh; chat; extra products.
- Changing, editing or skipping any existing test.

## Done when
- uv run pytest passes with the same tests as before (no test edited).
- Manual check on localhost: every screen in the screenshot list below looks consistent; no plain white default background; every button is where the player expects it.
- Manual check on the deployed app with two accounts: create, join, play a full tournament day, close, ranking.
- Invalid input (empty name, wrong join code, price 0, buying more than the cash) shows a clear message and never a Python error.
- The page is usable on a laptop screen and does not break on a narrow window.

## Screens to check by hand
Signed out; practice start; practice after buying; day result; end of run; advisor; loan; tournament create/join; tournament day with upgrades; Ready; closed day; final ranking; How to play.

## Delivery in 3 steps (each merged before the next)
1. Look: theme, page config, header, tabs, How to play skeleton.
2. Screens: Practice and Tournaments layout, cards, buttons, positions.
3. Messages and errors, small fixes, polish, test on the deployed app.
Status: step 1 merged; step 2 in progress (design system done, tournaments in progress)
