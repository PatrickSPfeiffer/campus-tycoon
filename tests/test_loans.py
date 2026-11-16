"""Checks for specs/feature-loans.md — one test per 'Done when' line from 1 to 8."""

import pytest

import logic

ANA = "ana@example.com"


def money(game):
    # Cash and debt together, to check that a refused loan changed nothing.
    return game["cash"], game["debt"]


def finish_run(db_path, player):
    # Trade the five days of the run with whatever stock the player has.
    for _ in range(logic.RUN_DAYS):
        logic.trade_day(db_path, player)


# 1. A new game has no debt and the usual final gain
def test_new_game_has_no_debt(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path, ANA)
    assert game["debt"] == 0.0
    assert logic.final_result(game)["gain"] == 0.0


# 2. A €50 loan adds cash and a €55 debt, and both are saved
def test_loan_of_50_adds_cash_and_debt_and_is_saved(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.take_loan(db_path, ANA, 50)
    assert money(game) == (150.0, 55.0)
    assert money(logic.load_game(db_path, ANA)) == (150.0, 55.0)


# 3. Limits: €1 → €1.10 debt, €50 accepted, €51 refused
def test_loan_limits(tmp_path):
    db_path = tmp_path / "game.db"
    assert logic.take_loan(db_path, ANA, 1)["debt"] == 1.10

    other = tmp_path / "other.db"
    assert logic.take_loan(other, ANA, 50)["debt"] == 55.0

    third = tmp_path / "third.db"
    with pytest.raises(ValueError):
        logic.take_loan(third, ANA, 51)


# 4. Only one loan per run
def test_second_loan_is_refused(tmp_path):
    db_path = tmp_path / "game.db"
    logic.take_loan(db_path, ANA, 20)
    with pytest.raises(ValueError, match="already have a loan"):
        logic.take_loan(db_path, ANA, 10)
    assert money(logic.load_game(db_path, ANA)) == (120.0, 22.0)


# 5. Wrong amounts are refused and change nothing
def test_wrong_amounts_are_refused(tmp_path):
    db_path = tmp_path / "game.db"
    for amount in [0, -5, 51, 2.5, True]:
        with pytest.raises(ValueError):
            logic.take_loan(db_path, ANA, amount)
    assert money(logic.load_game(db_path, ANA)) == (100.0, 0.0)


# 6. No loan after the run is complete
def test_no_loan_after_run_is_complete(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    finish_run(db_path, ANA)
    with pytest.raises(ValueError, match="run is complete"):
        logic.take_loan(db_path, ANA, 10)
    assert money(logic.load_game(db_path, ANA)) == (100.0, 0.0)


# 7. The final gain subtracts the debt
def test_final_gain_subtracts_debt(tmp_path):
    db_path = tmp_path / "game.db"
    logic.take_loan(db_path, ANA, 50)
    finish_run(db_path, ANA)
    game = logic.load_game(db_path, ANA)
    assert game["debt"] == 55.0
    final = logic.final_result(game)
    assert final["final_cash"] == 150.0
    assert final["gain"] == -5.0


# 8. A new run clears the debt
def test_new_run_clears_debt(tmp_path):
    db_path = tmp_path / "game.db"
    logic.take_loan(db_path, ANA, 50)
    game = logic.new_run(db_path, ANA, "Hard")
    assert money(game) == (70.0, 0.0)
    assert money(logic.load_game(db_path, ANA)) == (70.0, 0.0)
