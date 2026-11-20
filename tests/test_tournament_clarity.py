"""Checks for specs/feature-tournament-clarity.md — one test per 'Done when' line from 1 to 4."""

import ast
import pathlib

import db
import logic

ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"


def tournament_with_players(db_path):
    tournament = logic.create_tournament(db_path, ORGANISER, "Autumn Cup")
    for player in (ANA, BRUNO):
        logic.join_tournament(db_path, player, tournament["code"])
    return tournament["id"]


# 1. Simulated weather
def test_simulated_weather_is_stable_and_never_rain_and_hot():
    for tournament_id in range(1, 21):
        for day in range(1, logic.RUN_DAYS + 1):
            weather = logic.simulated_weather(tournament_id, day)
            assert weather == logic.simulated_weather(tournament_id, day)
            assert set(weather) == {"rain", "hot"}
            assert not (weather["rain"] and weather["hot"])


def test_simulated_weather_changes_between_days():
    kinds = set()
    for tournament_id in range(1, 21):
        for day in range(1, logic.RUN_DAYS + 1):
            weather = logic.simulated_weather(tournament_id, day)
            kinds.add("rain" if weather["rain"] else "hot" if weather["hot"] else "normal")
    assert kinds == {"rain", "hot", "normal"}


# 2. Used by the screen
def test_screen_without_fetch_uses_and_saves_the_simulated_weather(tmp_path):
    db_path = tmp_path / "game.db"
    tid = tournament_with_players(db_path)
    screen = logic.tournament_screen(db_path, ANA, tid)
    assert screen["weather"] == logic.simulated_weather(tid, 1)
    assert db.get_tournament_weather(db_path, tid, 1) == logic.simulated_weather(tid, 1)


def test_screen_with_fetch_still_reads_the_answer(tmp_path):
    db_path = tmp_path / "game.db"
    tid = tournament_with_players(db_path)

    def fetch():
        return {"daily": {"precipitation_sum": [3.0], "temperature_2m_max": [18.0]}}

    assert logic.tournament_screen(db_path, ANA, tid, fetch)["weather"] == {"rain": True, "hot": False}


# 3. Charts data
def test_chart_data_for_the_brief_example(tmp_path):
    db_path = tmp_path / "game.db"
    tid = tournament_with_players(db_path)
    db.save_tournament_weather(db_path, tid, 1, {"rain": False, "hot": False})
    logic.buy_tournament_stock(db_path, ANA, tid, "Café", 15)
    logic.set_tournament_price(db_path, ANA, tid, "Café", 3.5)
    logic.buy_tournament_stock(db_path, BRUNO, tid, "Café", 10)
    logic.set_tournament_price(db_path, BRUNO, tid, "Café", 6.0)
    logic.close_tournament_day(db_path, ORGANISER, tid)

    days = logic.tournament_screen(db_path, ANA, tid)["days"]
    assert logic.tournament_chart_data(days, ANA) == {
        "Day": [1], "Café": [22.5], "Croissant": [0.0], "Water": [0.0], "Total": [22.5],
    }
    assert logic.tournament_players_chart_data(days) == {"Day": [1], "ana": [22.5], "bruno": [20.0]}


def test_chart_data_is_empty_before_the_first_close():
    assert logic.tournament_chart_data([], ANA) == {
        "Day": [], "Café": [], "Croissant": [], "Water": [], "Total": [],
    }
    assert logic.tournament_players_chart_data([]) == {"Day": []}


# 4. Screen
def test_tournament_card_uses_the_new_pieces():
    source = pathlib.Path("app.py").read_text(encoding="utf-8")
    assert "fetch_lisbon_weather" not in source
    assert "Customers pay up to" not in source
    card = next(
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "tournament_card"
    )
    card_source = ast.unparse(card)
    assert "Join this tournament" in card_source
    assert "show_results" in card_source
    charts = next(
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "show_tournament_charts"
    )
    assert "bar_chart" in ast.unparse(charts)
    assert "tournament_chart_data" in ast.unparse(charts)
