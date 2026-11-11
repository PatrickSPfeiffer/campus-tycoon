import pytest

import db
import logic


ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"
CARLA = "carla@example.com"


def read_rows(db_path, sql, parameters=()):
    with db.open_database(db_path) as conn:
        return conn.execute(sql, parameters).fetchall()


def create_tournament(db_path, name="Autumn Cup"):
    return logic.create_tournament(db_path, ORGANISER, name)


def test_create_tournament_starts_at_day_one_with_unique_code(tmp_path):
    db_path = tmp_path / "game.db"

    first = create_tournament(db_path, "Autumn Cup")
    second = create_tournament(db_path, "Winter Cup")

    tournaments = read_rows(
        db_path,
        "SELECT name, code, organiser, day FROM tournaments ORDER BY id",
    )
    assert tournaments == [
        ("Autumn Cup", first["code"], ORGANISER, 1),
        ("Winter Cup", second["code"], ORGANISER, 1),
    ]
    assert len(first["code"]) == 6
    assert len(second["code"]) == 6
    assert all(character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for character in first["code"])
    assert all(character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for character in second["code"])
    assert first["code"] != second["code"]
    assert read_rows(db_path, "SELECT COUNT(*) FROM stands") == [(0,)]


def test_create_tournament_trims_valid_name(tmp_path):
    db_path = tmp_path / "game.db"

    tournament = create_tournament(db_path, "  Autumn Cup  ")

    assert tournament["name"] == "Autumn Cup"
    assert read_rows(db_path, "SELECT name FROM tournaments") == [("Autumn Cup",)]


def test_create_tournament_rejects_invalid_names_without_saving(tmp_path):
    db_path = tmp_path / "game.db"

    for name in ["", "   ", "a" * 41]:
        with pytest.raises(ValueError, match="name"):
            logic.create_tournament(db_path, ORGANISER, name)
        assert read_rows(db_path, "SELECT COUNT(*) FROM tournaments") == [(0,)]
        assert read_rows(db_path, "SELECT COUNT(*) FROM stands") == [(0,)]
        assert read_rows(db_path, "SELECT COUNT(*) FROM stand_products") == [(0,)]


def test_joining_three_players_assigns_seats_in_order(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = create_tournament(db_path)

    logic.join_tournament(db_path, ANA, tournament["code"])
    logic.join_tournament(db_path, BRUNO, tournament["code"])
    logic.join_tournament(db_path, CARLA, tournament["code"])

    assert read_rows(
        db_path,
        "SELECT player, seat FROM stands ORDER BY seat",
    ) == [(ANA, 1), (BRUNO, 2), (CARLA, 3)]


def test_join_creates_exact_starting_stand(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = create_tournament(db_path)

    logic.join_tournament(db_path, ANA, tournament["code"])

    assert read_rows(
        db_path,
        "SELECT player, seat, cash, ready FROM stands",
    ) == [(ANA, 1, 100.0, 0)]
    products = read_rows(
        db_path,
        "SELECT product, stock, price FROM stand_products ORDER BY product",
    )
    assert products == sorted(
        (name, 0, details["reference_price"])
        for name, details in logic.PRODUCTS.items()
    )


def test_join_accepts_lowercase_and_spaced_code(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = create_tournament(db_path)

    logic.join_tournament(db_path, ANA, f"  {tournament['code'].lower()}  ")

    assert read_rows(db_path, "SELECT player, seat FROM stands") == [(ANA, 1)]


def test_join_rejects_unknown_code_without_saving(tmp_path):
    db_path = tmp_path / "game.db"
    create_tournament(db_path)
    before = {
        "tournaments": read_rows(db_path, "SELECT * FROM tournaments"),
        "stands": read_rows(db_path, "SELECT * FROM stands"),
        "stand_products": read_rows(db_path, "SELECT * FROM stand_products"),
    }

    with pytest.raises(ValueError, match="code|tournament"):
        logic.join_tournament(db_path, ANA, "NOPE99")

    assert read_rows(db_path, "SELECT * FROM tournaments") == before["tournaments"]
    assert read_rows(db_path, "SELECT * FROM stands") == before["stands"]
    assert read_rows(db_path, "SELECT * FROM stand_products") == before["stand_products"]


def test_join_rejects_past_day_one_without_saving(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = create_tournament(db_path)
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = 2 WHERE id = ?", (tournament["id"],))
    before = {
        "tournaments": read_rows(db_path, "SELECT * FROM tournaments"),
        "stands": read_rows(db_path, "SELECT * FROM stands"),
        "stand_products": read_rows(db_path, "SELECT * FROM stand_products"),
    }

    with pytest.raises(ValueError, match="closed|day"):
        logic.join_tournament(db_path, ANA, tournament["code"])

    assert read_rows(db_path, "SELECT * FROM tournaments") == before["tournaments"]
    assert read_rows(db_path, "SELECT * FROM stands") == before["stands"]
    assert read_rows(db_path, "SELECT * FROM stand_products") == before["stand_products"]


def test_join_rejects_duplicate_player_without_saving(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = create_tournament(db_path)
    logic.join_tournament(db_path, ANA, tournament["code"])
    before = {
        "stands": read_rows(db_path, "SELECT * FROM stands"),
        "stand_products": read_rows(db_path, "SELECT * FROM stand_products"),
    }

    with pytest.raises(ValueError, match="already"):
        logic.join_tournament(db_path, ANA, tournament["code"])

    assert read_rows(db_path, "SELECT * FROM stands") == before["stands"]
    assert read_rows(db_path, "SELECT * FROM stand_products") == before["stand_products"]


def test_create_tournament_accepts_name_of_exactly_40_characters(tmp_path):
    db_path = tmp_path / "game.db"
    name = "A" * 40

    tournament = create_tournament(db_path, f"  {name}  ")

    assert tournament["name"] == name
    assert read_rows(db_path, "SELECT name FROM tournaments") == [(name,)]
