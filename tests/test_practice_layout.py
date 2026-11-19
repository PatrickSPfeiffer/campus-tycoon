"""Checks for specs/feature-practice-layout.md — the expected_profit examples and the screen."""

import ast
import pathlib

import logic


# The four expected_profit examples from the spec. No database: the game is a plain dict.
def test_expected_profit_for_a_mixed_day():
    game = logic.start_game()
    game["stock"] = {"Café": 10, "Croissant": 5, "Water": 0}
    game["price"]["Café"] = 4.00
    game["price"]["Croissant"] = 5.00
    assert logic.expected_profit(game) == {
        "by_product": {"Café": 20.00, "Croissant": 17.50, "Water": 0.00},
        "total": 37.50,
    }


def test_expected_profit_shows_a_loss_below_unit_cost():
    game = logic.start_game()
    game["stock"]["Café"] = 10
    game["price"]["Café"] = 1.50
    assert logic.expected_profit(game)["by_product"]["Café"] == -5.00


def test_expected_profit_is_zero_above_twice_the_reference():
    game = logic.start_game()
    game["stock"]["Café"] = 10
    game["price"]["Café"] = 9.00
    assert logic.expected_profit(game)["by_product"]["Café"] == 0.00


def test_expected_profit_of_a_new_game_is_zero():
    assert logic.expected_profit(logic.start_game()) == {
        "by_product": {"Café": 0.00, "Croissant": 0.00, "Water": 0.00},
        "total": 0.00,
    }


# The screen
def test_practice_screen_shows_expected_profit():
    source = pathlib.Path("app.py").read_text(encoding="utf-8")
    practice = next(
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "practice_screen"
    )
    called = {
        node.func.attr
        for node in ast.walk(practice)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "logic"
    }
    assert "expected_profit" in called
