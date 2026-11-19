"""Checks for specs/feature-fixes-after-live-test.md — one test per 'Done when' line from 1 to 5."""

import ast
import pathlib
import re
import sqlite3

import pytest

import db
import logic

ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"
OUTSIDER = "outsider@example.com"
NO_WEATHER = {"daily": {"precipitation_sum": [0.0], "temperature_2m_max": [18.0]}}


def fetch():
    return NO_WEATHER


def tournament_with_players(db_path, organiser=ORGANISER, players=(ANA, BRUNO), name="Autumn Cup"):
    tournament = logic.create_tournament(db_path, organiser, name)
    for player in players:
        logic.join_tournament(db_path, player, tournament["code"])
    return tournament


@pytest.fixture
def count_statements(monkeypatch):
    statements = []
    real_connect = sqlite3.connect

    def counting_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        conn.set_trace_callback(statements.append)
        return conn

    monkeypatch.setattr(db.sqlite3, "connect", counting_connect)
    return statements


def queries(statements):
    return [
        sql for sql in statements
        if sql.split()[0].upper() in ("SELECT", "INSERT", "UPDATE", "DELETE")
        and "sqlite_master" not in sql
    ]


# 1. Organised tournaments are listed
def test_tournament_list_includes_organised_and_joined_tournaments(tmp_path):
    db_path = tmp_path / "game.db"
    organised = tournament_with_players(db_path)                       # organiser does not play
    played = tournament_with_players(db_path, organiser=ANA, players=(ANA,), name="Ana Cup")
    joined = tournament_with_players(db_path, players=(ORGANISER,), name="Own Cup")

    rows = logic.tournament_list(db_path, ORGANISER)
    assert [(row["id"], row["playing"]) for row in rows] == [
        (organised["id"], False), (joined["id"], True),
    ]
    assert rows[0]["name"] == "Autumn Cup" and rows[0]["code"] == organised["code"]
    assert [(row["id"], row["playing"]) for row in logic.tournament_list(db_path, ANA)] == [
        (organised["id"], True), (played["id"], True),
    ]
    assert logic.tournament_list(db_path, OUTSIDER) == []


def test_tournament_list_keeps_the_day_for_splitting(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = tournament_with_players(db_path)
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = 6 WHERE id = ?", (tournament["id"],))
    active, finished = logic.split_tournaments(logic.tournament_list(db_path, ORGANISER))
    assert active == [] and [row["id"] for row in finished] == [tournament["id"]]


# 2. Few reads
def test_tournament_list_reads_little(tmp_path, count_statements):
    db_path = tmp_path / "game.db"
    for _ in range(4):
        tournament_with_players(db_path)
    logic.tournament_list(db_path, ORGANISER)
    count_statements.clear()
    logic.tournament_list(db_path, ORGANISER)
    assert len(queries(count_statements)) <= 2


# 3. Organiser screen
def test_screen_for_an_organiser_who_does_not_play(tmp_path, count_statements):
    db_path = tmp_path / "game.db"
    tournament = tournament_with_players(db_path)
    tid = tournament["id"]
    logic.ready_tournament(db_path, BRUNO, tid)

    logic.tournament_screen(db_path, ORGANISER, tid, fetch)  # saves the weather of day 1
    count_statements.clear()
    screen = logic.tournament_screen(db_path, ORGANISER, tid, fetch)
    assert len(queries(count_statements)) <= 5
    assert screen["stand"] is None
    assert screen["upgrades"] == []
    assert screen["organiser"] == ORGANISER
    assert screen["players"] == logic.tournament_status(db_path, ORGANISER, tid)["players"]
    assert screen["days"] == [] and screen["ranking"] is None

    with pytest.raises(ValueError, match=re.escape("You have not joined this tournament.")):
        logic.tournament_screen(db_path, OUTSIDER, tid, fetch)


def test_organiser_sees_the_ranking_at_the_end(tmp_path):
    db_path = tmp_path / "game.db"
    tid = tournament_with_players(db_path)["id"]
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = 6 WHERE id = ?", (tid,))
    screen = logic.tournament_screen(db_path, ORGANISER, tid, fetch)
    assert screen["ranking"] == logic.tournament_ranking(db_path, tid)


# 4. Organiser can close the day
def test_non_playing_organiser_closes_the_day_and_sees_it(tmp_path):
    db_path = tmp_path / "game.db"
    tid = tournament_with_players(db_path)["id"]
    logic.buy_tournament_stock(db_path, ANA, tid, "Café", 5)
    logic.close_tournament_day(db_path, ORGANISER, tid)
    screen = logic.tournament_screen(db_path, ORGANISER, tid, fetch)
    assert screen["day"] == 2
    assert [day["day"] for day in screen["days"]] == [1]
    assert screen["days"][0]["stands"][0]["units_sold"]["Café"] == 5


# 5. Screen
def app_tree():
    return ast.parse(pathlib.Path("app.py").read_text(encoding="utf-8"))


def logic_calls(tree):
    return {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "logic"
    }


def test_screen_lists_organised_tournaments():
    assert "tournament_list" in logic_calls(app_tree())


def test_price_fields_leave_the_check_to_logic():
    for node in ast.walk(app_tree()):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "number_input":
            label = ast.unparse(node.args[0]) if node.args else ""
            if "price" in label.lower() or "(€)" in label and "loan" not in label.lower():
                keywords = {keyword.arg for keyword in node.keywords}
                assert "min_value" not in keywords, label
                assert "max_value" not in keywords, label


def test_practice_screen_has_no_emoji():
    tree = app_tree()
    practice = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "practice_screen"
    )
    source = ast.unparse(practice)
    assert not re.search("[\U0001F300-\U0001FAFF☀-➿]", source)


def test_how_to_play_explains_gain_and_difficulty():
    tree = app_tree()
    help_screen = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "help_screen"
    )
    source = ast.unparse(help_screen)
    assert "Final gain" in source
    assert "Difficulty" in source
