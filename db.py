import os
import sqlite3

DEFAULT_PATH = "data/game.db"


def connect(db_path):
    folder = os.path.dirname(db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS game ("
        " id INTEGER PRIMARY KEY CHECK (id = 1),"
        " cash REAL NOT NULL,"
        " stock INTEGER NOT NULL,"
        " day INTEGER NOT NULL,"
        " price REAL NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS results ("
        " day INTEGER PRIMARY KEY,"
        " units_sold INTEGER NOT NULL,"
        " revenue REAL NOT NULL,"
        " cogs REAL NOT NULL,"
        " gross_profit REAL NOT NULL)"
    )
    return conn


def get_game(db_path):
    with connect(db_path) as conn:
        row = conn.execute("SELECT cash, stock, day, price FROM game WHERE id = 1").fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "cash": float(row["cash"]),
        "stock": row["stock"],
        "day": row["day"],
        "price": float(row["price"]),
    }


def save_game(db_path, game):
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO game (id, cash, stock, day, price) VALUES (1, ?, ?, ?, ?)",
            (game["cash"], game["stock"], game["day"], game["price"]),
        )
    conn.close()


def save_day(db_path, game, result):
    # Game state and the day's result are written in one transaction,
    # so a day is never saved without its result (or the other way round).
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO game (id, cash, stock, day, price) VALUES (1, ?, ?, ?, ?)",
            (game["cash"], game["stock"], game["day"], game["price"]),
        )
        conn.execute(
            "INSERT INTO results (day, units_sold, revenue, cogs, gross_profit)"
            " VALUES (?, ?, ?, ?, ?)",
            (result["day"], result["units_sold"], result["revenue"],
             result["cogs"], result["gross_profit"]),
        )
    conn.close()


def get_results(db_path):
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT day, units_sold, revenue, cogs, gross_profit FROM results ORDER BY day"
        ).fetchall()
    conn.close()
    return [
        {
            "day": row["day"],
            "units_sold": row["units_sold"],
            "revenue": float(row["revenue"]),
            "cogs": float(row["cogs"]),
            "gross_profit": float(row["gross_profit"]),
        }
        for row in rows
    ]
