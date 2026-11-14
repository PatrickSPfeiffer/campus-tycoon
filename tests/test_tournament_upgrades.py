import re

import pytest

import db
import logic


ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"
OUTSIDER = "outsider@example.com"

UPGRADE = "Coffee machine"
COST = 30.0


def read_rows(db_path, sql, parameters=()):
    with db.open_database(db_path) as conn:
        return conn.execute(sql, parameters).fetchall()


def create_tournament(db_path):
    return logic.create_tournament(db_path, ORGANISER, "Autumn Cup")


def setup_tournament(db_path, players=(ANA, BRUNO)):
    tournament = create_tournament(db_path)
    for player in players:
        logic.join_tournament(db_path, player, tournament["code"])
    return tournament


def snapshot(db_path):
    return {
        table: read_rows(db_path, f"SELECT * FROM {table} ORDER BY rowid")
        for table in ("tournaments", "stands", "stand_products", "tournament_results", "stand_upgrades")
    }


def assert_refusal(db_path, action, message):
    before = snapshot(db_path)
    with pytest.raises(ValueError, match=re.escape(message)):
        action()
    assert snapshot(db_path) == before


def set_day(db_path, tournament_id, day):
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = ? WHERE id = ?", (day, tournament_id))


def set_cash(db_path, tournament_id, player, cash):
    with db.open_database(db_path) as conn:
        conn.execute(
            "UPDATE stands SET cash = ? WHERE tournament_id = ? AND player = ?",
            (cash, tournament_id, player),
        )


def test_catalogue_has_coffee_machine():
    assert logic.UPGRADES[UPGRADE]["cost"] == COST
    assert logic.UPGRADES[UPGRADE]["reference_price"] == 5.0


def test_stand_upgrades_table_exists_and_is_empty(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)

    assert read_rows(db_path, "SELECT tournament_id, player, upgrade FROM stand_upgrades ORDER BY rowid") == []


def test_buy_upgrade_updates_cash_and_ownership(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    products_before = read_rows(
        db_path,
        "SELECT product, stock, price FROM stand_products WHERE tournament_id = ? AND player = ? ORDER BY rowid",
        (tournament["id"], ANA),
    )

    returned_cash = logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE)

    assert returned_cash == 70.0
    assert read_rows(
        db_path, "SELECT cash FROM stands WHERE tournament_id = ? AND player = ?", (tournament["id"], ANA)
    ) == [(70.0,)]
    assert read_rows(
        db_path,
        "SELECT tournament_id, player, upgrade FROM stand_upgrades ORDER BY rowid",
    ) == [(tournament["id"], ANA, UPGRADE)]
    assert read_rows(
        db_path,
        "SELECT product, stock, price FROM stand_products WHERE tournament_id = ? AND player = ? ORDER BY rowid",
        (tournament["id"], ANA),
    ) == products_before
    assert read_rows(
        db_path, "SELECT cash FROM stands WHERE tournament_id = ? AND player = ?", (tournament["id"], BRUNO)
    ) == [(100.0,)]


def test_buy_upgrade_accepts_exact_cash(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_cash(db_path, tournament["id"], ANA, COST)

    assert logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE) == 0.0
    assert read_rows(db_path, "SELECT cash FROM stands WHERE player = ?", (ANA,)) == [(0.0,)]


def test_buy_upgrade_rejects_not_enough_cash(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_cash(db_path, tournament["id"], ANA, 29.99)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE),
        "Not enough cash: buying costs €30.00, you have €29.99.",
    )


def test_buy_upgrade_rejects_unknown_tournament(tmp_path):
    db_path = tmp_path / "game.db"
    setup_tournament(db_path, (ANA,))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, 9999, UPGRADE),
        "Tournament was not found.",
    )


def test_buy_upgrade_rejects_complete_tournament(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_day(db_path, tournament["id"], logic.RUN_DAYS + 1)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE),
        "The tournament is complete.",
    )


def test_buy_upgrade_rejects_player_who_has_not_joined(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, OUTSIDER, tournament["id"], UPGRADE),
        "You have not joined this tournament.",
    )


