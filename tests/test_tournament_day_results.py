"""Checks for specs/feature-tournament-day-results.md — one test per 'Done when' line from 1 to 6."""

import ast
import pathlib
import sqlite3

import pytest

import db
import logic

ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"
NO_WEATHER = {"daily": {"precipitation_sum": [0.0], "temperature_2m_max": [18.0]}}


def fetch():
    return NO_WEATHER


def setup_tournament(db_path):
    tournament = logic.create_tournament(db_path, ORGANISER, "Autumn Cup")
    for player in (ANA, BRUNO):
        logic.join_tournament(db_path, player, tournament["code"])
    return tournament["id"]


def play_brief_example_day(db_path, tid):
    # Team brief example: Ana €3.50 with 15 Café, Bruno €6.00 with 10 Café → Ana sells 15, Bruno 5.
    logic.buy_tournament_stock(db_path, ANA, tid, "Café", 15)
    logic.set_tournament_price(db_path, ANA, tid, "Café", 3.5)
    logic.buy_tournament_stock(db_path, BRUNO, tid, "Café", 10)
    logic.set_tournament_price(db_path, BRUNO, tid, "Café", 6.0)
    logic.ready_tournament(db_path, ANA, tid)
    return logic.ready_tournament(db_path, BRUNO, tid)


# 1. Results after a day
def test_results_after_a_day_show_every_stand(tmp_path):
    db_path = tmp_path / "game.db"
    tid = setup_tournament(db_path)
    logic.tournament_screen(db_path, ANA, tid, fetch)  # saves the weather of day 1
    play_brief_example_day(db_path, tid)

    days = logic.tournament_screen(db_path, BRUNO, tid, fetch)["days"]
    assert [day["day"] for day in days] == [1]
    ana, bruno = days[0]["stands"]
    assert ana["player"] == ANA
    assert ana["price"] == {"Café": 3.5, "Croissant": 3.0, "Water": 1.2}
    assert ana["units_sold"] == {"Café": 15, "Croissant": 0, "Water": 0}
    assert bruno["player"] == BRUNO
    assert bruno["price"]["Café"] == 6.0
    assert bruno["units_sold"]["Café"] == 5


# 2. Order
def test_days_oldest_first_and_stands_in_seat_order(tmp_path):
    db_path = tmp_path / "game.db"
    tid = setup_tournament(db_path)
    play_brief_example_day(db_path, tid)
    logic.close_tournament_day(db_path, ORGANISER, tid)

    days = logic.tournament_screen(db_path, ANA, tid, fetch)["days"]
    assert [day["day"] for day in days] == [1, 2]
    for day in days:
        assert [stand["player"] for stand in day["stands"]] == [ANA, BRUNO]
    # Day 2: Ana had no stock left, Bruno sold his last 5 Café.
    assert days[1]["stands"][0]["units_sold"]["Café"] == 0
    assert days[1]["stands"][1]["units_sold"]["Café"] == 5


# 3. Nothing before day 1 closes
def test_no_days_before_the_first_close(tmp_path):
    db_path = tmp_path / "game.db"
    tid = setup_tournament(db_path)
    assert logic.tournament_screen(db_path, ANA, tid, fetch)["days"] == []


# 4. No private data
def test_day_results_show_no_cash_or_stock(tmp_path):
    db_path = tmp_path / "game.db"
    tid = setup_tournament(db_path)
    play_brief_example_day(db_path, tid)
    for stand in logic.tournament_screen(db_path, ANA, tid, fetch)["days"][0]["stands"]:
        assert set(stand) == {"player", "name", "price", "units_sold"}
        assert stand["name"] == logic.player_name(stand["player"])


# 5. Still few reads
def test_screen_with_results_still_reads_little(tmp_path, monkeypatch):
    db_path = tmp_path / "game.db"
    tid = setup_tournament(db_path)
    play_brief_example_day(db_path, tid)
    logic.tournament_screen(db_path, ANA, tid, fetch)

    statements = []
    real_connect = sqlite3.connect

    def counting_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        conn.set_trace_callback(statements.append)
        return conn

    monkeypatch.setattr(db.sqlite3, "connect", counting_connect)
    logic.tournament_screen(db_path, ANA, tid, fetch)
    queries = [
        sql for sql in statements
        if sql.split()[0].upper() in ("SELECT", "INSERT", "UPDATE", "DELETE")
        and "sqlite_master" not in sql
    ]
    assert len(queries) <= 5


# 6. Screen
def tournament_card_source():
    tree = ast.parse(pathlib.Path("app.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "tournament_card":
            return node
    pytest.fail("app.py has no tournament_card function")


def test_tournament_card_has_refresh_button():
    labels = [
        node.args[0].value
        for node in ast.walk(tournament_card_source())
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "button"
        and node.args and isinstance(node.args[0], ast.Constant)
    ]
    assert "Refresh" in labels


def test_ready_shows_the_closed_day():
    source = ast.unparse(tournament_card_source())
    assert "ready_tournament" in source
    assert 'closed_day"]' in source or "closed_day']" in source
