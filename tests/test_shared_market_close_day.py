import db
import logic


ORGANISER = "organiser@example.com"
ANA = "ana@example.com"
BRUNO = "bruno@example.com"
CARLA = "carla@example.com"
CAFE = "Café"


def setup_tournament(db_path, cafe_stands, day=1):
    tournament = logic.create_tournament(db_path, ORGANISER, "Autumn Cup")
    tournament_id = tournament["id"]
    for player, price, stock in cafe_stands:
        logic.join_tournament(db_path, player, tournament["code"])

    # Set starting stock directly so buying it does not change the starting cash.
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = ? WHERE id = ?", (day, tournament_id))
        for player, price, stock in cafe_stands:
            conn.execute(
                "UPDATE stand_products SET price = ?, stock = ? "
                "WHERE tournament_id = ? AND player = ? AND product = ?",
                (price, stock, tournament_id, player, CAFE),
            )
    return tournament_id


def cafe_sales(result):
    return {
        player: products[CAFE]["units_sold"]
        for player, products in result["by_player"].items()
    }


def test_close_day_saves_team_brief_sales_revenue_cash_and_stock(tmp_path):
    db_path = tmp_path / "game.db"
    tournament_id = setup_tournament(db_path, [(ANA, 3.50, 15), (BRUNO, 6.00, 10)])

    result = logic.close_tournament_day(db_path, ORGANISER, tournament_id)

    assert result["day"] == 1
    with db.open_database(db_path) as conn:
        sales = conn.execute(
            "SELECT player, units_sold, revenue FROM tournament_results "
            "WHERE tournament_id = ? AND day = ? AND product = ? ORDER BY player",
            (tournament_id, 1, CAFE),
        ).fetchall()
    assert sales == [(ANA, 15, 52.50), (BRUNO, 5, 30.00)]

    stands = db.get_tournament_stands(db_path, tournament_id)
    assert (stands[ANA]["cash"], stands[ANA]["stock"][CAFE]) == (152.50, 0)
    assert (stands[BRUNO]["cash"], stands[BRUNO]["stock"][CAFE]) == (130.00, 5)


def test_close_day_gives_all_sales_to_the_cheaper_stand(tmp_path):
    db_path = tmp_path / "game.db"
    tournament_id = setup_tournament(db_path, [(ANA, 3.90, 20), (BRUNO, 4.00, 20)])

    result = logic.close_tournament_day(db_path, ORGANISER, tournament_id)

    assert cafe_sales(result) == {ANA: 20, BRUNO: 0}


def test_close_day_uses_tournament_day_to_rotate_tied_stands(tmp_path):
    db_path = tmp_path / "game.db"
    cafe_stands = [(ANA, 4.00, 20), (BRUNO, 4.00, 20), (CARLA, 9.00, 20)]

    day_one_id = setup_tournament(db_path, cafe_stands, day=1)
    day_two_id = setup_tournament(db_path, cafe_stands, day=2)

    day_one = logic.close_tournament_day(db_path, ORGANISER, day_one_id)
    day_two = logic.close_tournament_day(db_path, ORGANISER, day_two_id)

    assert (cafe_sales(day_one), cafe_sales(day_two)) == (
        {ANA: 16, BRUNO: 14, CARLA: 0},
        {ANA: 14, BRUNO: 16, CARLA: 0},
    )


def test_tournament_market_sales_includes_every_player_and_product(tmp_path):
    db_path = tmp_path / "game.db"
    tournament_id = setup_tournament(db_path, [(ANA, 3.90, 20), (BRUNO, 4.00, 20)])
    stands = db.get_tournament_stands(db_path, tournament_id)

    assert logic.tournament_market_sales(stands, day=1) == {
        ANA: {"Café": 20, "Croissant": 0, "Water": 0},
        BRUNO: {"Café": 0, "Croissant": 0, "Water": 0},
    }
