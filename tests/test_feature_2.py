import pytest

import logic

PLAYER = "ana@example.com"


def test_new_game_price_then_set_and_restart(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path, PLAYER)
    assert game["price"]["Café"] == 4.0
    assert isinstance(game["price"]["Café"], float)

    logic.buy(db_path, PLAYER, "Café", 10)
    game = logic.set_price(db_path, PLAYER, "Café", 6.00)
    assert game["price"]["Café"] == 6.0

    # Restart: open the same database file again.
    game = logic.load_game(db_path, PLAYER)
    assert game["price"]["Café"] == 6.0
    assert isinstance(game["price"]["Café"], float)
    assert game["cash"] == 80.0
    assert game["stock"]["Café"] == 10


def test_reject_invalid_prices(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.set_price(db_path, PLAYER, "Café", 6.00)

    for price in [0, -1, 4.001]:
        with pytest.raises(ValueError):
            logic.set_price(db_path, PLAYER, "Café", price)

    game = logic.load_game(db_path, PLAYER)
    assert game["price"]["Café"] == 6.0


def test_trade_at_price_6(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    logic.set_price(db_path, PLAYER, "Café", 6.00)

    result = logic.trade_day(db_path, PLAYER)
    assert result["by_product"]["Café"]["units_sold"] == 5
    assert result["by_product"]["Café"]["revenue"] == 30.0
    assert result["by_product"]["Café"]["cogs"] == 10.0
    assert result["by_product"]["Café"]["gross_profit"] == 20.0

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 110.0
    assert game["stock"]["Café"] == 5


def test_trade_at_price_9_sells_nothing(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    logic.set_price(db_path, PLAYER, "Café", 9.00)

    result = logic.trade_day(db_path, PLAYER)
    assert result["by_product"]["Café"]["units_sold"] == 0

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 80.0
    assert game["stock"]["Café"] == 10
    assert game["day"] == 2


def test_trade_at_price_4_01_rounds_money(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    logic.set_price(db_path, PLAYER, "Café", 4.01)

    result = logic.trade_day(db_path, PLAYER)
    assert result["by_product"]["Café"]["units_sold"] == 5
    assert result["by_product"]["Café"]["revenue"] == 20.05
    assert result["by_product"]["Café"]["gross_profit"] == 10.05

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 100.05
