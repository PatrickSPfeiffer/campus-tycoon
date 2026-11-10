import pytest

import logic

PLAYER = "ana@example.com"


def play_check_2_run(db_path):
    # Check 2: buy 10 Café and 10 Water, price Water out of demand, trade five times.
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    logic.buy(db_path, PLAYER, "Water", 10)
    logic.set_price(db_path, PLAYER, "Water", 2.50)
    for _ in range(5):
        logic.trade_day(db_path, PLAYER)


def test_new_game_is_day_1_of_5_and_not_complete(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path, PLAYER)
    assert logic.RUN_DAYS == 5
    assert game["day"] == 1
    assert logic.is_run_complete(game) is False


def test_five_trades_complete_the_run_with_final_result(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, PLAYER)
    logic.buy(db_path, PLAYER, "Café", 10)
    game = logic.buy(db_path, PLAYER, "Water", 10)
    assert game["cash"] == 75.0
    logic.set_price(db_path, PLAYER, "Water", 2.50)

    for _ in range(4):
        logic.trade_day(db_path, PLAYER)
    assert logic.is_run_complete(logic.load_game(db_path, PLAYER)) is False

    logic.trade_day(db_path, PLAYER)
    game = logic.load_game(db_path, PLAYER)
    assert logic.is_run_complete(game) is True

    final = logic.final_result(game)
    assert final == {"final_cash": 115.0, "stock_at_cost": 5.0, "gain": 20.0}
    for key in ["final_cash", "stock_at_cost", "gain"]:
        assert isinstance(final[key], float)


def test_buying_and_trading_rejected_after_run_complete(tmp_path):
    db_path = tmp_path / "game.db"
    play_check_2_run(db_path)
    before = logic.load_game(db_path, PLAYER)
    history_before = logic.get_results(db_path, PLAYER)

    # €2.00 is affordable with €115, so only the completed run stops it.
    with pytest.raises(ValueError):
        logic.buy(db_path, PLAYER, "Café", 1)
    with pytest.raises(ValueError):
        logic.trade_day(db_path, PLAYER)

    after = logic.load_game(db_path, PLAYER)
    assert after["cash"] == before["cash"]
    assert after["stock"] == before["stock"]
    assert after["day"] == before["day"]
    assert logic.get_results(db_path, PLAYER) == history_before


def test_history_has_five_days_and_completed_run_survives_restart(tmp_path):
    db_path = tmp_path / "game.db"
    play_check_2_run(db_path)

    results = logic.get_results(db_path, PLAYER)
    assert [r["day"] for r in results] == [1, 2, 3, 4, 5]

    # Restart: open the same database file again.
    game = logic.load_game(db_path, PLAYER)
    assert logic.is_run_complete(game) is True
    assert logic.final_result(game) == {"final_cash": 115.0, "stock_at_cost": 5.0, "gain": 20.0}
    assert [r["day"] for r in logic.get_results(db_path, PLAYER)] == [1, 2, 3, 4, 5]


def test_new_run_restores_starting_state(tmp_path):
    db_path = tmp_path / "game.db"
    play_check_2_run(db_path)

    logic.new_run(db_path, PLAYER)

    # Restart: open the same database file again.
    game = logic.load_game(db_path, PLAYER)
    assert game["cash"] == 100.0
    assert isinstance(game["cash"], float)
    assert game["stock"] == {"Café": 0, "Croissant": 0, "Water": 0}
    assert game["price"] == {"Café": 4.0, "Croissant": 3.0, "Water": 1.2}
    assert game["day"] == 1
    assert logic.is_run_complete(game) is False
    assert logic.get_results(db_path, PLAYER) == []
