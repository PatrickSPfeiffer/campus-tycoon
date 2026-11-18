"""Checks for specs/feature-reuse-turso-connection.md — one test per 'Done when' line.

Turso is faked with a local SQLite file behind a fake libsql, so no test reaches the network.
"""

import sqlite3
import threading

import pytest

import db
import logic

ANA = "ana@example.com"
FAKE_SETTINGS = {"TURSO_DATABASE_URL": "libsql://fake-db.turso.io", "TURSO_AUTH_TOKEN": "fake-token"}


class FakeTursoConnection:
    # Behaves like a libsql connection, but stores the data in a local SQLite file.
    def __init__(self, path):
        self.inner = sqlite3.connect(path, check_same_thread=False)
        self.closed = False
        self.fail_next = False

    def execute(self, sql, *args):
        if self.fail_next:
            self.fail_next = False
            raise ValueError("Hrana: `http error: connection reset`")
        return self.inner.execute(sql, *args)

    def __enter__(self):
        self.inner.__enter__()
        return self

    def __exit__(self, *exc):
        return self.inner.__exit__(*exc)

    def close(self):
        self.closed = True
        self.inner.close()


class FakeLibsql:
    def __init__(self, path):
        self.path = path
        self.connections = []

    def connect(self, url, auth_token):
        conn = FakeTursoConnection(self.path)
        self.connections.append(conn)
        return conn


@pytest.fixture
def turso(tmp_path, monkeypatch):
    # Every test starts with no remembered tables or connections.
    monkeypatch.setattr(db, "_TABLES_READY", set())
    db.forget_connections()
    monkeypatch.setattr(db, "read_settings", lambda: FAKE_SETTINGS)
    fake = FakeLibsql(tmp_path / "turso.db")
    monkeypatch.setattr(db, "libsql", fake)
    yield fake
    db.forget_connections()


# 1. One connection per click
def test_one_turso_connection_for_a_whole_click(turso):
    path = db.DEFAULT_PATH
    logic.load_game(path, ANA)
    logic.buy(path, ANA, "Café", 10)
    logic.set_price(path, ANA, "Café", 4.0)
    logic.trade_day(path, ANA)
    logic.get_results(path, ANA)
    assert len(turso.connections) == 1
    assert logic.load_game(path, ANA)["cash"] == 120.0


# 2. Idle connection is replaced
def test_idle_connection_is_replaced(turso, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(db, "now", lambda: clock[0])
    logic.load_game(db.DEFAULT_PATH, ANA)
    clock[0] += db.REUSE_SECONDS + 1
    logic.load_game(db.DEFAULT_PATH, ANA)
    assert len(turso.connections) == 2
    assert turso.connections[0].closed is True


# 3. Network error
def test_network_error_forgets_the_connection(turso):
    logic.load_game(db.DEFAULT_PATH, ANA)
    turso.connections[0].fail_next = True
    with pytest.raises(db.DatabaseUnavailable):
        logic.load_game(db.DEFAULT_PATH, ANA)
    assert turso.connections[0].closed is True

    game = logic.load_game(db.DEFAULT_PATH, ANA)
    assert len(turso.connections) == 2
    assert game["cash"] == 100.0


# 4. Each thread separately
def test_each_thread_gets_its_own_connection(turso):
    logic.load_game(db.DEFAULT_PATH, ANA)
    errors = []

    def other_player():
        try:
            logic.load_game(db.DEFAULT_PATH, "bruno@example.com")
        except Exception as error:  # reported below, so the test fails clearly
            errors.append(error)
        finally:
            db.forget_connections()

    thread = threading.Thread(target=other_player)
    thread.start()
    thread.join()
    assert errors == []
    assert len(turso.connections) == 2


# 5. Local unchanged
def test_local_sqlite_still_opens_a_connection_per_call(tmp_path, monkeypatch):
    opened = []
    real_connect = sqlite3.connect

    def counting_connect(*args, **kwargs):
        opened.append(1)
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(db.sqlite3, "connect", counting_connect)
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.buy(db_path, ANA, "Café", 1)
    assert len(opened) >= 3
