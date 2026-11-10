import pytest

import logic

PLAYER = "ana@example.com"


def test_buy_within_budget_then_reject_unaffordable(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 100.0
    assert isinstance(game["cash"], float)
    assert game["stock"]["Café"] == 0
    assert game["day"] == 1

    game = logic.buy(db_path, PLAYER, "Café", 10)
    assert game["cash"] == 80.0
    assert isinstance(game["cash"], float)
    assert game["stock"]["Café"] == 10

    with pytest.raises(ValueError):
        logic.buy(db_path, PLAYER, "Café", 41)

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 80.0
    assert game["stock"]["Café"] == 10


def test_reject_invalid_quantities(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)

    for quantity in [0, -5, 2.5]:
        with pytest.raises(ValueError):
            logic.buy(db_path, PLAYER, "Café", quantity)

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 100.0
    assert game["stock"]["Café"] == 0


def test_trade_one_day(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)

    result = logic.trade_day(db_path, PLAYER)
    assert result["day"] == 1
    assert result["by_product"]["Café"]["units_sold"] == 10
    assert result["by_product"]["Café"]["revenue"] == 40.0
    assert result["by_product"]["Café"]["cogs"] == 20.0
    assert result["by_product"]["Café"]["gross_profit"] == 20.0
    for key in ["revenue", "cogs", "gross_profit"]:
        assert isinstance(result["by_product"]["Café"][key], float)

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 120.0
    assert isinstance(game["cash"], float)
    assert game["stock"]["Café"] == 0
    assert game["day"] == 2


def test_restart_keeps_progress_without_replaying_the_day(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    logic.trade_day(db_path, PLAYER)

    # Restart: open the same database file again.
    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 120.0
    assert game["stock"]["Café"] == 0
    assert game["day"] == 2

    results = logic.get_results(db_path, PLAYER)
    assert [r["day"] for r in results] == [1]
    assert results[0]["by_product"]["Café"]["units_sold"] == 10
    assert results[0]["by_product"]["Café"]["revenue"] == 40.0
    assert results[0]["by_product"]["Café"]["cogs"] == 20.0
    assert results[0]["by_product"]["Café"]["gross_profit"] == 20.0


def test_stock_limits_sales(tmp_path):
    # Each case gets its own database file.
    few_db = tmp_path / "few.db"
    logic.load_game(few_db, PLAYER)
    logic.buy(few_db, PLAYER, "Café", 3)
    result = logic.trade_day(few_db, PLAYER)
    assert result["by_product"]["Café"]["units_sold"] == 3
    game = logic.load_game(few_db, PLAYER)
    assert game["cash"] == 106.0
    assert game["stock"]["Café"] == 0

    many_db = tmp_path / "many.db"
    logic.load_game(many_db, PLAYER)
    logic.buy(many_db, PLAYER, "Café", 15)
    result = logic.trade_day(many_db, PLAYER)
    assert result["by_product"]["Café"]["units_sold"] == 10
    game = logic.load_game(many_db, PLAYER)
    assert game["cash"] == 110.0
    assert game["stock"]["Café"] == 5


def test_demand_boundaries():
    # Pure rule: touches no database at all.
    assert logic.demand(4.00, 4.00) == 10
    assert logic.demand(4.01, 4.00) == 5
    assert logic.demand(8.00, 4.00) == 5
    assert logic.demand(8.01, 4.00) == 0
