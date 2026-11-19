# Feature: fixes after the live test

Owner: Filippo Venturini · Branch: `fixes-after-live-test` · Reviewer: Patrick (new read function in `db.py`)

## Why

On 19 Nov we played the deployed app from start to end. Most things work, but:

1. **The organiser loses their tournament.** Creating a tournament does not join it, and the
   Tournaments screen only lists tournaments the player joined. An organiser who does not play
   never sees the tournament again: they cannot close a day or see the results. The team brief
   says the organiser "sees every player's results, and can close a day early. An organiser may
   also play in it."
2. **A wrong price is refused in silence.** The price fields have a minimum of €0.01, so a price
   of 0 only shows a small red icon and the button does nothing, with no message.
3. **The join code is easy to miss.** After creating a tournament, the code shows once, in small
   grey text, and the screen has no hint when the player has no tournament yet.
4. **How to play** does not say how the final gain is calculated (the number that decides the
   ranking) nor what the difficulty levels change.
5. Small look issues: an emoji in the Practice demand line (the UI spec says icons, no emoji),
   and table columns where numbers and headings are aligned differently.

## What

1. `db.get_organised_tournaments(db_path, organiser)`: one read of the tournaments a player
   created (id, name, code, day). Read only; no table change.
2. `logic.tournament_list(db_path, player)`: the tournaments the player joined **and** the ones
   they organise, each once, ordered by id, each with `playing` (True when the player has a
   stand). At most 2 statements. `logic.my_tournaments` stays as it is.
3. `logic.tournament_screen` also accepts the organiser who did not join: `stand` is `None`,
   `upgrades` is `[]`, and everything else (players, ready flags, day results, ranking) is the
   same. A player who is neither organiser nor member is still refused. Still at most 5
   statements.
4. The tournament card for an organiser who does not play shows the day, players and who is
   ready, "Close day now", Market results and the ranking, and a note: "You organise this
   tournament but do not play in it. To play, join it with the code …". No buy, price, upgrade or
   Ready controls.
5. Price fields have no minimum or maximum in the screen: `logic.check_price` decides, and its
   message ("Price must be more than €0.", …) is shown.
6. After creating a tournament, the code is shown large ("Share this code: ABC123"). With no
   tournament yet, the screen says "You have no tournaments yet. Create one or join one with a
   code."
7. How to play adds "Final gain" (final cash + leftover stock at unit cost − starting cash − loan
   to repay) and "Difficulty" (Easy €150, Normal €100, Hard €70 to start). The help cards are
   placed row by row, so on a phone they keep the reading order.
8. The demand line uses the app's info icon instead of an emoji; table cells and headings are all
   left aligned.

## Out of scope

- Changes to the rules, the tables or the Practice layout of `specs/feature-practice-layout.md`.
- Speed of the hosted database (Patrick is checking the Turso region).

## Done when

1. **Organised tournaments are listed:** an organiser who did not join sees their tournament with
   `playing` False; a player who joined and organises sees it once with `playing` True; others
   see nothing.
2. **Few reads:** `tournament_list` runs at most 2 statements.
3. **Organiser screen:** `tournament_screen` for a non-playing organiser has `stand` None,
   `upgrades` [], the players and the day results; after day 5 it has the ranking. An outsider is
   still refused, and it runs at most 5 statements.
4. **Organiser can close the day** from the same data: closing day 1 as a non-playing organiser
   works and the screen shows day 1 in `days`.
5. **Screen:** `app.py` uses `tournament_list`, has no `min_value` on the price fields, has no
   emoji in the Practice screen, and How to play has "Final gain" and "Difficulty".
6. **No behaviour change:** all existing tests still pass.
