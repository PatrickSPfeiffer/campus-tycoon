import pytest

import logic


def test_new_game_price_then_set_and_restart(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path)
    assert game["price"] == 4.0
    assert isinstance(game["price"], float)

    logic.buy(db_path, 10)
    game = logic.set_price(db_path, 6.00)
    assert game["price"] == 6.0

    # Restart: open the same database file again.
    game = logic.load_game(db_path)
    assert game["price"] == 6.0
    assert isinstance(game["price"], float)
    assert game["cash"] == 80.0
    assert game["stock"] == 10


def test_reject_invalid_prices(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path)
    logic.set_price(db_path, 6.00)

    for price in [0, -1, 4.001]:
        with pytest.raises(ValueError):
            logic.set_price(db_path, price)

    game = logic.load_game(db_path)
    assert game["price"] == 6.0


def test_trade_at_price_6(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path)
    logic.buy(db_path, 10)
    logic.set_price(db_path, 6.00)

    result = logic.trade_day(db_path)
    assert result["units_sold"] == 5
    assert result["revenue"] == 30.0
    assert result["cogs"] == 10.0
    assert result["gross_profit"] == 20.0

    game = logic.load_game(db_path)
    assert game["cash"] == 110.0
    assert game["stock"] == 5


def test_trade_at_price_9_sells_nothing(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path)
    logic.buy(db_path, 10)
    logic.set_price(db_path, 9.00)

    result = logic.trade_day(db_path)
    assert result["units_sold"] == 0

    game = logic.load_game(db_path)
    assert game["cash"] == 80.0
    assert game["stock"] == 10
    assert game["day"] == 2


def test_trade_at_price_4_01_rounds_money(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path)
    logic.buy(db_path, 10)
    logic.set_price(db_path, 4.01)

    result = logic.trade_day(db_path)
    assert result["units_sold"] == 5
    assert result["revenue"] == 20.05
    assert result["gross_profit"] == 10.05

    game = logic.load_game(db_path)
    assert game["cash"] == 100.05
