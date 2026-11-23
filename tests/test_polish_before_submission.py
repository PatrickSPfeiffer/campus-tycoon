"""Checks for specs/polish-before-submission.md — one test per 'Done when' line from 1 to 4."""

import ast
import pathlib

SOURCE = pathlib.Path("app.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def function(name):
    return next(node for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef) and node.name == name)


def calls(node, attribute):
    return [
        call for call in ast.walk(node)
        if isinstance(call, ast.Call) and getattr(call.func, "attr", None) == attribute
    ]


def keywords(call):
    return {keyword.arg: ast.unparse(keyword.value) for keyword in call.keywords}


# 1. Disabled buttons look disabled
def test_disabled_buttons_are_styled():
    assert "button:disabled" in ast.unparse(function("inject_css"))


# 2. Help text
def test_help_matches_the_screen():
    assert "Market results" not in SOURCE
    help_source = ast.unparse(function("help_screen"))
    assert "Day N results" in help_source
    assert "each tournament day" in help_source


# 3. Same chart height
def test_every_bar_chart_has_a_height():
    charts = calls(TREE, "bar_chart")
    assert len(charts) >= 4
    for chart in charts:
        assert "height" in keywords(chart), ast.unparse(chart)


# 4. Practice charts open at the end, loan field disabled
def test_practice_end_and_loan_field():
    screen = function("practice_screen")
    expanders = [keywords(call) for call in calls(screen, "expander")]
    assert any(item.get("expanded") == "run_complete" for item in expanders)
    loan_fields = [call for call in calls(screen, "number_input") if keywords(call).get("key") == "'loan_amount'"]
    assert loan_fields and "disabled" in keywords(loan_fields[0])
