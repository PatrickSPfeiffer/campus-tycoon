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
        " day INTEGER NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products ("
        " name TEXT PRIMARY KEY,"
        " stock INTEGER NOT NULL,"
        " price REAL NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS results ("
        " day INTEGER NOT NULL,"
        " product TEXT NOT NULL,"
        " units_sold INTEGER NOT NULL,"
        " revenue REAL NOT NULL,"
        " cogs REAL NOT NULL,"
        " gross_profit REAL NOT NULL,"
        " PRIMARY KEY (day, product))"
    )
    return conn


def get_game(db_path):
    with connect(db_path) as conn:
        row = conn.execute("SELECT cash, day FROM game WHERE id = 1").fetchone()
        products = conn.execute("SELECT name, stock, price FROM products").fetchall()
    conn.close()
    if row is None:
        return None
    return {
        "cash": float(row["cash"]),
        "day": row["day"],
        "stock": {p["name"]: p["stock"] for p in products},
        "price": {p["name"]: float(p["price"]) for p in products},
    }


def write_game(conn, game):
    conn.execute(
        "INSERT OR REPLACE INTO game (id, cash, day) VALUES (1, ?, ?)",
        (game["cash"], game["day"]),
    )
    for name in game["stock"]:
        conn.execute(
            "INSERT OR REPLACE INTO products (name, stock, price) VALUES (?, ?, ?)",
            (name, game["stock"][name], game["price"][name]),
        )


def save_game(db_path, game):
    with connect(db_path) as conn:
        write_game(conn, game)
    conn.close()


def save_day(db_path, game, result):
    # Game state and the day's results are written in one transaction,
    # so a day is never saved without its results (or the other way round).
    # The primary key (day, product) stops a day from being recorded twice.
    with connect(db_path) as conn:
        write_game(conn, game)
        for name, line in result["by_product"].items():
            conn.execute(
                "INSERT INTO results (day, product, units_sold, revenue, cogs, gross_profit)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (result["day"], name, line["units_sold"], line["revenue"],
                 line["cogs"], line["gross_profit"]),
            )
    conn.close()


def reset_game(db_path, game):
    # Clearing the history and writing the new game happen in one transaction.
    with connect(db_path) as conn:
        conn.execute("DELETE FROM results")
        write_game(conn, game)
    conn.close()


def get_result_rows(db_path):
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT day, product, units_sold, revenue, cogs, gross_profit"
            " FROM results ORDER BY day, rowid"
        ).fetchall()
    conn.close()
    return [
        {
            "day": row["day"],
            "product": row["product"],
            "units_sold": row["units_sold"],
            "revenue": float(row["revenue"]),
            "cogs": float(row["cogs"]),
            "gross_profit": float(row["gross_profit"]),
        }
        for row in rows
    ]
