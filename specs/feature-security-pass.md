# Feature: security pass

Owner: Filippo Venturini · Branch: `feature-security-pass`

## Why

Security is 10% of the grade: "access control and input validation are enforced; dependencies
are minimal, pinned, and without known vulnerabilities". A review of the code found it in good
shape (secrets only in `.streamlit/secrets.toml` and git-ignored, parameterised SQL, `uv.lock`,
tests on every pull request), with a few gaps that a user of the public app could exploit.

## What

1. **Tournament names (S1):** only letters (also accented), digits, spaces and `- ' . ! ? & ( )`.
   Today any text is accepted, and Streamlit renders Markdown: a name like
   `[click here](http://fake-site)` would become a link shown to every player.
2. **Join codes (S2):** after trimming and upper-casing, a code must be exactly 6 letters or
   digits (the format the app generates). Anything else is rejected before the database is read.
3. **Prices (S3):** practice and tournament prices must be finite numbers and at most €1000.00
   (`logic.MAX_PRICE`). Today `inf` is accepted and shown as "€inf".
4. **Error details (S4):** `.streamlit/config.toml` sets `showErrorDetails = "none"`, so the public
   app never shows a traceback (file paths, code) to players.
5. **Templates and documentation (S5):** `.env.example` lists the environment variable names with
   empty values; `docs/security.md` explains where secrets live, who can do what, what is
   validated, how dependencies are pinned, and the known limits (for the walkthrough).

Every rejected action raises ValueError with a clear message and changes nothing.

## Out of scope

- Changing database tables, the sign-in flow or the tournament rules.
- Turning on Dependabot (needs repository admin: Patrick).
- Rewriting git history.

## Done when

1. **Names accepted:** "Autumn Cup", "Café Cup", "Nova's Cup (2026)!" create a tournament.
2. **Names rejected:** "[click](http://x.y)", "<b>hi</b>", "**bold**", "`code`" raise ValueError
   mentioning the name; no tournament is saved.
3. **Codes rejected:** "ABC", 1000 letters, "AB C12", "ABC12!" raise ValueError mentioning the code;
   a well-formed but unknown code ("NOPE99") is still "not found"; a lowercase valid code with spaces still joins.
4. **Prices:** practice and tournament: 1000.00 accepted; 1000.01, `inf` and `nan` rejected and
   the saved price is unchanged; all existing price messages stay the same.
5. **Config:** `.streamlit/config.toml` has `[client] showErrorDetails = "none"`.
6. **Secrets stay out of git:** `.gitignore` lists `.streamlit/secrets.toml`, `.env` and `*.db`;
   `.env.example` has `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` with empty values.

Check: `uv run pytest` is green, also in GitHub Actions on the pull request.
