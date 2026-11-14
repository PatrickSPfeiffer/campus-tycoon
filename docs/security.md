# Security

How Campus Tycoon protects its secrets and its players, and what it does not do yet.
Written for the repository walkthrough: every point says where to look in the code.

## Secrets

- **What:** the Turso database URL and token, and the Google sign-in values (`[auth]`).
- **Where:** only in `.streamlit/secrets.toml` on a laptop and in the Streamlit Cloud settings
  for the deployed app. Both are outside git: `.gitignore` lists `.streamlit/secrets.toml`,
  `.env` and `*.db` (checked by `tests/test_security_pass.py`).
- **Templates:** `.streamlit/secrets.example.toml` and `.env.example` show the names with fake or
  empty values, so a new member knows what to fill in.
- **Tests never use real secrets:** a test's own database file never reads the settings
  (`db.connect`), and tests never call Turso or Google.
- **Error messages hide secrets:** "Database unavailable" never contains the URL or token
  (`db.connect_turso`), and `.streamlit/config.toml` sets `showErrorDetails = "none"`, so players
  never see a traceback. The team still sees errors in the terminal and in the Streamlit Cloud logs.

## Who can do what (access control)

- Nobody plays without signing in with Google; the player is the verified Google email, never
  typed in (`logic.player_from_user`).
- Every practice function reads and changes only that player's rows (`player` in every query).
- Tournaments: only players who joined can buy, set prices or press Ready on their own stand;
  only the organiser can close a day early; actions after day 5 are rejected (feature 11 tests).

## Input validation

All checks are in `logic.py`, so they also protect the app if `app.py` changes:

| Input | Rule |
|---|---|
| Quantity | positive whole number, affordable |
| Price | number, finite, more than €0, at most 2 decimals, at most €1000.00 (`MAX_PRICE`) |
| Product | one of the catalogue |
| Difficulty level | Easy, Normal or Hard |
| Tournament name | 1–40 characters: letters, digits, spaces and `- ' . ! ? & ( )`; no Markdown or HTML, which Streamlit would render as links for every player |
| Join code | exactly 6 letters or digits, checked before the database is read |

SQL injection: every query uses `?` parameters; no query is built by joining text with user input.

## Dependencies

- Only two libraries: `streamlit[auth]` and `libsql` (plus `pytest` for tests).
- Exact versions are pinned in `uv.lock`; GitHub Actions installs them with `uv sync --locked`
  and runs all tests on every pull request.
- Dependabot alerts are on (turned on by Patrick, repository admin): 0 open alerts on 14 Nov 2026.
- No automatic update pull requests (no `dependabot.yml`): an unplanned Streamlit or libsql
  upgrade could break sign-in or the database before the demo. If an alert appears, we update
  that one library by hand in a normal pull request, with the tests as proof.

## Known limits

- The tournament ranking function does not check who asks; the app only calls it for
  tournaments the player joined.
- Anyone with a Google account can sign in; there is no list of allowed players.
- Free Turso and Streamlit plans can pause; there is no backup of the hosted database.
