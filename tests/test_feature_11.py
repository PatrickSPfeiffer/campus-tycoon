import re

import pytest

import db
import logic


ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"
CARLA = "carla@example.com"
OUTSIDER = "outsider@example.com"


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
        for table in ("tournaments", "stands", "stand_products", "tournament_results")
    }


def assert_refusal(db_path, action, message):
    before = snapshot(db_path)
    with pytest.raises(ValueError, match=re.escape(message)):
        action()
    assert snapshot(db_path) == before


def set_day(db_path, tournament_id, day):
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = ? WHERE id = ?", (day, tournament_id))


def set_stock(db_path, tournament_id, player, product, quantity, price=None):
    with db.open_database(db_path) as conn:
        if price is None:
            conn.execute(
                "UPDATE stand_products SET stock = ? WHERE tournament_id = ? AND player = ? AND product = ?",
                (quantity, tournament_id, player, product),
            )
        else:
            conn.execute(
                "UPDATE stand_products SET stock = ?, price = ? WHERE tournament_id = ? AND player = ? AND product = ?",
                (quantity, price, tournament_id, player, product),
            )


def test_buy_tournament_stock_updates_cash_and_stock(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    product = next(iter(logic.PRODUCTS))
    unit_cost = logic.PRODUCTS[product]["unit_cost"]

    logic.buy_tournament_stock(db_path, ANA, tournament["id"], product, 3)

    assert read_rows(db_path, "SELECT cash FROM stands WHERE player = ?", (ANA,)) == [
        (round(100 - 3 * unit_cost, 2),)
    ]
    assert read_rows(
        db_path,
        "SELECT stock FROM stand_products WHERE player = ? AND product = ?",
        (ANA, product),
    ) == [(3,)]


@pytest.mark.parametrize(
    ("quantity", "message"),
    [(0, "Quantity must be a positive whole number."), (-1, "Quantity must be a positive whole number."), (1.5, "Quantity must be a positive whole number.")],
)
def test_buy_rejects_invalid_quantity_without_changes(tmp_path, quantity, message):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    product = next(iter(logic.PRODUCTS))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock(db_path, ANA, tournament["id"], product, quantity),
        message,
    )


def test_buy_rejects_not_enough_cash_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    product = max(logic.PRODUCTS, key=lambda name: logic.PRODUCTS[name]["unit_cost"])
    quantity = int(100 / logic.PRODUCTS[product]["unit_cost"]) + 1
    cost = round(quantity * logic.PRODUCTS[product]["unit_cost"], 2)
    message = f"Not enough cash: buying costs €{cost:.2f}, you have €100.00."
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock(db_path, ANA, tournament["id"], product, quantity),
        message,
    )


def test_buy_rejects_unknown_product_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock(db_path, ANA, tournament["id"], "Mystery", 1),
        "Unknown product: Mystery.",
    )


def test_buy_rejects_non_member_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    product = next(iter(logic.PRODUCTS))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock(db_path, OUTSIDER, tournament["id"], product, 1),
        "You have not joined this tournament.",
    )


def test_buy_rejects_after_ready_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA, BRUNO))
    logic.ready_tournament(db_path, ANA, tournament["id"])
    product = next(iter(logic.PRODUCTS))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock(db_path, ANA, tournament["id"], product, 1),
        "You are Ready and cannot change decisions.",
    )


def test_buy_rejects_complete_tournament_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_day(db_path, tournament["id"], 6)
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock(db_path, ANA, tournament["id"], next(iter(logic.PRODUCTS)), 1),
        "The tournament is complete.",
    )


def test_buy_rejects_unknown_tournament_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    setup_tournament(db_path, (ANA,))
    assert_refusal(
        db_path,
        lambda: logic.buy_tournament_stock(db_path, ANA, 9999, next(iter(logic.PRODUCTS)), 1),
        "Tournament was not found.",
    )


