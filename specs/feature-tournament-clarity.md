# Feature: clearer tournaments (weather, results, charts)

Owner: Filippo Venturini · Branch: `tournament-clarity` · Reviewer: Patrick

## Why

Patrick and Filippo played a whole tournament on 20 Nov:

1. **The weather never changes.** It is today's real Lisbon weather, so a tournament played in one
   afternoon has the same weather every day (in November almost always "Normal"), and the
   weather rule never matters.
2. **"Customers pay up to €4.00 / €8.00"** next to the selling price is not understood.
3. **An organiser who has not joined** already sees the weather and the days, as if they played.
4. **Results are hidden at the bottom** of a long card, and the results table mixes nine columns.
5. Practice has profit charts; tournaments have none.
6. How the **Coffee machine** works is not explained on the card.

## What

1. **Simulated weather per day.** `logic.simulated_weather(tournament_id, day)` returns
   `{"rain": bool, "hot": bool}`: rain 30%, hot 25%, normal 45%, never both. It is decided by the
   tournament id and the day only (`random.Random` with a fixed seed), so every player sees the
   same weather, and a new day can bring different weather. `tournament_screen` uses it when it
   is called without `fetch`; the result is saved as before, so the day close uses the same
   weather. `tournament_weather` and the real Lisbon fetch stay for the existing tests.
   The banner says the day and its effect: "Day 2 weather: Rain · Café reference €5.00 today".
2. **Selling price help instead of the third column.** The sell box shows Reference price and
   Your selling price; the "?" on the price explains: "Half of the customers pay up to €R, the
   other half up to €2R. Above €2R nobody buys. The cheapest stand sells first."
3. **Organiser who has not joined:** a short card: name, code, "Join this tournament" button,
   players and who is ready, Close day now, and the results. No weather, no parts 1–3.
4. **Results first.**
   - While playing: after the weather banner, "Day N results" shows the last closed day, one
     small table per product (Player · Price · Sold), then parts 1–3.
   - When the tournament is complete: no weather and no parts 1–3; part 4 "Results" shows the
     ranking first, then the last day tables and the charts.
   - Older days and the charts are in a "Charts and all days" expander while playing.
5. **Charts.** `logic.tournament_chart_data(days, player)` returns the player's gross profit
   per day by product and in total (same shape as `profit_chart_data`).
   `logic.tournament_players_chart_data(days)` returns each player's total gross profit per day
   (key = player name). Gross profit = round(units × price, 2) − round(units × unit cost, 2), as at
   the day close. Two bar charts: "Your gross profit per day by product" and "Gross profit per day:
   every player".
6. **Coffee machine** box note: "One-time €30.00: your Café reference becomes €5.00 for the rest
   of the tournament (customers pay up to €5.00 / €10.00)."

## Out of scope

- Changes to `db.py`, the tables, the market rule or the Practice screen.

## Done when

1. **Simulated weather:** the same tournament and day always give the same weather; rain and hot
   are never both true; over 20 tournaments × 5 days there is rain, hot and normal weather.
2. **Used by the screen:** `tournament_screen` without `fetch` returns and saves
   `simulated_weather(id, day)`; with `fetch` it still reads the fetched answer.
3. **Charts data:** for the team brief example (Ana 15 Café at €3.50, Bruno 5 at €6.00) Ana's
   chart data is Café 22.50, total 22.50, and the players' data is ana 22.50, bruno 20.00.
4. **Screen:** the app calls `tournament_screen` without the Lisbon fetch, has no "Customers pay up
   to" text, has a "Join this tournament" button and bar charts in `tournament_card`.
5. **No behaviour change elsewhere:** all existing tests still pass.
