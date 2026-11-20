"""Checks for specs/feature-tournament-layout-polish.md — one test per 'Done when' line from 1 to 4."""

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
        if isinstance(call, ast.Call)
        and (getattr(call.func, "attr", None) == attribute or getattr(call.func, "id", None) == attribute)
    ]


def first_text(call):
    # The first argument as written in the code, e.g. "Close day now" or f't{tournament_id}_buy'.
    return ast.unparse(call.args[0]) if call.args else ""


# 1. Styles
def test_practice_styles_also_cover_the_tournament_keys():
    css = ast.unparse(function("inject_css"))
    for key in (
        "st-key-tournament_part_",
        "st-key-tournament_box_",
        "st-key-tournament_plan_headings_",
        "st-key-tournament_buy_side_",
        "st-key-tournament_sell_side_",
        "st-key-tournament_part_trade_",
        "_ready_button",
        "_buy_button",
    ):
        assert key in css, key


# 2. Feedback
def test_every_flash_in_the_tournament_card_is_shown():
    card = function("tournament_card")
    set_scopes = {first_text(call) for call in calls(card, "flash")}
    shown_scopes = {first_text(call) for call in calls(card, "show_flash")}
    assert set_scopes
    assert set_scopes <= shown_scopes


# 3. Organiser
def test_close_day_for_playing_and_non_playing_organisers():
    card = function("tournament_card")
    plain = [call for call in calls(card, "button") if first_text(call) == "'Close day now'"]
    in_form = [call for call in calls(card, "form_submit_button") if first_text(call) == "'Close day now'"]
    assert plain and in_form


# 4. Parts
def test_four_numbered_parts_and_one_results_heading():
    card = function("tournament_card")
    numbers = {call.args[0].value for call in calls(card, "part_heading") if isinstance(call.args[0], ast.Constant)}
    assert numbers == {1, 2, 3, 4}
    source = ast.unparse(card)
    assert "At close" not in source
    assert "'Market results'" not in source