def test_set_tournament_price_updates_price(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    product = next(iter(logic.PRODUCTS))

    logic.set_tournament_price(db_path, ANA, tournament["id"], product, 2.75)

    assert read_rows(
        db_path,
        "SELECT price FROM stand_products WHERE player = ? AND product = ?",
        (ANA, product),
    ) == [(2.75,)]


@pytest.mark.parametrize(
    ("price", "message"),
    [("2", "Price must be a number."), (0, "Price must be more than €0."), (-1, "Price must be more than €0."), (1.234, "Price can have at most 2 decimals.")],
)
def test_set_tournament_price_rejects_invalid_price_without_changes(tmp_path, price, message):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    product = next(iter(logic.PRODUCTS))
    assert_refusal(
        db_path,
        lambda: logic.set_tournament_price(db_path, ANA, tournament["id"], product, price),
        message,
    )


def test_set_tournament_price_rejects_non_member_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    product = next(iter(logic.PRODUCTS))
    assert_refusal(
        db_path,
        lambda: logic.set_tournament_price(db_path, OUTSIDER, tournament["id"], product, 2.5),
        "You have not joined this tournament.",
    )


def test_set_tournament_price_rejects_after_ready_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA, BRUNO))
    logic.ready_tournament(db_path, ANA, tournament["id"])
    product = next(iter(logic.PRODUCTS))
    assert_refusal(
        db_path,
        lambda: logic.set_tournament_price(db_path, ANA, tournament["id"], product, 2.5),
        "You are Ready and cannot change decisions.",
    )


def test_ready_sets_ready_flag_and_returns_no_close_when_others_not_ready(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)

    result = logic.ready_tournament(db_path, ANA, tournament["id"])

    assert result["closed_day"] is None
    assert read_rows(db_path, "SELECT player, ready FROM stands ORDER BY seat") == [(ANA, 1), (BRUNO, 0)]


def test_ready_twice_is_refused_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    logic.ready_tournament(db_path, ANA, tournament["id"])
    assert_refusal(
        db_path,
        lambda: logic.ready_tournament(db_path, ANA, tournament["id"]),
        "You are already Ready.",
    )


def test_ready_rejects_non_member_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    assert_refusal(
        db_path,
        lambda: logic.ready_tournament(db_path, OUTSIDER, tournament["id"]),
        "You have not joined this tournament.",
    )


def test_ready_rejects_complete_tournament_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_day(db_path, tournament["id"], 6)
    assert_refusal(
        db_path,
        lambda: logic.ready_tournament(db_path, ANA, tournament["id"]),
        "The tournament is complete.",
    )


def test_last_ready_closes_day_automatically_and_saves_sales_and_resets_ready(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    products = sorted(logic.PRODUCTS)
    product = products[0]
    details = logic.PRODUCTS[product]
    price = details["reference_price"]
    stock_before = {ANA: 8, BRUNO: 2}
    for player, quantity in stock_before.items():
        set_stock(db_path, tournament["id"], player, product, quantity, price)
    logic.ready_tournament(db_path, ANA, tournament["id"])

    result = logic.ready_tournament(db_path, BRUNO, tournament["id"])

    assert result["closed_day"]["day"] == 1
    expected_rows = []
    expected_cash = []
    expected_stock = []
    for player in (ANA, BRUNO):
        units = min(logic.demand(price, details["reference_price"]), stock_before[player])
        revenue = round(units * price, 2)
        cogs = round(units * details["unit_cost"], 2)
        for name in products:
            if name == product:
                expected_rows.append((1, player, name, units, revenue, cogs, round(revenue - cogs, 2)))
            else:
                expected_rows.append((1, player, name, 0, 0.0, 0.0, 0.0))
        expected_cash.append((player, round(100 + revenue, 2), 0))
        expected_stock.append((player, stock_before[player] - units))
    assert read_rows(
        db_path,
        "SELECT day, player, product, units_sold, revenue, cogs, gross_profit "
        "FROM tournament_results ORDER BY player, product",
    ) == expected_rows
    assert read_rows(db_path, "SELECT player, cash, ready FROM stands ORDER BY seat") == expected_cash
    assert read_rows(db_path, "SELECT day FROM tournaments") == [(2,)]
    assert read_rows(
        db_path,
        "SELECT player, stock FROM stand_products WHERE product = ? ORDER BY player",
        (product,),
    ) == expected_stock


def test_day_does_not_close_while_someone_is_not_ready(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)

    result = logic.ready_tournament(db_path, ANA, tournament["id"])

    assert result["closed_day"] is None
    assert read_rows(db_path, "SELECT day FROM tournaments") == [(1,)]
    assert read_rows(db_path, "SELECT COUNT(*) FROM tournament_results") == [(0,)]


def test_organiser_can_close_day_early(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)

    result = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    assert result["day"] == 1
    assert read_rows(db_path, "SELECT day FROM tournaments") == [(2,)]


def test_organiser_who_did_not_join_can_close_early(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))

    result = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    assert result["day"] == 1
    assert read_rows(db_path, "SELECT player FROM stands") == [(ANA,)]


