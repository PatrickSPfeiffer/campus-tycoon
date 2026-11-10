import pytest

import logic

PLAYER = "ana@example.com"


def start_check_4_game(db_path):
    # The state of check 4: €65, 10 Café at €4.00, 10 Croissant at €3.50, no Water.
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    logic.buy(db_path, PLAYER, "Croissant", 10)
    logic.set_price(db_path, PLAYER, "Croissant", 3.50)


def test_new_game_has_three_products(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 100.0
    assert isinstance(game["cash"], float)
    assert game["day"] == 1
    assert game["stock"] == {"Café": 0, "Croissant": 0, "Water": 0}
    assert game["price"] == {"Café": 4.0, "Croissant": 3.0, "Water": 1.2}
    for price in game["price"].values():
        assert isinstance(price, float)


def test_buy_two_products_then_reject_unknown_product(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    game = logic.buy(db_path, PLAYER, "Croissant", 10)
    assert game["cash"] == 65.0
    assert game["stock"] == {"Café": 10, "Croissant": 10, "Water": 0}

    with pytest.raises(ValueError):
        logic.buy(db_path, PLAYER, "Tea", 1)

    with pytest.raises(ValueError):
        logic.set_price(db_path, PLAYER, "Tea", 2.00)

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 65.0
    assert game["stock"] == {"Café": 10, "Croissant": 10, "Water": 0}
    assert game["price"] == {"Café": 4.0, "Croissant": 3.0, "Water": 1.2}


def test_set_price_changes_only_that_product_and_survives_restart(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    game = logic.set_price(db_path, PLAYER, "Croissant", 3.50)
    assert game["price"] == {"Café": 4.0, "Croissant": 3.5, "Water": 1.2}

    # Restart: open the same database file again.
    game = logic.load_game(db_path, PLAYER)
    assert game["price"] == {"Café": 4.0, "Croissant": 3.5, "Water": 1.2}


def test_trade_one_day_by_product_and_in_total(tmp_path):
    db_path = tmp_path / "game.db"
    start_check_4_game(db_path)
    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 65.0

    result = logic.trade_day(db_path, PLAYER)
    assert result["day"] == 1
    assert result["by_product"]["Café"] == {
        "units_sold": 10, "revenue": 40.0, "cogs": 20.0, "gross_profit": 20.0,
    }
    assert result["by_product"]["Croissant"] == {
        "units_sold": 5, "revenue": 17.5, "cogs": 7.5, "gross_profit": 10.0,
    }
    assert result["by_product"]["Water"] == {
        "units_sold": 0, "revenue": 0.0, "cogs": 0.0, "gross_profit": 0.0,
    }
    assert result["total"] == {
        "units_sold": 15, "revenue": 57.5, "cogs": 27.5, "gross_profit": 30.0,
    }
    for key in ["revenue", "cogs", "gross_profit"]:
        assert isinstance(result["total"][key], float)

    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 122.5
    assert game["stock"] == {"Café": 0, "Croissant": 5, "Water": 0}
    assert game["day"] == 2


def test_restart_after_trading_keeps_everything_and_one_result_per_product(tmp_path):
    db_path = tmp_path / "game.db"
    start_check_4_game(db_path)
    traded = logic.trade_day(db_path, PLAYER)

    # Restart: open the same database file again.
    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 122.5
    assert game["stock"] == {"Café": 0, "Croissant": 5, "Water": 0}
    assert game["price"] == {"Café": 4.0, "Croissant": 3.5, "Water": 1.2}
    assert game["day"] == 2

    results = logic.get_results(db_path, PLAYER)
    assert [r["day"] for r in results] == [1]
    assert sorted(results[0]["by_product"]) == ["Café", "Croissant", "Water"]
    assert results[0] == traded
