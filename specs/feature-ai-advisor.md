# Feature: AI business advisor (practice mode)

## Why

Players need a simple hint about pricing while learning the practice game. An optional AI
advisor can suggest prices and explain them, without giving anyone an advantage in a tournament.

## What

- The practice screen has an **Ask the advisor** button. It is never shown in tournaments.
- The model is called only when the button is pressed: one OpenRouter call per click, never
  automatically. Streamlit reruns must not make extra calls.
- `advisor.py` is the only file that calls OpenRouter, like `db.py` is the only file that reads
  or writes the database.
- `advisor.ask_openrouter(prompt, api_key)` uses Python's `urllib.request` only (no new library),
  calls model `openrouter/free` with a 10-second timeout, and returns the reply text. An empty
  key raises `ValueError` and sends nothing.
- The secret is `OPENROUTER_API_KEY`. `app.py` reads it from `st.secrets`; the key is never written
  in code. Add the key with an empty value to `.streamlit/secrets.example.toml`.
- `logic.advisor_prompt(game)` contains the day, cash, stock, catalogue, and demand rule (10 / 5 /
  0), and asks for JSON only with a price and reason for Café, Croissant and Water.
- `logic.check_advice(text)` accepts only valid JSON with exactly those three products, where every
  price passes `check_price` and every reason is non-empty text. Before reading the JSON, it removes
  a leading ```json or ``` line and a trailing ``` line. Otherwise it raises `ValueError`.
- `logic.fallback_advice()` returns the plan B: price each product at twice its reference price,
  with one fixed reason.
- `logic.get_advice(game, ask)` calls `ask(advisor_prompt(game))`. If `ask` raises any error or
  the reply is rejected, it returns the fallback. The result is
  `{"source": "ai" or "fallback", "prices": {...}}`.
- Advice never changes the game.
- app.py shows a table with product, price and reason, labelled **AI suggestion** or
  **Basic tip (AI not available)**. The advice is plain text, never Markdown.

## Out of scope

- Tournaments or any advisor button in tournament screens.
- Applying suggested prices automatically.
- Keeping advice after the next click.
- Saving advice in the database; there are no table changes.
- Quantities to buy, chat, and paid models.

## Done when

1. A fake valid JSON answer for Café, Croissant and Water is accepted and returned as an AI
   suggestion with the three prices and reasons.
2. A fake answer with price `0` is rejected and produces the fallback.
3. A fake answer that is not JSON is rejected and produces the fallback.
4. A fake answer missing a product is rejected and produces the fallback.
5. If the fake `ask` raises an error, `get_advice` produces the fallback.
6. An empty API key raises `ValueError` before anything is sent.
7. The fallback prices are Café €8.00, Croissant €6.00 and Water €2.40, each with the fixed
   reason.
8. Calling `get_advice` leaves the game unchanged, including day, cash, stock and prices.
9. Tests use fake answers and fake `ask` functions only; tests never use the internet.
10. Manual check on the deployed app: the button appears and works in practice mode, is absent in
    tournaments, shows the correct label and plain-text table, and one click makes at most one
    model request.
11. **Code fences:** a valid answer wrapped in ```json ... ``` is accepted (source `"ai"`).