def test_non_organiser_member_cannot_close_early_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    assert_refusal(
        db_path,
        lambda: logic.close_tournament_day(db_path, ANA, tournament["id"]),
        "Only the organiser can close the day early.",
    )


def test_tournament_with_no_players_cannot_be_closed_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = create_tournament(db_path)
    assert_refusal(
        db_path,
        lambda: logic.close_tournament_day(db_path, ORGANISER, tournament["id"]),
        "A tournament with no players cannot be closed.",
    )


def test_not_ready_player_still_sells_when_day_closes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    product = next(iter(logic.PRODUCTS))
    price = logic.PRODUCTS[product]["reference_price"]
    set_stock(db_path, tournament["id"], BRUNO, product, 4, price)
    logic.ready_tournament(db_path, ANA, tournament["id"])

    closed = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    assert closed["day"] == 1
    sold = min(logic.demand(price, logic.PRODUCTS[product]["reference_price"]), 4)
    assert read_rows(
        db_path,
        "SELECT units_sold FROM tournament_results WHERE player = ? AND product = ?",
        (BRUNO, product),
    ) == [(sold,)]


def test_closing_day_records_each_product_and_carries_leftover_stock(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    products = sorted(logic.PRODUCTS)
    for name in products:
        set_stock(db_path, tournament["id"], ANA, name, 3, logic.PRODUCTS[name]["reference_price"])

    logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    rows = read_rows(
        db_path,
        "SELECT day, player, product, units_sold, revenue, cogs, gross_profit "
        "FROM tournament_results ORDER BY product",
    )
    assert len(rows) == len(logic.PRODUCTS)
    expected_cash = 100.0
    for row, name in zip(rows, products):
        day, player, product, units, revenue, cogs, gross = row
        info = logic.PRODUCTS[name]
        expected_units = min(logic.demand(info["reference_price"], info["reference_price"]), 3)
        expected_revenue = round(expected_units * info["reference_price"], 2)
        expected_cogs = round(expected_units * info["unit_cost"], 2)
        assert (day, player, product, units, revenue, cogs, gross) == (
            1, ANA, name, expected_units, expected_revenue, expected_cogs, round(expected_revenue - expected_cogs, 2)
        )
        expected_cash = round(expected_cash + expected_revenue, 2)
    assert read_rows(db_path, "SELECT cash, ready FROM stands") == [(expected_cash, 0)]
    for name in products:
        original = 3
        sold = min(logic.demand(logic.PRODUCTS[name]["reference_price"], logic.PRODUCTS[name]["reference_price"]), original)
        assert read_rows(
            db_path,
            "SELECT stock FROM stand_products WHERE player = ? AND product = ?",
            (ANA, name),
        ) == [(original - sold,)]
    assert read_rows(db_path, "SELECT day FROM tournaments") == [(2,)]


@pytest.mark.parametrize("function_name", ["buy", "price", "ready", "close"])
def test_day_six_refuses_all_actions_without_changes(tmp_path, function_name):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (ANA,))
    set_day(db_path, tournament["id"], 6)
    actions = {
        "buy": lambda: logic.buy_tournament_stock(db_path, ANA, tournament["id"], next(iter(logic.PRODUCTS)), 1),
        "price": lambda: logic.set_tournament_price(db_path, ANA, tournament["id"], next(iter(logic.PRODUCTS)), 2.0),
        "ready": lambda: logic.ready_tournament(db_path, ANA, tournament["id"]),
        "close": lambda: logic.close_tournament_day(db_path, ORGANISER, tournament["id"]),
    }
    assert_refusal(db_path, actions[function_name], "The tournament is complete.")


def test_ranking_is_refused_before_completion_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    assert_refusal(
        db_path,
        lambda: logic.tournament_ranking(db_path, tournament["id"]),
        "The tournament is not complete.",
    )


