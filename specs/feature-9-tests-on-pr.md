# Feature 9: Tests on every pull request

## Why
Five people work on the code in parallel. Today "the tests pass" only means
they pass on the author's computer. We want a neutral machine to run the full
test suite on every pull request, so the reviewer sees a green or red check
before merging into main.

## What
- A GitHub Actions workflow in .github/workflows/tests.yml.
- It runs on every pull request (opened or updated).
- Steps: check out the code, install uv, install the project's dependencies
  from the lock file, run `uv run pytest`.
- It runs all the tests in the project, including the ones added later,
  without any change to the workflow.
- The run never uses the hosted Turso database: the workflow defines no
  TURSO_* variables and uses no secrets, so db.py falls back to SQLite and
  the tests keep using their temporary databases.

## Out of scope
- Making the check required before merging (branch protection: Patrick's
  decision, repository settings).
- Running on pushes to main, linting, coverage, automatic deployment.
- Testing Google sign-in or the Streamlit screens.

## Done when
- [ ] The workflow file exists and contains no secrets or TURSO_* values.
- [ ] Opening a pull request shows a "Tests" check that runs automatically.
- [ ] The check is green, and it runs the same number of tests as
      `uv run pytest` locally (35 at the time of this feature).
- [ ] On a throwaway branch (never merged), a deliberately failing test turns
      the check red; the branch is then deleted.
- [ ] README mentions that tests run automatically on every pull request.
