# Campus Tycoon

Product briefs: docs/. The original brief is the BRD file; docs/team-brief.md describes
the team project and wins where the two differ. Task specs: specs/.

## Running things
- App: uv run streamlit run app.py
- Tests: uv run pytest

## Structure
- app.py: Streamlit screens only. No rules here.
- logic.py: the rules and calculations.
- db.py: the only file that reads or writes the database.
- tests/: pytest. Every test uses its own temporary local database, never the real one.

## How to work
- Build each spec on a branch named after it, e.g. feature-tournaments. Never commit feature work to main.
- After every change, run the tests for the task and paste the final output. The output is the proof.
- Write tests only when the task asks for tests. After that, never edit, delete or skip anything in tests/; if a test seems wrong, say so and stop.
- One spec per task. Do not build anything listed under Out of scope.
- Keep it simple: plain functions, so every team member can explain every line.
- Add a library only when the spec names it. Keep dependencies few, and let uv pin them in uv.lock.
- Money is a float. Round every money calculation to 2 decimals with round(value, 2).
- The database tables may change between features. Never write code to upgrade old databases; we reset the data ourselves.

## Team rules
- Only the owner of the data structure changes database tables. If a task needs a new table or column, say so and stop.
- Every pull request is reviewed by another team member before it is merged.
- Change this file only through a pull request, like any other file.

## Secrets
- Secrets (API keys, database connection strings, login provider keys) are read from environment variables or .streamlit/secrets.toml, never written in the code.
- Never commit .env or .streamlit/secrets.toml. Before the first commit that uses a secret, confirm that git ignores the secrets file.
- Tests never call real external services (hosted database, Google sign-in, APIs); they use fakes or a local database.