def test_ranking_orders_by_gain_then_seat_and_values_stock_at_cost(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path, (CARLA, ANA, BRUNO))
    product = next(iter(logic.PRODUCTS))
    unit_cost = logic.PRODUCTS[product]["unit_cost"]
    ana_cash = round(110 - 2 * unit_cost, 2)
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = 6 WHERE id = ?", (tournament["id"],))
        conn.execute("UPDATE stands SET cash = 110 WHERE player = ?", (CARLA,))
        conn.execute("UPDATE stands SET cash = ? WHERE player = ?", (ana_cash, ANA))
        conn.execute("UPDATE stands SET cash = 130 WHERE player = ?", (BRUNO,))
        conn.execute(
            "UPDATE stand_products SET stock = 2 WHERE player = ? AND product = ?",
            (ANA, product),
        )

    ranking = logic.tournament_ranking(db_path, tournament["id"])

    assert [row["player"] for row in ranking] == [BRUNO, CARLA, ANA]
    assert [row["seat"] for row in ranking] == [3, 1, 2]
    assert [row["gain"] for row in ranking] == [30.0, 10.0, 10.0]
    assert ranking[2]["final_cash"] == ana_cash
    assert ranking[2]["stock_at_cost"] == round(2 * unit_cost, 2)


def test_tournament_units_sold_uses_demand_caps_stock_and_keeps_stands_independent():
    names = list(logic.PRODUCTS)
    product = names[0]
    reference = logic.PRODUCTS[product]["reference_price"]
    stands = {
        ANA: {"stock": {product: 20}, "price": {product: reference}},
        BRUNO: {"stock": {product: 5}, "price": {product: reference}},
        CARLA: {"stock": {product: 20}, "price": {product: 2 * reference + 0.01}},
        OUTSIDER: {"stock": {product: 2}, "price": {product: reference}},
    }

    sold = logic.tournament_units_sold(stands)

    assert sold == {ANA: {product: 10}, BRUNO: {product: 5}, CARLA: {product: 0}, OUTSIDER: {product: 2}}


def test_tournament_units_sold_uses_each_products_reference_price():
    stands = {
        ANA: {
            "stock": {name: 20 for name in logic.PRODUCTS},
            "price": {name: details["reference_price"] for name, details in logic.PRODUCTS.items()},
        }
    }

    assert logic.tournament_units_sold(stands) == {
        ANA: {name: logic.demand(details["reference_price"], details["reference_price"]) for name, details in logic.PRODUCTS.items()}
    }


def test_closing_five_days_completes_tournament_and_enables_ranking(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    for expected_day in range(1, 6):
        assert read_rows(db_path, "SELECT day FROM tournaments") == [(expected_day,)]
        result = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])
        assert result["day"] == expected_day
    assert read_rows(db_path, "SELECT day FROM tournaments") == [(6,)]
    assert read_rows(db_path, "SELECT COUNT(*) FROM tournament_results") == [(5 * 2 * len(logic.PRODUCTS),)]
    ranking = logic.tournament_ranking(db_path, tournament["id"])
    assert [row["player"] for row in ranking] == [ANA, BRUNO]


@pytest.mark.parametrize("function_name", ["buy", "price", "ready", "close", "ranking"])
def test_unknown_tournament_is_refused_by_every_action(tmp_path, function_name):
    db_path = tmp_path / "game.db"
    setup_tournament(db_path, (ANA,))
    product = next(iter(logic.PRODUCTS))
    actions = {
        "buy": lambda: logic.buy_tournament_stock(db_path, ANA, 9999, product, 1),
        "price": lambda: logic.set_tournament_price(db_path, ANA, 9999, product, 2.0),
        "ready": lambda: logic.ready_tournament(db_path, ANA, 9999),
        "close": lambda: logic.close_tournament_day(db_path, ORGANISER, 9999),
        "ranking": lambda: logic.tournament_ranking(db_path, 9999),
    }
    assert_refusal(db_path, actions[function_name], "Tournament was not found.")


def test_outsider_cannot_close_day_early_without_changes(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = setup_tournament(db_path)
    assert_refusal(
        db_path,
        lambda: logic.close_tournament_day(db_path, OUTSIDER, tournament["id"]),
        "Only the organiser can close the day early.",
    )


def test_tournament_units_sold_middle_price_band_sells_five():
    product = next(iter(logic.PRODUCTS))
    reference = logic.PRODUCTS[product]["reference_price"]
    stands = {ANA: {"stock": {product: 20}, "price": {product: round(1.5 * reference, 2)}}}

    assert logic.tournament_units_sold(stands) == {ANA: {product: 5}}
