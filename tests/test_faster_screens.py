"""Checks for specs/feature-faster-screens.md — one test per 'Done when' line from 1 to 7."""

import ast
import pathlib
import re
import sqlite3

import pytest

import db
import logic

ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"
OUTSIDER = "outsider@example.com"
NO_WEATHER = {"daily": {"precipitation_sum": [0.0], "temperature_2m_max": [18.0]}}


def fetch():
    return NO_WEATHER


def read_rows(db_path, sql, parameters=()):
    with db.open_database(db_path) as conn:
        return conn.execute(sql, parameters).fetchall()


def snapshot(db_path):
    return {
        table: read_rows(db_path, f"SELECT * FROM {table} ORDER BY rowid")
        for table in ("games", "products", "tournaments", "stands", "stand_products", "stand_upgrades")
    }


def assert_refusal(db_path, action, message):
    before = snapshot(db_path)
    with pytest.raises(ValueError, match=re.escape(message)):
        action()
    assert snapshot(db_path) == before


def setup_tournament(db_path, players=(ANA, BRUNO)):
    tournament = logic.create_tournament(db_path, ORGANISER, "Autumn Cup")
    for player in players:
        logic.join_tournament(db_path, player, tournament["code"])
    return tournament


def set_day(db_path, tournament_id, day):
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = ? WHERE id = ?", (day, tournament_id))


def stand(db_path, tournament_id, player):
    return db.get_tournament_stands(db_path, tournament_id)[player]


