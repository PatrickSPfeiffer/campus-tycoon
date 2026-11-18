import sqlite3

import db


def test_old_games_schema_is_migrated_and_existing_data_is_preserved(tmp_path):
    db_path = tmp_path / "game.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE games ("
        " player TEXT PRIMARY KEY,"
        " cash REAL NOT NULL,"
        " day INTEGER NOT NULL,"
        " start_cash REAL NOT NULL DEFAULT 100.0)"
    )
    conn.execute(
        "INSERT INTO games (player, cash, day, start_cash) VALUES (?, ?, ?, ?)",
        ("ana@example.com", 125.0, 2, 100.0),
    )
    conn.commit()

    db.create_tables(conn)
    db.create_tables(conn)
    conn.close()

    assert db.get_game(db_path, "ana@example.com") == {
        "cash": 125.0,
        "day": 2,
        "start_cash": 100.0,
        "debt": 0.0,
        "stock": {},
        "price": {},
    }
