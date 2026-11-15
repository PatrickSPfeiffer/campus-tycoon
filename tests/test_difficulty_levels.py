"""Checks for specs/feature-difficulty-levels.md — one test per 'Done when' line."""

import pytest

import db
import logic

ANA = "ana@example.com"


def read_rows(db_path, sql):
    with db.open_database(db_path) as conn:
        return conn.execute(sql).fetchall()


# 1. Easy
def test_easy_run_starts_with_150(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    game = logic.new_run(db_path, ANA, "Easy")
    assert game["cash"] == 150.0
    assert game["day"] == 1
    assert game["stock"] == {"Café": 0, "Croissant": 0, "Water": 0}
    assert logic.get_results(db_path, ANA) == []
    assert logic.load_game(db_path, ANA)["cash"] == 150.0


# 2. Hard
def test_hard_run_starts_with_70(tmp_path):
    db_path = tmp_path / "game.db"
    logic.new_run(db_path, ANA, "Hard")
    assert logic.load_game(db_path, ANA)["cash"] == 70.0


# 3. Normal is unchanged
def test_first_game_and_default_new_run_are_normal(tmp_path):
    db_path = tmp_path / "game.db"
    assert logic.load_game(db_path, ANA)["cash"] == 100.0
    logic.new_run(db_path, ANA, "Easy")
    logic.new_run(db_path, ANA)
    game = logic.load_game(db_path, ANA)
    assert game["cash"] == 100.0
    assert game["start_cash"] == 100.0


# 4. Rejected: unknown level changes nothing
def test_unknown_level_is_rejected_and_nothing_changes(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.buy(db_path, ANA, "Café", 10)
    logic.trade_day(db_path, ANA)
    before = logic.load_game(db_path, ANA)
    history_before = logic.get_results(db_path, ANA)

    with pytest.raises(ValueError):
        logic.new_run(db_path, ANA, "Impossible")

    assert logic.load_game(db_path, ANA) == before
    assert logic.get_results(db_path, ANA) == history_before


# 5. The gain uses the run's own starting cash
def test_gain_subtracts_the_levels_starting_cash(tmp_path):
    db_path = tmp_path / "game.db"
    logic.new_run(db_path, ANA, "Easy")
    logic.buy(db_path, ANA, "Café", 10)  # €20.00
    for _ in range(5):
        logic.trade_day(db_path, ANA)
    game = logic.load_game(db_path, ANA)
    assert logic.final_result(game) == {"final_cash": 170.0, "stock_at_cost": 0.0, "gain": 20.0}


# 6. Restart keeps the level, stored in games.start_cash
def test_level_survives_restart(tmp_path):
    db_path = tmp_path / "game.db"
    logic.new_run(db_path, ANA, "Hard")
    logic.buy(db_path, ANA, "Water", 10)  # €5.00
    for _ in range(5):
        logic.trade_day(db_path, ANA)

    game = logic.load_game(db_path, ANA)  # the same file opened again
    assert game["start_cash"] == 70.0
    assert logic.final_result(game)["gain"] == 7.0  # 77.00 − 70.00
    assert read_rows(db_path, "SELECT start_cash FROM games") == [(70.0,)]


# 7. Tournaments still start every stand with €100
def test_tournament_stand_still_starts_with_100(tmp_path):
    db_path = tmp_path / "game.db"
    logic.new_run(db_path, ANA, "Easy")
    tournament = logic.create_tournament(db_path, "org@example.com", "Friday cup")
    logic.join_tournament(db_path, ANA, tournament["code"])
    stand = logic.get_my_stands(db_path, ANA)[0]
    assert stand["cash"] == 100.0
