# Feature 8: sign-in with Google

## Why
Tournaments need to know who each player is, and each player must only see and change
their own game (access control, in the security criterion). Sign-in replaces the fixed
"guest" player. Nova accounts were tested first, but Nova blocks students from
registering apps, so the app uses Google accounts.

## What
- [ ] Players sign in with Google through Streamlit's st.login. The Authlib library that
      st.login needs is added with uv and pinned in uv.lock.
- [ ] Before signing in, the app shows only a short welcome and a "Sign in with Google"
      button: no game data.
- [ ] After signing in, the player is the email Google returns (st.user.email). A small
      function in logic.py turns the signed-in user into the player, and rejects a user
      who is not signed in or has no email.
- [ ] The email is cleaned before it becomes the player: spaces are trimmed and it is
      made lowercase, so "  Ana@Example.com " becomes "ana@example.com".
- [ ] If Google says the email is not verified (email_verified is present and False),
      the user is rejected. If email_verified is missing, the user is accepted.
- [ ] app.py never uses a fixed player and has no field where a player can type an email,
      so nobody can act as another player.
- [ ] A "Sign out" button returns to the welcome screen.
- [ ] The login settings live in the [auth] section of .streamlit/secrets.toml and in the
      Streamlit settings, never in the code. .streamlit/secrets.example.toml shows the
      [auth] section with placeholder values.

## Out of scope
Microsoft or Nova sign-in, tournament roles, a profile page, deleting accounts,
moving the old "guest" game to a real account.

## Done when
1. The function that turns the signed-in user into the player returns the email when
   the user is signed in, and rejects a user who is not signed in, or whose email is
   missing or empty. (Tested with fake users, without Google.)
2. The 30 existing tests pass unchanged.
3. By hand, on the laptop: the app first shows only the welcome and the button; signing in
   with Google opens a new game (€100, day 1); after playing a day, signing out and in
   again shows the same game.
4. By hand, with a second Google account: it gets its own new game, and the first
   account's game is unchanged. The players table shows both emails.
5. By hand, on the deployed app after the merge: check 3 again on the public URL.
6. All tests green, on branch feature-8-sign-in, pushed.
