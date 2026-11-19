"""Checks for specs/feature-easier-screens.md — one test per 'Done when' line from 1 to 6."""

import ast
import pathlib

import db
import logic

ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
NO_STOCK = {"Café": 0, "Croissant": 0, "Water": 0}
CATALOGUE_PRICES = {"Café": 4.0, "Croissant": 3.0, "Water": 1.2}


# 1. Warnings
def test_no_stock_warning():
    assert logic.trade_warnings(NO_STOCK, CATALOGUE_PRICES) == [
        "You have no stock, so this day sells nothing. Buy stock first."
    ]


def test_price_above_twice_the_reference_warning():
    stock = {"Café": 5, "Croissant": 0, "Water": 0}
    prices = dict(CATALOGUE_PRICES, Café=8.01)
    assert logic.trade_warnings(stock, prices) == ["Café: above €8.00, nobody will buy it."]


def test_price_below_unit_cost_warning():
    stock = {"Café": 0, "Croissant": 3, "Water": 0}
    prices = dict(CATALOGUE_PRICES, Croissant=1.0)
    assert logic.trade_warnings(stock, prices) == [
        "Croissant: below its unit cost (€1.50), every sale loses money."
    ]


def test_no_warning_for_a_sensible_day_and_for_products_without_stock():
    stock = {"Café": 10, "Croissant": 0, "Water": 10}
    prices = {"Café": 4.0, "Croissant": 100.0, "Water": 2.4}
    assert logic.trade_warnings(stock, prices) == []


# 2. References replace the catalogue
def test_references_replace_the_catalogue():
    stock = {"Café": 5, "Croissant": 0, "Water": 0}
    references = {"Café": 5.0, "Croissant": 3.0, "Water": 1.2}
    assert logic.trade_warnings(stock, dict(CATALOGUE_PRICES, Café=9.0), references) == []
    assert logic.trade_warnings(stock, dict(CATALOGUE_PRICES, Café=10.01), references) == [
        "Café: above €10.00, nobody will buy it."
    ]


# 3. Stand references
def test_stand_references():
    calm = {"rain": False, "hot": False}
    assert logic.stand_references(calm, []) == CATALOGUE_PRICES
    assert logic.stand_references({"rain": True, "hot": False}, [])["Café"] == 5.0
    assert logic.stand_references({"rain": False, "hot": True}, [])["Water"] == 1.5
    assert logic.stand_references(calm, ["Coffee machine"]) == dict(CATALOGUE_PRICES, Café=5.0)
    assert logic.stand_references({"rain": True, "hot": False}, ["Coffee machine"])["Café"] == 5.0


# 4. Same rule as the market
def play_one_day(db_path, weather, product, price, upgrade=None):
    tournament = logic.create_tournament(db_path, ORGANISER, "Solo Cup")
    tid = tournament["id"]
    logic.join_tournament(db_path, ANA, tournament["code"])
    db.save_tournament_weather(db_path, tid, 1, weather)
    if upgrade:
        logic.buy_tournament_upgrade(db_path, ANA, tid, upgrade)
    logic.buy_tournament_stock(db_path, ANA, tid, product, 10)
    logic.set_tournament_price(db_path, ANA, tid, product, price)
    closed = logic.close_tournament_day(db_path, ORGANISER, tid)
    return closed["by_player"][ANA][product]["units_sold"]


def test_hot_day_reference_matches_the_market(tmp_path):
    hot = {"rain": False, "hot": True}
    reference = logic.stand_references(hot, [])["Water"]
    # At the reference price all 10 budget customers buy (at €1.50 without heat only 5 would).
    assert play_one_day(tmp_path / "game.db", hot, "Water", reference) == 10


def test_coffee_machine_reference_matches_the_market(tmp_path):
    calm = {"rain": False, "hot": False}
    reference = logic.stand_references(calm, ["Coffee machine"])["Café"]
    assert play_one_day(tmp_path / "game.db", calm, "Café", reference, "Coffee machine") == 10


# 5. Split tournaments
def test_split_tournaments_keeps_order():
    rows = [{"id": 1, "day": 6}, {"id": 2, "day": 1}, {"id": 3, "day": 5}, {"id": 4, "day": 6}]
    active, finished = logic.split_tournaments(rows)
    assert [row["id"] for row in active] == [2, 3]
    assert [row["id"] for row in finished] == [1, 4]


# 6. Screen
def app_source():
    return pathlib.Path("app.py").read_text(encoding="utf-8")


def test_app_uses_the_new_helpers():
    called = {
        node.func.attr
        for node in ast.walk(ast.parse(app_source()))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "logic"
    }
    assert {"trade_warnings", "stand_references", "split_tournaments"} <= called


def test_practice_has_more_options_expanders():
    labels = [
        node.args[0].value
        for node in ast.walk(ast.parse(app_source()))
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "expander"
        and node.args and isinstance(node.args[0], ast.Constant)
    ]
    for label in ("Loan", "New run"):
        assert label in labels