def test_buy_upgrade_rejects_after_ready(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    logic.ready_tournament(db_path, ANA, tournament["id"])
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE),
        "You are Ready and cannot change decisions.",
    )


def test_buy_upgrade_rejects_unknown_upgrade(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], "Mystery"),
        "Unknown upgrade.",
    )


def test_buy_upgrade_rejects_already_owned_upgrade(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE),
        "You already have this upgrade.",
    )
    assert read_rows(
        db_path,
        "SELECT tournament_id, player, upgrade FROM stand_upgrades ORDER BY rowid",
    ) == [(tournament["id"], ANA, UPGRADE)]


def test_complete_tournament_refusal_precedes_unknown_upgrade(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_day(db_path, tournament["id"], logic.RUN_DAYS + 1)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], "Mystery"),
        "The tournament is complete.",
    )


def test_ready_refusal_precedes_unknown_upgrade(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    logic.ready_tournament(db_path, ANA, tournament["id"])
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], "Mystery"),
        "You are Ready and cannot change decisions.",
    )


def test_unknown_upgrade_refusal_precedes_not_enough_cash(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_cash(db_path, tournament["id"], ANA, 0.0)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], "Mystery"),
        "Unknown upgrade.",
    )


def test_already_owned_refusal_precedes_not_enough_cash(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE)
    set_cash(db_path, tournament["id"], ANA, 0.0)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE),
        "You already have this upgrade.",
    )


def test_upgrades_are_independent_between_players_and_tournaments(tmp_path):
    db_path = tmp_path / "game.db"
    first = setup_tournament(db_path)
    logic.buy_tournament_upgrade(db_path, ANA, first["id"], UPGRADE)
    second = logic.create_tournament(db_path, "another-organiser@example.com", "Winter Cup")
    logic.join_tournament(db_path, ANA, second["code"])

    assert logic.tournament_upgrades(db_path, BRUNO, first["id"]) == []
    assert logic.tournament_upgrades(db_path, ANA, second["id"]) == []


def test_only_purchase_gives_gain_minus_30_in_ranking(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE)
    for _ in range(logic.RUN_DAYS):
        logic.ready_tournament(db_path, ANA, tournament["id"])
        logic.ready_tournament(db_path, BRUNO, tournament["id"])

    ranking = logic.tournament_ranking(db_path, tournament["id"])

    assert {row["player"]: row["gain"] for row in ranking} == {ANA: -30.0, BRUNO: 0.0}
    assert ranking[0]["player"] == BRUNO


def test_tournament_upgrades_is_empty_at_start(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))

    assert logic.tournament_upgrades(db_path, ANA, tournament["id"]) == []


def test_tournament_upgrades_lists_purchased_upgrade(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    logic.buy_tournament_upgrade(db_path, ANA, tournament["id"], UPGRADE)

    assert logic.tournament_upgrades(db_path, ANA, tournament["id"]) == [UPGRADE]


def test_tournament_upgrades_are_alphabetical(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    with db.open_database(db_path) as conn:
        conn.executemany(
            "INSERT INTO stand_upgrades (tournament_id, player, upgrade) VALUES (?, ?, ?)",
            [(tournament["id"], ANA, "Zeta"), (tournament["id"], ANA, "Alpha")],
        )

    assert logic.tournament_upgrades(db_path, ANA, tournament["id"]) == ["Alpha", "Zeta"]


def test_tournament_upgrades_rejects_unknown_tournament(tmp_path):
    db_path = tmp_path / "game.db"
    setup_tournament(db_path, (ANA,))

    with pytest.raises(ValueError, match=re.escape("Tournament was not found.")):
        logic.tournament_upgrades(db_path, ANA, 9999)


def test_tournament_upgrades_rejects_player_who_has_not_joined(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))

    with pytest.raises(ValueError, match=re.escape("You have not joined this tournament.")):
        logic.tournament_upgrades(db_path, OUTSIDER, tournament["id"])
