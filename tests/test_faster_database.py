"""Checks for specs/feature-faster-database.md — one test per 'Done when' line."""

import os

import pytest

import db
import logic

ANA = "ana@example.com"


@pytest.fixture
def count_create_tables(monkeypatch):
    # Wraps the real create_tables and counts how often it runs.
    calls = []
    real = db.create_tables

    def counting(conn):
        calls.append(1)
        real(conn)

    monkeypatch.setattr(db, "create_tables", counting)
    return calls


# 1. Once per database
def test_tables_are_created_once_per_database(tmp_path, count_create_tables):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.buy(db_path, ANA, "Café", 10)
    logic.set_price(db_path, ANA, "Café", 4.0)
    logic.trade_day(db_path, ANA)
    logic.get_results(db_path, ANA)
    assert len(count_create_tables) == 1
    assert logic.load_game(db_path, ANA)["cash"] == 120.0


# 2. Each database separately
def test_each_database_gets_its_own_tables(tmp_path, count_create_tables):
    logic.load_game(tmp_path / "first.db", ANA)
    logic.load_game(tmp_path / "second.db", ANA)
    logic.load_game(tmp_path / "first.db", ANA)
    assert len(count_create_tables) == 2


# 3. Emptied file
def test_deleted_local_file_gets_tables_again(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.buy(db_path, ANA, "Café", 10)
    os.remove(db_path)

    game = logic.load_game(db_path, ANA)
    assert game["cash"] == 100.0
    assert game["stock"]["Café"] == 0


# 4. Failure is not remembered
def test_failed_first_block_creates_tables_again(tmp_path, count_create_tables):
    db_path = tmp_path / "game.db"
    with pytest.raises(RuntimeError):
        with db.open_database(db_path):
            raise RuntimeError("something went wrong")
    logic.load_game(db_path, ANA)
    assert len(count_create_tables) == 2
