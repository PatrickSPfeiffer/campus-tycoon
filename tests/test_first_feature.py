import pytest

import logic


def test_buy_within_budget_then_reject_unaffordable(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path)
    assert game["cash"] == 100.0
    assert isinstance(game["cash"], float)
    assert game["stock"] == 0
    assert game["day"] == 1

    game = logic.buy(db_path, 10)
    assert game["cash"] == 80.0
    assert isinstance(game["cash"], float)
    assert game["stock"] == 10

    with pytest.raises(ValueError):
        logic.buy(db_path, 41)

    game = logic.load_game(db_path)
    assert game["cash"] == 80.0
    assert game["stock"] == 10


def test_reject_invalid_quantities(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path)

    for quantity in [0, -5, 2.5]:
        with pytest.raises(ValueError):
            logic.buy(db_path, quantity)

    game = logic.load_game(db_path)
    assert game["cash"] == 100.0
    assert game["stock"] == 0


def test_trade_one_day(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path)
    logic.buy(db_path, 10)

    result = logic.trade_day(db_path)
    assert result["day"] == 1
    assert result["units_sold"] == 10
    assert result["revenue"] == 40.0
    assert result["cogs"] == 20.0
    assert result["gross_profit"] == 20.0
    for key in ["revenue", "cogs", "gross_profit"]:
        assert isinstance(result[key], float)

    game = logic.load_game(db_path)
    assert game["cash"] == 120.0
    assert isinstance(game["cash"], float)
    assert game["stock"] == 0
    assert game["day"] == 2


def test_restart_keeps_progress_without_replaying_the_day(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path)
    logic.buy(db_path, 10)
    logic.trade_day(db_path)

    # Restart: open the same database file again.
    game = logic.load_game(db_path)
    assert game["cash"] == 120.0
    assert game["stock"] == 0
    assert game["day"] == 2

    results = logic.get_results(db_path)
    assert [r["day"] for r in results] == [1]
    assert results[0]["units_sold"] == 10
    assert results[0]["revenue"] == 40.0
    assert results[0]["cogs"] == 20.0
    assert results[0]["gross_profit"] == 20.0


def test_stock_limits_sales(tmp_path):
    # Each case gets its own database file.
    few_db = tmp_path / "few.db"
    logic.load_game(few_db)
    logic.buy(few_db, 3)
    result = logic.trade_day(few_db)
    assert result["units_sold"] == 3
    game = logic.load_game(few_db)
    assert game["cash"] == 106.0
    assert game["stock"] == 0

    many_db = tmp_path / "many.db"
    logic.load_game(many_db)
    logic.buy(many_db, 15)
    result = logic.trade_day(many_db)
    assert result["units_sold"] == 10
    game = logic.load_game(many_db)
    assert game["cash"] == 110.0
    assert game["stock"] == 5


def test_demand_boundaries():
    # Pure rule: touches no database at all.
    assert logic.demand(4.00, 4.00) == 10
    assert logic.demand(4.01, 4.00) == 5
    assert logic.demand(8.00, 4.00) == 5
    assert logic.demand(8.01, 4.00) == 0
