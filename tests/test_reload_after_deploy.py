"""Checks for specs/fix-reload-after-deploy.md — one test per 'Done when' line from 1 to 3."""

import ast
import importlib
import os
import pathlib
import sys

import reloader


def write_module(folder, value):
    path = folder / "sample_module.py"
    path.write_text(f"VALUE = {value!r}\n", encoding="utf-8")
    return path


# 1. A changed file is reloaded
def test_changed_module_is_reloaded(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(tmp_path))
    path = write_module(tmp_path, "old")
    sys.modules.pop("sample_module", None)
    module = importlib.import_module("sample_module")
    reloader.reload_changed([module])          # first time: reloaded once, time saved

    write_module(tmp_path, "new")
    later = os.path.getmtime(path) + 10
    os.utime(path, (later, later))             # the deploy writes a newer file
    importlib.invalidate_caches()
    assert reloader.reload_changed([module]) == ["sample_module"]
    assert module.VALUE == "new"


# 2. An unchanged file is not reloaded again
def test_unchanged_module_is_not_reloaded(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(tmp_path))
    write_module(tmp_path, "same")
    sys.modules.pop("sample_module", None)
    module = importlib.import_module("sample_module")
    assert reloader.reload_changed([module]) == ["sample_module"]
    assert reloader.reload_changed([module]) == []


# 3. The app reloads db before logic, before anything else uses them
def test_app_reloads_db_then_logic_first():
    tree = ast.parse(pathlib.Path("app.py").read_text(encoding="utf-8"))
    calls = [
        node for node in tree.body
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        and ast.unparse(node.value.func) == "reloader.reload_changed"
    ]
    assert len(calls) == 1
    names = [element.id for element in calls[0].value.args[0].elts]
    assert names.index("db") < names.index("logic")
    first_other_use = next(
        index for index, node in enumerate(tree.body)
        if isinstance(node, (ast.Assign, ast.FunctionDef)) or (
            isinstance(node, ast.Expr) and node is not calls[0]
        )
    )
    assert tree.body.index(calls[0]) < first_other_use
