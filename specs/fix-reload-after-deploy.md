# Fix: the app works right after a merge (no "Reboot app")

Owner: Filippo Venturini · Branch: `reload-after-deploy` · Reviewer: Patrick

## Why

Twice after a merge (#39 and #51) the live app crashed (`AttributeError`, `TypeError`) until
someone pressed "Reboot app" on Streamlit Cloud, which only the app owner can do. Streamlit Cloud
runs the new `app.py` but keeps the old `db.py` and `logic.py` in memory, so the new screen calls
functions the old modules do not have yet.

## What

- `reloader.reload_changed(modules)`: for each module, if its file's modification time is not the
  one saved when it was loaded (or nothing is saved yet), reload it with `importlib.reload`; then
  save the time on the module. Returns the names reloaded.
- `app.py` calls `reloader.reload_changed([db, logic, mailer])` right after the imports, before
  anything else: `db` before `logic`, because `logic` uses `db`.
- A fresh app reloads each module once (harmless); after that only a deploy reloads them.

## Out of scope

- Any change to rules, screens or tables.

## Done when

1. A module whose file changed is reloaded and has the new code.
2. A module whose file did not change is not reloaded again.
3. `app.py` calls `reloader.reload_changed` once, right after the imports, with `db` before `logic`.
4. All existing tests still pass.
