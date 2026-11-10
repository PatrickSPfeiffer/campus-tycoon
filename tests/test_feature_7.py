import sqlite3

import pytest

import db
import logic

ANA = "ana@example.com"
BRUNO = "bruno@example.com"

PRACTICE_TABLES = ["players", "games", "products", "results"]
TOURNAMENT_TABLES = ["tournaments", "stands", "stand_products", "tournament_results"]


def read_rows(db_path, sql):
    # Reads straight from the test's own local database file.
    with db.open_database(db_path) as conn:
        return conn.execute(sql).fetchall()


def test_check_1_new_player_gets_a_new_game_and_is_added_to_players(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path, ANA)
    assert game["cash"] == 100.0
    assert isinstance(game["cash"], float)
    assert game["day"] == 1
    assert game["stock"] == {"Café": 0, "Croissant": 0, "Water": 0}
    assert game["price"] == {"Café": 4.0, "Croissant": 3.0, "Water": 1.2}

    # The name is the part of the email before "@".
    assert read_rows(db_path, "SELECT email, name FROM players") == [(ANA, "ana")]

    # Without "@", the whole text is the name.
    logic.load_game(db_path, "guest")
    assert read_rows(db_path, "SELECT name FROM players WHERE email = 'guest'") == [("guest",)]


def test_check_2_buying_and_pricing_change_only_that_players_game(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.load_game(db_path, BRUNO)

    game = logic.buy(db_path, ANA, "Café", 10)
    assert game["cash"] == 80.0
    assert game["stock"]["Café"] == 10

    bruno = logic.load_game(db_path, BRUNO)
    assert bruno["cash"] == 100.0
    assert bruno["stock"] == {"Café": 0, "Croissant": 0, "Water": 0}

    bruno = logic.set_price(db_path, BRUNO, "Croissant", 3.50)
    assert bruno["price"]["Croissant"] == 3.5

    ana = logic.load_game(db_path, ANA)
    assert ana["price"]["Croissant"] == 3.0
    assert ana["cash"] == 80.0
    assert ana["stock"]["Café"] == 10


def test_check_3_trading_and_new_run_change_only_that_players_game(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.load_game(db_path, BRUNO)
    logic.buy(db_path, ANA, "Café", 10)
    logic.trade_day(db_path, ANA)

    bruno = logic.load_game(db_path, BRUNO)
    assert bruno["day"] == 1
    assert bruno["cash"] == 100.0
    assert logic.get_results(db_path, BRUNO) == []

    ana_before = logic.load_game(db_path, ANA)
    ana_results_before = logic.get_results(db_path, ANA)
    assert ana_before["cash"] == 120.0
    assert ana_before["day"] == 2
    assert [r["day"] for r in ana_results_before] == [1]

    logic.new_run(db_path, BRUNO)

    assert logic.load_game(db_path, ANA) == ana_before
    assert logic.get_results(db_path, ANA) == ana_results_before
    bruno = logic.load_game(db_path, BRUNO)
    assert bruno["cash"] == 100.0
    assert bruno["day"] == 1


def test_check_4_restart_gives_each_player_their_own_saved_game(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.load_game(db_path, BRUNO)
    logic.buy(db_path, ANA, "Café", 10)
    logic.trade_day(db_path, ANA)
    logic.buy(db_path, BRUNO, "Water", 10)
    logic.set_price(db_path, BRUNO, "Croissant", 3.50)

    # Restart: open the same database file again.
    ana = logic.load_game(db_path, ANA)
    assert ana["cash"] == 120.0
    assert ana["day"] == 2
    assert ana["stock"] == {"Café": 0, "Croissant": 0, "Water": 0}
    assert ana["price"] == {"Café": 4.0, "Croissant": 3.0, "Water": 1.2}
    assert [r["day"] for r in logic.get_results(db_path, ANA)] == [1]

    bruno = logic.load_game(db_path, BRUNO)
    assert bruno["cash"] == 95.0
    assert bruno["day"] == 1
    assert bruno["stock"] == {"Café": 0, "Croissant": 0, "Water": 10}
    assert bruno["price"] == {"Café": 4.0, "Croissant": 3.5, "Water": 1.2}
    assert logic.get_results(db_path, BRUNO) == []

    assert sorted(read_rows(db_path, "SELECT email, name FROM players")) == [
        (ANA, "ana"), (BRUNO, "bruno"),
    ]


def test_check_5_empty_or_too_long_player_is_rejected_and_nothing_saved(tmp_path):
    db_path = tmp_path / "game.db"
    for player in ["", "   ", None, "a" * 255]:
        with pytest.raises(ValueError):
            logic.load_game(db_path, player)
        with pytest.raises(ValueError):
            logic.buy(db_path, player, "Café", 1)
        with pytest.raises(ValueError):
            logic.set_price(db_path, player, "Café", 5.00)
        with pytest.raises(ValueError):
            logic.trade_day(db_path, player)
        with pytest.raises(ValueError):
            logic.new_run(db_path, player)
        with pytest.raises(ValueError):
            logic.get_results(db_path, player)

    for table in PRACTICE_TABLES:
        assert read_rows(db_path, f"SELECT COUNT(*) FROM {table}") == [(0,)]

    # Exactly 254 characters is still allowed.
    longest = "a" * 242 + "@example.com"
    assert len(longest) == 254
    assert logic.load_game(db_path, longest)["cash"] == 100.0
    assert read_rows(db_path, "SELECT email FROM players") == [(longest,)]


def test_check_6_tournament_tables_exist_empty_and_enforce_unique_code_and_seat(tmp_path):
    db_path = tmp_path / "game.db"
    with db.open_database(db_path) as conn:
        names = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        for table in TOURNAMENT_TABLES:
            assert (table,) in names
            assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchall() == [(0,)]

        add_tournament = (
            "INSERT INTO tournaments (id, name, code, organiser, day) VALUES (?, ?, ?, ?, ?)"
        )
        conn.execute(add_tournament, (1, "Cup A", "ABC123", ANA, 1))
        conn.execute(add_tournament, (2, "Cup B", "XYZ789", BRUNO, 1))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(add_tournament, (3, "Cup C", "ABC123", BRUNO, 1))
        # Every tournament column is NOT NULL.
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(add_tournament, (4, None, "NUL000", BRUNO, 1))

        add_stand = (
            "INSERT INTO stands (tournament_id, player, seat, cash, ready) VALUES (?, ?, ?, ?, ?)"
        )
        conn.execute(add_stand, (1, ANA, 1, 100.0, 0))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(add_stand, (1, BRUNO, 1, 100.0, 0))
        # The same seat in another tournament, or the next seat, is fine.
        conn.execute(add_stand, (2, BRUNO, 1, 100.0, 0))
        conn.execute(add_stand, (1, BRUNO, 2, 100.0, 0))

        assert conn.execute("SELECT COUNT(*) FROM tournaments").fetchall() == [(2,)]
        assert conn.execute(
            "SELECT tournament_id, player, seat FROM stands ORDER BY tournament_id, seat"
        ).fetchall() == [(1, ANA, 1), (1, BRUNO, 2), (2, BRUNO, 1)]
