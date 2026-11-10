import os
import sqlite3
from contextlib import contextmanager

import libsql
import streamlit as st

DEFAULT_PATH = "data/game.db"
SETTING_NAMES = ["TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN"]
UNAVAILABLE_MESSAGE = (
    "Database unavailable: the game data cannot be reached right now. "
    "Please try again in a moment."
)


class DatabaseUnavailable(Exception):
    pass


def read_settings():
    # Environment variables first, then st.secrets. A missing value becomes "".
    settings = {}
    for name in SETTING_NAMES:
        value = os.environ.get(name, "")
        if not value:
            try:
                value = st.secrets.get(name, "")
            except FileNotFoundError:
                # No secrets file: teammates without the secrets use local SQLite.
                value = ""
        settings[name] = value
    return settings


def choose_database(db_path, settings):
    # Only the game's own file can move to Turso; a test's own file always stays local.
    if db_path != DEFAULT_PATH:
        return {"kind": "local", "path": db_path}
    url = settings.get("TURSO_DATABASE_URL", "")
    token = settings.get("TURSO_AUTH_TOKEN", "")
    if not url and not token:
        return {"kind": "local", "path": db_path}
    if not url or not token:
        raise DatabaseUnavailable(UNAVAILABLE_MESSAGE)
    return {"kind": "turso", "url": url, "token": token}


def connect_turso(url, token):
    # Everything here counts as connecting, including the quick check,
    # so any exception becomes "database unavailable". The message never
    # contains the URL or the token.
    try:
        conn = libsql.connect(url, auth_token=token)
        conn.execute("SELECT 1")
    except Exception:
        raise DatabaseUnavailable(UNAVAILABLE_MESSAGE) from None
    return conn


def is_network_error(error):
    # libsql raises ValueError for every problem; its network errors
    # start with "Hrana: `http error".
    return isinstance(error, ValueError) and str(error).startswith("Hrana: `http error")


def connect(db_path):
    # A test's own database file never reads the real secrets.
    settings = read_settings() if db_path == DEFAULT_PATH else {}
    choice = choose_database(db_path, settings)
    if choice["kind"] == "turso":
        conn = connect_turso(choice["url"], choice["token"])
    else:
        folder = os.path.dirname(choice["path"])
        if folder:
            os.makedirs(folder, exist_ok=True)
        conn = sqlite3.connect(choice["path"])
    return conn


def create_tables(conn):
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


@contextmanager
def open_database(db_path):
    # One transaction: it is saved only if everything in the block succeeds.
    # If libsql loses the network, nothing is saved and the error becomes
    # "database unavailable". Other errors are not caught.
    conn = connect(db_path)
    try:
        with conn:
            create_tables(conn)
            yield conn
    except ValueError as error:
        if is_network_error(error):
            raise DatabaseUnavailable(UNAVAILABLE_MESSAGE) from None
        raise
    finally:
        conn.close()


# Rows are read by position, because libsql returns plain tuples
# where sqlite3 could return rows with names.

def get_game(db_path):
    with open_database(db_path) as conn:
        row = conn.execute("SELECT cash, day FROM game WHERE id = 1").fetchone()
        products = conn.execute("SELECT name, stock, price FROM products").fetchall()
    if row is None:
        return None
    return {
        "cash": float(row[0]),
        "day": row[1],
        "stock": {p[0]: p[1] for p in products},
        "price": {p[0]: float(p[2]) for p in products},
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
    with open_database(db_path) as conn:
        write_game(conn, game)


def save_day(db_path, game, result):
    # Game state and the day's results are written in one transaction,
    # so a day is never saved without its results (or the other way round).
    # The primary key (day, product) stops a day from being recorded twice.
    with open_database(db_path) as conn:
        write_game(conn, game)
        for name, line in result["by_product"].items():
            conn.execute(
                "INSERT INTO results (day, product, units_sold, revenue, cogs, gross_profit)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (result["day"], name, line["units_sold"], line["revenue"],
                 line["cogs"], line["gross_profit"]),
            )


def reset_game(db_path, game):
    # Clearing the history and writing the new game happen in one transaction.
    with open_database(db_path) as conn:
        conn.execute("DELETE FROM results")
        write_game(conn, game)


def get_result_rows(db_path):
    with open_database(db_path) as conn:
        rows = conn.execute(
            "SELECT day, product, units_sold, revenue, cogs, gross_profit"
            " FROM results ORDER BY day, rowid"
        ).fetchall()
    return [
        {
            "day": row[0],
            "product": row[1],
            "units_sold": row[2],
            "revenue": float(row[3]),
            "cogs": float(row[4]),
            "gross_profit": float(row[5]),
        }
        for row in rows
    ]
