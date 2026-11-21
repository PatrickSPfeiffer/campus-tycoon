"""Checks for specs/feature-tournament-pages.md — one test per 'Done when' line from 1 to 3."""

import ast
import pathlib

import logic

ROWS = [{"id": 3, "name": "Old"}, {"id": 20, "name": "20"}, {"id": 7, "name": "Mid"}]


# 1. Newest first
def test_newest_first():
    assert [row["id"] for row in logic.newest_first(ROWS)] == [20, 7, 3]
    assert [row["id"] for row in ROWS] == [3, 20, 7]   # the list given is not changed


# 2. Find the opened tournament
def test_find_tournament():
    assert logic.find_tournament(ROWS, "20")["name"] == "20"
    assert logic.find_tournament(ROWS, 7)["name"] == "Mid"
    assert logic.find_tournament(ROWS, "99") is None      # not one of the player's tournaments
    assert logic.find_tournament(ROWS, "abc") is None
    assert logic.find_tournament(ROWS, None) is None


# 3. Screen
def test_tournaments_screen_opens_one_tournament():
    source = pathlib.Path("app.py").read_text(encoding="utf-8")
    screen = next(
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "tournaments_screen"
    )
    text = ast.unparse(screen)
    assert "find_tournament" in text
    assert "newest_first" in text
    assert "'All tournaments'" in text
    assert 'st.query_params["tournament"]' in source
    row = next(
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "tournament_row"
    )
    assert "'Open'" in ast.unparse(row)
    assert "tournament_row" in text
