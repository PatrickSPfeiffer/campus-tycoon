"""Checks for specs/fix-ghost-elements.md — one test per 'Done when' line from 1 to 3."""

import ast
import pathlib

SOURCE = pathlib.Path("app.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def function(name):
    return next(
        node for node in ast.walk(TREE)
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def calls(node, attribute):
    return [
        call for call in ast.walk(node)
        if isinstance(call, ast.Call) and getattr(call.func, "attr", None) == attribute
    ]


# 1. Full reruns only
def test_no_fragment_reruns_left():
    reruns = calls(TREE, "rerun")
    assert reruns
    for call in reruns:
        assert not any(keyword.arg == "scope" for keyword in call.keywords), ast.unparse(call)


# 2. Space under the live total
def test_order_total_has_a_bottom_margin():
    css = ast.unparse(function("inject_css"))
    rule = css.split(".order-total {", 1)[1].split("}", 1)[0]
    assert "margin-bottom" in rule or "margin:" in rule


# 3. Both tournament charts have colours
def test_both_tournament_charts_have_colours():
    charts = calls(function("show_tournament_charts"), "bar_chart")
    assert len(charts) == 2
    for chart in charts:
        assert any(keyword.arg == "color" for keyword in chart.keywords), ast.unparse(chart)
