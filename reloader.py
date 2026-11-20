"""Reload our own modules after a deploy (specs/fix-reload-after-deploy.md).

After a merge, Streamlit Cloud runs the new app.py but keeps the old db.py and logic.py in
memory, so app.py can call a function that the old logic.py does not have yet (AttributeError,
TypeError) until someone presses "Reboot app". This reloads a module whenever its file is not
the one that was loaded.
"""

import importlib
import os


def reload_changed(modules):
    """Reload each module whose file changed since it was loaded; return their names.

    The first time (no saved time yet) the module is reloaded too: we cannot know whether the
    copy in memory is the current file. Order matters: pass db before logic, which uses it.
    """
    reloaded = []
    for module in modules:
        changed_at = os.path.getmtime(module.__file__)
        if getattr(module, "_loaded_mtime", None) != changed_at:
            module = importlib.reload(module)
            reloaded.append(module.__name__)
        module._loaded_mtime = changed_at
    return reloaded
