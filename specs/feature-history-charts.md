# Feature: history charts (practice mode)

Owner: Filippo Venturini · Branch: `feature-history-charts`

## Why

Today the Results section is one table per day. A player cannot see at a glance which
product earns money and how the run is going. Two charts make the history readable in
seconds and help in the live demo (UI/UX, Scope).

## What

- A pure function `logic.profit_chart_data(results)` turns the saved history
  (the list returned by `logic.get_results`) into chart data:
  `{"Day": [...], "Café": [...], "Croissant": [...], "Water": [...], "Total": [...]}`.
  - One value per completed day, days in ascending order.
  - Each product list holds that product's gross profit for the day; a product missing
    from a day counts as 0.00.
  - "Total" is the day's total gross profit. Every value is a float rounded to 2 decimals.
  - Products follow the catalogue order in `PRODUCTS`.
- In `app.py`, under Results:
  - "Gross profit per day by product": a bar chart with the three products.
  - "Total gross profit per day": a line chart.
  - With no completed day yet: the message "Trade a day to see your charts." and no chart.
- The charts read only the signed-in player's own results (access rule: a player only sees
  their own practice run).

## Out of scope

- Charts for tournaments (their results are another table; possible later feature).
- New tables or columns, new libraries (Streamlit's built-in charts are enough).
- Changing how results are calculated or saved.

## Done when

1. **No history:** `profit_chart_data([])` gives the five keys, each with an empty list.
2. **Accepted:** buy 10 Café (€20) and 10 Water (€5), keep reference prices, trade two days →
   Day [1, 2], Café [20.0, 0.0], Croissant [0.0, 0.0], Water [7.0, 0.0], Total [27.0, 0.0].
3. **Order:** the keys are Day, Café, Croissant, Water, Total; days given as 2, 1 come out as 1, 2.
4. **Edge case:** a day without a product line gives 0.0 for that product.
5. **Rounding:** gross profits 0.1 and 0.2 give a Total of 0.3 (not 0.30000000000000004).
6. **Privacy:** after Bruno trades a day, Ana's chart data is still empty.
7. **By hand:** in the app the charts appear after day 1, update after each trade, and disappear
   after "Start a new run".

Check: `uv run pytest` is green, also in GitHub Actions on the pull request.
