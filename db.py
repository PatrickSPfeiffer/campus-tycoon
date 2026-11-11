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
    # Practice: one game per player. Every row belongs to one player (their email).
    conn.execute(
        "CREATE TABLE IF NOT EXISTS players ("
        " email TEXT PRIMARY KEY,"
        " name TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS games ("
        " player TEXT PRIMARY KEY,"
        " cash REAL NOT NULL,"
        " day INTEGER NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products ("
        " player TEXT NOT NULL,"
        " product TEXT NOT NULL,"
        " stock INTEGER NOT NULL,"
        " price REAL NOT NULL,"
        " PRIMARY KEY (player, product))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS results ("
        " player TEXT NOT NULL,"
        " day INTEGER NOT NULL,"
        " product TEXT NOT NULL,"
        " units_sold INTEGER NOT NULL,"
        " revenue REAL NOT NULL,"
        " cogs REAL NOT NULL,"
        " gross_profit REAL NOT NULL,"
        " PRIMARY KEY (player, day, product))"
    )
    # Tournaments: created now, used from a later feature. See docs/data-model.md.
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tournaments ("
        " id INTEGER PRIMARY KEY NOT NULL,"
        " name TEXT NOT NULL,"
        " code TEXT NOT NULL UNIQUE,"
        " organiser TEXT NOT NULL,"
        " day INTEGER NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS stands ("
        " tournament_id INTEGER NOT NULL,"
        " player TEXT NOT NULL,"
        " seat INTEGER NOT NULL,"
        " cash REAL NOT NULL,"
        " ready INTEGER NOT NULL CHECK (ready IN (0, 1)),"
        " PRIMARY KEY (tournament_id, player),"
        " UNIQUE (tournament_id, seat))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS stand_products ("
        " tournament_id INTEGER NOT NULL,"
        " player TEXT NOT NULL,"
        " product TEXT NOT NULL,"
        " stock INTEGER NOT NULL,"
        " price REAL NOT NULL,"
        " PRIMARY KEY (tournament_id, player, product))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tournament_results ("
        " tournament_id INTEGER NOT NULL,"
        " day INTEGER NOT NULL,"
        " player TEXT NOT NULL,"
        " product TEXT NOT NULL,"
        " price REAL NOT NULL,"
        " units_sold INTEGER NOT NULL,"
        " revenue REAL NOT NULL,"
        " cogs REAL NOT NULL,"
        " gross_profit REAL NOT NULL,"
        " PRIMARY KEY (tournament_id, day, player, product))"
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


def get_tournament_by_code(db_path, code):
    with open_database(db_path) as conn:
        row = conn.execute(
            "SELECT id, name, code, organiser, day FROM tournaments WHERE code = ?",
            (code,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "code": row[2],
        "organiser": row[3],
        "day": row[4],
    }


def create_tournament(db_path, name, code, organiser, day):
    with open_database(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO tournaments (name, code, organiser, day) VALUES (?, ?, ?, ?)",
            (name, code, organiser, day),
        )
        tournament_id = cursor.lastrowid
    return {
        "id": tournament_id,
        "name": name,
        "code": code,
        "organiser": organiser,
        "day": day,
    }


def stand_exists(db_path, tournament_id, player):
    with open_database(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM stands WHERE tournament_id = ? AND player = ?",
            (tournament_id, player),
        ).fetchone()
    return row is not None


def join_tournament(db_path, tournament_id, player, cash, ready, products):
    with open_database(db_path) as conn:
        existing = conn.execute(
            "SELECT 1 FROM stands WHERE tournament_id = ? AND player = ?",
            (tournament_id, player),
        ).fetchone()
        if existing is not None:
            raise ValueError("You have already joined this tournament.")

        next_seat = conn.execute(
            "SELECT COALESCE(MAX(seat), 0) + 1 FROM stands WHERE tournament_id = ?",
            (tournament_id,),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO stands (tournament_id, player, seat, cash, ready)"
            " VALUES (?, ?, ?, ?, ?)",
            (tournament_id, player, next_seat, cash, ready),
        )
        for name, product in products.items():
            conn.execute(
                "INSERT INTO stand_products"
                " (tournament_id, player, product, stock, price)"
                " VALUES (?, ?, ?, ?, ?)",
                (tournament_id, player, name, product["stock"], product["price"]),
            )


# Rows are read by position, because libsql returns plain tuples
# where sqlite3 could return rows with names.
# Every practice function takes the player (their email) and only
# reads or changes that player's rows.

def get_game(db_path, player):
    with open_database(db_path) as conn:
        row = conn.execute("SELECT cash, day FROM games WHERE player = ?", (player,)).fetchone()
        products = conn.execute(
            "SELECT product, stock, price FROM products WHERE player = ?", (player,)
        ).fetchall()
    if row is None:
        return None
    return {
        "cash": float(row[0]),
        "day": row[1],
        "stock": {p[0]: p[1] for p in products},
        "price": {p[0]: float(p[2]) for p in products},
    }


def write_game(conn, player, game):
    conn.execute(
        "INSERT OR REPLACE INTO games (player, cash, day) VALUES (?, ?, ?)",
        (player, game["cash"], game["day"]),
    )
    for name in game["stock"]:
        conn.execute(
            "INSERT OR REPLACE INTO products (player, product, stock, price) VALUES (?, ?, ?, ?)",
            (player, name, game["stock"][name], game["price"][name]),
        )


def add_player(db_path, player, name, game):
    # The player and their first game are saved in one transaction.
    # A player who is already in players keeps their name.
    with open_database(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO players (email, name) VALUES (?, ?)", (player, name)
        )
        write_game(conn, player, game)


def save_game(db_path, player, game):
    with open_database(db_path) as conn:
        write_game(conn, player, game)


def save_day(db_path, player, game, result):
    # Game state and the day's results are written in one transaction,
    # so a day is never saved without its results (or the other way round).
    # The primary key (player, day, product) stops a day from being recorded twice.
    with open_database(db_path) as conn:
        write_game(conn, player, game)
        for name, line in result["by_product"].items():
            conn.execute(
                "INSERT INTO results"
                " (player, day, product, units_sold, revenue, cogs, gross_profit)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (player, result["day"], name, line["units_sold"], line["revenue"],
                 line["cogs"], line["gross_profit"]),
            )


def reset_game(db_path, player, game):
    # Clearing this player's history and writing their new game happen in one transaction.
    with open_database(db_path) as conn:
        conn.execute("DELETE FROM results WHERE player = ?", (player,))
        write_game(conn, player, game)


def get_result_rows(db_path, player):
    with open_database(db_path) as conn:
        rows = conn.execute(
            "SELECT day, product, units_sold, revenue, cogs, gross_profit"
            " FROM results WHERE player = ? ORDER BY day, rowid",
            (player,),
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
