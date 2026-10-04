# Campus Tycoon

Product brief: docs/. Task specs: specs/.

## Running things
- App: uv run streamlit run app.py
- Tests: uv run pytest

## Structure
- app.py: Streamlit screens only. No rules here.
- logic.py: the rules and calculations.
- db.py: the only file that reads or writes the SQLite database (data/game.db).
- tests/: pytest. Every test uses its own temporary database, never data/game.db.

## How to work
- Build each spec on a branch named after it, e.g. first-feature. Never commit feature work to main.
- After every change, run the tests for the task and paste the final output. The output is the proof.
- Write tests only when the task asks for tests. After that, never edit, delete or skip anything in tests/; if a test seems wrong, say so and stop.
- One spec per task. Do not build anything listed under Out of scope.
- Keep it simple: plain functions, the standard sqlite3 module, no extra libraries. I must be able to explain every line.