# 1. Buy many (practice)
def test_buy_many_buys_several_products_at_once(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.buy_many(db_path, ANA, {"Café": 10, "Croissant": 0, "Water": 5})
    assert game["cash"] == 77.5
    saved = logic.load_game(db_path, ANA)
    assert saved["cash"] == 77.5
    assert saved["stock"] == {"Café": 10, "Croissant": 0, "Water": 5}


# 2. Buy many refused
@pytest.mark.parametrize(
    ("quantities", "message"),
    [
        ({"Café": 0, "Croissant": 0, "Water": 0}, "Choose a quantity of at least 1 for one product."),
        ({"Café": 2, "Water": -1}, "Quantity must be a whole number, 0 or more."),
        ({"Café": 1.5}, "Quantity must be a whole number, 0 or more."),
        ({"Café": True}, "Quantity must be a whole number, 0 or more."),
        ({"Tea": 1}, "Unknown product: Tea."),
        ({"Café": 40, "Water": 41}, "Not enough cash: buying costs €100.50, you have €100.00."),
    ],
)
def test_buy_many_refusals_change_nothing(tmp_path, quantities, message):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    assert_refusal(db_path, lambda: logic.buy_many(db_path, ANA, quantities), message)


def test_buy_many_refused_after_the_run(tmp_path):
    db_path = tmp_path / "game.db"
    for _ in range(logic.RUN_DAYS):
        logic.trade_day(db_path, ANA)
    assert_refusal(db_path, lambda: logic.buy_many(db_path, ANA, {"Café": 1}), "The run is complete.")


# 3. Set prices (practice)
def test_set_prices_saves_several_prices(tmp_path):
    db_path = tmp_path / "game.db"
    logic.set_prices(db_path, ANA, {"Café": 3.5, "Water": 1.0})
    prices = logic.load_game(db_path, ANA)["price"]
    assert prices == {"Café": 3.5, "Croissant": 3.0, "Water": 1.0}


@pytest.mark.parametrize(
    ("price", "message"),
    [
        (0, "Price must be more than €0."),
        (1.234, "Price can have at most 2 decimals."),
        (1000.01, "Price can be at most €1000.00."),
    ],
)
def test_set_prices_one_invalid_price_refuses_all(tmp_path, price, message):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    assert_refusal(
        db_path, lambda: logic.set_prices(db_path, ANA, {"Café": 3.5, "Water": price}), message
    )


def test_set_prices_refuses_unknown_product(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    assert_refusal(
        db_path, lambda: logic.set_prices(db_path, ANA, {"Café": 3.5, "Tea": 1.0}), "Unknown product: Tea."
    )


# 4. Tournament buy and prices
def test_tournament_buy_many_and_set_prices(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    result = logic.buy_tournament_stock_many(db_path, ANA, tournament["id"], {"Café": 10, "Water": 5})
    assert result["cash"] == 77.5
    logic.set_tournament_prices(db_path, ANA, tournament["id"], {"Café": 3.5, "Croissant": 2.8})
    saved = stand(db_path, tournament["id"], ANA)
    assert saved["cash"] == 77.5
    assert saved["stock"] == {"Café": 10, "Croissant": 0, "Water": 5}
    assert saved["price"] == {"Café": 3.5, "Croissant": 2.8, "Water": 1.2}


@pytest.mark.parametrize(
    ("quantities", "message"),
    [
        ({"Café": 0, "Water": 0}, "Choose a quantity of at least 1 for one product."),
        ({"Café": 2, "Water": -1}, "Quantity must be a whole number, 0 or more."),
        ({"Tea": 1}, "Unknown product: Tea."),
        ({"Café": 40, "Water": 41}, "Not enough cash: buying costs €100.50, you have €100.00."),
    ],
)
def test_tournament_buy_many_refusals_change_nothing(tmp_path, quantities, message):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock_many(db_path, ANA, tournament["id"], quantities),
        message,
    )


def test_tournament_set_prices_one_invalid_price_refuses_all(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    assert_refusal(
        db_path,
        lambda: logic.set_tournament_prices(db_path, ANA, tournament["id"], {"Café": 3.5, "Water": 0}),
        "Price must be more than €0.",
    )


def test_tournament_many_actions_refused_for_outsider_ready_and_complete(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    tid = tournament["id"]
    buy = {"Café": 1}
    prices = {"Café": 3.5}
    for action in (
        lambda: logic.buy_tournament_stock_many(db_path, OUTSIDER, tid, buy),
        lambda: logic.set_tournament_prices(db_path, OUTSIDER, tid, prices),
    ):
        assert_refusal(db_path, action, "You have not joined this tournament.")

    logic.ready_tournament(db_path, ANA, tid)
    for action in (
        lambda: logic.buy_tournament_stock_many(db_path, ANA, tid, buy),
        lambda: logic.set_tournament_prices(db_path, ANA, tid, prices),
    ):
        assert_refusal(db_path, action, "You are Ready and cannot change decisions.")

    set_day(db_path, tid, logic.RUN_DAYS + 1)
    for action in (
        lambda: logic.buy_tournament_stock_many(db_path, BRUNO, tid, buy),
        lambda: logic.set_tournament_prices(db_path, BRUNO, tid, prices),
    ):
        assert_refusal(db_path, action, "The tournament is complete.")


# 5. Tournament screen
def test_tournament_screen_matches_the_old_functions(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    tid = tournament["id"]
    logic.buy_tournament_stock(db_path, ANA, tid, "Café", 10)
    logic.buy_tournament_upgrade(db_path, ANA, tid, "Coffee machine")
    logic.ready_tournament(db_path, BRUNO, tid)

    screen = logic.tournament_screen(db_path, ANA, tid, fetch)
    status = logic.tournament_status(db_path, ANA, tid)
    assert screen["name"] == "Autumn Cup"
    assert screen["code"] == tournament["code"]
    assert screen["organiser"] == ORGANISER
    assert screen["day"] == status["day"] == 1
    assert screen["players"] == status["players"]
    assert screen["weather"] == {"rain": False, "hot": False}
    assert screen["stand"]["cash"] == 50.0
    assert screen["stand"]["ready"] is False
    assert screen["stand"]["stock"] == {"Café": 10, "Croissant": 0, "Water": 0}
    assert screen["stand"]["price"] == {"Café": 4.0, "Croissant": 3.0, "Water": 1.2}
    assert screen["upgrades"] == logic.tournament_upgrades(db_path, ANA, tid) == ["Coffee machine"]
    assert screen["ranking"] is None

    set_day(db_path, tid, logic.RUN_DAYS + 1)
    finished = logic.tournament_screen(db_path, ANA, tid, fetch)
    assert finished["ranking"] == logic.tournament_ranking(db_path, tid)


def test_tournament_screen_refuses_outsider_and_unknown_tournament(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    with pytest.raises(ValueError, match="You have not joined this tournament."):
        logic.tournament_screen(db_path, OUTSIDER, tournament["id"], fetch)
    with pytest.raises(ValueError, match="Tournament was not found."):
        logic.tournament_screen(db_path, ANA, 999, fetch)


def test_my_tournaments_lists_the_players_tournaments(tmp_path):
    db_path = tmp_path / "game.db"
    first = setup_tournament(db_path)
    second = setup_tournament(db_path, players=(ANA,))
    listed = logic.my_tournaments(db_path, ANA)
    assert [row["id"] for row in listed] == [first["id"], second["id"]]
    assert [row["name"] for row in listed] == ["Autumn Cup", "Autumn Cup"]
    assert logic.my_tournaments(db_path, OUTSIDER) == []


# 6. Few reads
@pytest.fixture
def count_statements(monkeypatch):
    # Counts the SQL statements run on local SQLite connections opened by db.py.
    statements = []
    real_connect = sqlite3.connect

    def counting_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        conn.set_trace_callback(statements.append)
        return conn

    monkeypatch.setattr(db.sqlite3, "connect", counting_connect)
    return statements


def queries(statements):
    # Only real reads and writes; transaction bookkeeping and table creation are not round trips we add.
    return [
        sql for sql in statements
        if sql.split()[0].upper() in ("SELECT", "INSERT", "UPDATE", "DELETE")
        and "sqlite_master" not in sql
    ]


def test_tournament_screen_reads_little(tmp_path, count_statements):
    db_path = tmp_path / "game.db"
    tournaments = [setup_tournament(db_path) for _ in range(5)]
    tid = tournaments[2]["id"]
    logic.tournament_screen(db_path, ANA, tid, fetch)  # saves today's weather once

    count_statements.clear()
    logic.tournament_screen(db_path, ANA, tid, fetch)
    assert len(queries(count_statements)) <= 5

    set_day(db_path, tid, logic.RUN_DAYS + 1)
    logic.tournament_screen(db_path, ANA, tid, fetch)
    count_statements.clear()
    logic.tournament_screen(db_path, ANA, tid, fetch)
    assert len(queries(count_statements)) <= 5

    count_statements.clear()
    logic.my_tournaments(db_path, ANA)
    assert len(queries(count_statements)) == 1


# 7. Lazy screens
def app_tree():
    return ast.parse(pathlib.Path("app.py").read_text(encoding="utf-8"))


SCREEN_PAGES = {"practice_screen": "practice", "tournaments_screen": "tournaments", "help_screen": "help"}


def calls_inside_branch(tree, page):
    # Every call found in the body of an `if ... == "<page>"` branch.
    found = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
            and [type(op) for op in node.test.ops] == [ast.Eq]
            and any(isinstance(side, ast.Constant) and side.value == page
                    for side in [node.test.left, *node.test.comparators])
        ):
            for statement in node.body:
                found.update(id(inner) for inner in ast.walk(statement) if isinstance(inner, ast.Call))
    return found


def test_only_the_open_screen_is_built():
    tree = app_tree()
    tabs_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "tabs"
    ]
    assert tabs_calls == []
    for screen, page in SCREEN_PAGES.items():
        screen_calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == screen
        ]
        assert screen_calls, f"{screen} is never called"
        inside = calls_inside_branch(tree, page)
        for call in screen_calls:
            assert id(call) in inside, f"{screen} is called outside the branch for page {page!r}"


def test_practice_and_tournament_card_are_fragments():
    fragments = set()
    for node in ast.walk(app_tree()):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                target = decorator.func if isinstance(decorator, ast.Call) else decorator
                if getattr(target, "attr", None) == "fragment":
                    fragments.add(node.name)
    assert {"practice_screen", "tournament_card"} <= fragments
