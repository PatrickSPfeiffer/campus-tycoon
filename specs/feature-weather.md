# Feature: Weather events (tournaments)

Owner: Filippo Bortignon · Branch: `feature-weather`

## Why

Every tournament day has the same market. Real Lisbon weather makes days different:
rain makes Café customers pay more, heat makes Water customers pay more.
It is fair, because all players get the same weather.

## What

- `weather.py`: `fetch_lisbon_weather()` calls Open-Meteo with `urllib` (no key, no new library,
  10-second timeout) and returns the JSON. URL:
  `https://api.open-meteo.com/v1/forecast?latitude=38.72&longitude=-9.14&daily=precipitation_sum,temperature_2m_max&timezone=Europe/Lisbon&forecast_days=1`
- `logic.read_weather(data)` returns `{"rain": bool, "hot": bool}`.
  Rain: `precipitation_sum[0]` ≥ 1.0 mm. Hot: `temperature_2m_max[0]` ≥ 25 °C.
  Anything else in the answer raises `ValueError`.
- New table `tournament_weather (tournament_id, day, rain, hot)`, key `(tournament_id, day)`
  (approved by Patrick). In `db.py`: `get_tournament_weather` and `save_tournament_weather`.
- `logic.tournament_weather(db_path, tournament_id, fetch)`: if today's weather is saved, return it.
  Otherwise call `fetch`; if it fails, use no effect. Save it and return it.
- "Today" means the tournament's current `day` column.
- `tournament_weather` reads the current tournament day itself; its signature stays unchanged.
- If fetching fails, save `{"rain": False, "hot": False}` so the API is not called again that day.
- `fetch` returns raw Open-Meteo JSON; `tournament_weather` calls `read_weather` on it.
- Weather-adjusted reference prices are used only while calculating that day's sales; they are not saved.
- No effect is represented by `{"rain": False, "hot": False}`.
- At day close, the saved weather changes the reference price for every stand:
  rain → Café €5.00 (instead of €4.00), hot → Water €1.50 (instead of €1.20).
  It uses the `reference` option that `market_sales` already has. No saved weather → no effect.
- Tournament screen: one line, "Today in Lisbon: rain / hot / normal".

## Out of scope

Practice game, changing `market_sales`, other cities, retrying the API on the same day.

## Done when

1. Fake answer 3.2 mm, 18 °C → rain. Fake answer 0 mm, 27 °C → hot. A broken answer → `ValueError`.
2. The weather is fetched once per day: a second call the same day does not call fetch.
3. API down (a fake fetch that raises) → no effect, no crash.
4. One player, Café €5.00, stock 20: normal day sells 5, rainy day sells 10.
5. One player, Water €1.50, stock 20: normal day sells 5, hot day sells 10.
6. No test uses the internet; all old tests pass.
7. By hand: the tournament screen shows the weather, the same for every player.
