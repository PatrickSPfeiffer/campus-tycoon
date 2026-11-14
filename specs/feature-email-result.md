# Email the result

## Why
When a practice run ends, the player should get an email with their final result, so they can keep it. This feature sends an email through a team Gmail account. The run must finish normally even if the email cannot be sent. The email account password is a secret and must never be written in code, tests, logs or messages.

## What
1. When a practice run ends (the player's fifth "Trade one day"), the player receives one email with their final result: final cash, remaining stock at cost and overall gain or loss, taken from `logic.final_result(game)`. It is sent only to the signed-in player's own email address (`PLAYER`), never to anyone else.
2. In `logic.py`, a pure function `result_email_message(player, final)` returns the subject and the plain-text body (no network, no secrets). Subject: "Your Campus Tycoon result". Body: a greeting, the three values formatted with `€{value:.2f}`, and one closing line. The function raises ValueError if `player` is not a non-empty string.
3. In a new file `mailer.py` (the only file that talks to the email service), a plain function `send_result_email(player, final, smtp_factory=smtplib.SMTP_SSL)` builds the message with `logic.result_email_message` and `email.message.EmailMessage`, and sends it through smtp.gmail.com on port 465 with a 10 second timeout, logging in with the two secrets. It returns exactly one of these strings: "sent", "skipped" or "failed". It never raises an exception to its caller.
4. The two secrets are `EMAIL_ADDRESS` (the team Gmail address, also used as the sender) and `EMAIL_APP_PASSWORD` (the Gmail app password). `mailer.py` reads them like `db.read_settings` does for the database: environment variables first, then `st.secrets`; a missing secrets file or a missing value is the empty string.
5. If either secret is missing or empty, nothing is sent and the result is "skipped" (this is the normal case for teammates who do not have the secrets).
6. If the connection, login or sending fails for any reason (smtplib.SMTPException, OSError including timeouts), the result is "failed". Error text, the password and the address are never shown to the player and never logged. An invalid player is checked first: it gives "failed" even when the secrets are missing.
7. In `app.py`, in the "Trade one day" handler, after `logic.trade_day` succeeds, if the reloaded game is complete (`logic.is_run_complete`), the app calls `mailer.send_result_email` once, inside a spinner, and shows: success "Your result was emailed to <PLAYER>." for "sent"; info "Result email is not configured, so no email was sent." for "skipped"; warning "We could not send the email, but your result is saved." for "failed". Then the app continues exactly as before (`st.rerun()` shows the final result, so the message must be kept in `st.session_state` until the next screen is drawn). The run is saved before any email is attempted.
8. No table or column is added or changed: the email is attempted once, at the moment the run ends, because `trade_day` refuses any action after the fifth day.
9. `.streamlit/secrets.example.toml` gets the two new names with placeholder values only (never real values), above the [auth] header. `.env.example` is not changed: a security-pass test requires it to list only the two database names. The two email settings can still be given as environment variables.

## Out of scope
- Tournaments (no email when a tournament ends).
- Emails to other people, reports with charts or attachments, resending an email, retry logic, an unsubscribe option.
- Changing the final result rules, the database, the CSV report or the screens other than the message after the fifth day.
- Setting the secrets on Streamlit Cloud (Patrick does it when the feature is ready).

## Done when
- Tests in `tests/test_email_result.py` are written first and fail: message content and formatting (three values with two decimals); invalid player raises ValueError; with fake secrets and a fake SMTP factory the message is sent once, to the player's address only, with the right subject, using the secrets for login; missing or empty secrets give "skipped" and the fake is never called; a fake that raises SMTPException, OSError or TimeoutError gives "failed" and nothing is raised; the password never appears in the message or in the returned value; a simulated full run of five days finishes and its final result is unchanged whether the email works, is skipped or fails.
- No test opens a real network connection or reads a real secret.
- `uv run pytest` passes with all old tests unmodified.
- Manual test: with no secrets set, a practice run ends normally and shows the "not configured" message; with a deliberately wrong fake setting the run still ends and shows the warning.
- The diff touches only `logic.py`, `mailer.py`, `app.py`, `.streamlit/secrets.example.toml`, `tests/test_email_result.py` and the spec; no secret file is committed.
- The pull request passes the "Tests" check.
