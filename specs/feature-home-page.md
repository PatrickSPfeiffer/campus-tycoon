# Home page after sign-in

## Why
After signing in, the player lands straight in three tabs and has to guess where to start.
A home page with three clear choices makes the first steps obvious, for new players and
for the class during the live demo. (UI/UX criterion: direct workflows.)

## What
- [ ] After signing in, the app shows a home page with three large cards, side by side on a
      wide screen and stacked on a phone: Practice ("Play a five-day run on your own"),
      Tournaments ("Compete for the same customers with other players") and How to play
      ("The rules in two minutes"). Each card has an icon, a title, its sentence and a button.
- [ ] A card's button opens that screen. The screens are the existing practice_screen,
      tournaments_screen and help_screen, unchanged. Only the open screen is built.
- [ ] Each screen has a "Home" button at the top that returns to the home page.
- [ ] The open screen is kept in the page address (st.query_params, key "page", values
      practice, tournaments, help), so reloading the page stays on the same screen. An
      unknown value, or no value, shows the home page. Right after signing in, the home
      page is shown.
- [ ] The tabs are removed. The signed-in banner and the Sign out button stay as they are.
- [ ] The cards use the app's existing style (colours, card borders, icons).

## Out of scope
New game features, changes to the practice, tournament or help screens themselves,
showing game status on the cards, separate URLs per tournament.

## Done when
1. All existing tests pass unchanged, except test_tabs_run_only_when_open in tests/test_faster_screens.py, which is replaced by a test with the same intent (only the open screen is built).
2. By hand: after signing in, the home page shows the three cards; each button opens its screen.
3. By hand: "Home" returns to the home page from each screen.
4. By hand: reloading the browser on a screen stays on that screen; changing the address to
   ?page=nonsense shows the home page without an error.
5. By hand: buying, trading and a tournament Ready still work as before.
6. By hand, on a phone or a narrow window: the cards stack and stay readable.
