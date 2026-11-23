"""Checks for specs/fix-ghost-callbacks.md — one test per 'Done when' line from 1 to 2."""

import ast
import pathlib

TREE = ast.parse(pathlib.Path("app.py").read_text(encoding="utf-8"))


def is_fragment(node):
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if getattr(target, "attr", None) == "fragment":
            return True
    return False


def fragments():
    return [node for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef) and is_fragment(node)]


def called(node, attribute):
    return [
        call for call in ast.walk(node)
        if isinstance(call, ast.Call) and getattr(call.func, "attr", None) == attribute
    ]


# 1. No rerun inside a fragment
def test_no_rerun_inside_fragments():
    names = {node.name for node in fragments()}
    assert {"practice_screen", "tournament_card", "practice_plan", "tournament_plan"} <= names
    for node in fragments():
        assert not called(node, "rerun"), node.name


# 2. Plan fragments only hold fields and the total
def test_plan_fragments_have_no_buttons():
    for node in fragments():
        if node.name in ("practice_plan", "tournament_plan"):
            assert not called(node, "button"), node.name
