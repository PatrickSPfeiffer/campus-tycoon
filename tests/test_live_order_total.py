"""Checks for specs/feature-live-order-total.md — one test per 'Done when' line from 1 to 2."""

import ast
import pathlib

TREE = ast.parse(pathlib.Path("app.py").read_text(encoding="utf-8"))


def function(name):
    return next(
        node for node in ast.walk(TREE)
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def is_fragment(node):
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if getattr(target, "attr", None) == "fragment":
            return True
    return False


def called_names(node):
    return {
        getattr(call.func, "id", None) or getattr(call.func, "attr", None)
        for call in ast.walk(node) if isinstance(call, ast.Call)
    }


# 1. Plan parts are fragments with the live total
def test_plan_parts_are_fragments_with_the_total():
    for name in ("practice_plan", "tournament_plan"):
        plan = function(name)
        assert is_fragment(plan), name
        assert "order_total" in called_names(plan), name


# 2. The total uses the rule in logic, and no form holds the How many fields
def test_total_uses_logic_and_no_form_holds_the_quantities():
    assert "order_cost" in ast.unparse(function("order_total"))
    for node in ast.walk(TREE):
        if isinstance(node, ast.With):
            for item in node.items:
                call = item.context_expr
                if isinstance(call, ast.Call) and getattr(call.func, "attr", None) == "form":
                    assert "How many" not in ast.unparse(node), ast.unparse(call)
