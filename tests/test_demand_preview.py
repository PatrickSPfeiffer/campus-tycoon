from copy import deepcopy

import logic


def test_new_game_previews_demand_at_reference_prices_with_no_stock():
    game = logic.start_game()

    assert logic.demand_preview(game) == {
        product: {"price": details["reference_price"], "demand": 10, "stock": 0, "will_sell": 0}
        for product, details in logic.PRODUCTS.items()
    }


def test_preview_limits_sales_by_price_and_stock_for_each_product():
    game = logic.start_game()
    game["price"].update({"Café": 4.00, "Croissant": 3.50, "Water": 2.41})
    game["stock"].update({"Café": 20, "Croissant": 3, "Water": 10})

    assert logic.demand_preview(game) == {
        "Café": {"price": 4.00, "demand": 10, "stock": 20, "will_sell": 10},
        "Croissant": {"price": 3.50, "demand": 5, "stock": 3, "will_sell": 3},
        "Water": {"price": 2.41, "demand": 0, "stock": 10, "will_sell": 0},
    }


def test_preview_respects_water_price_boundaries():
    game = logic.start_game()
    game["stock"]["Water"] = 20

    for price, expected_units in [(1.20, 10), (1.21, 5), (2.40, 5), (2.41, 0)]:
        game["price"]["Water"] = price

        assert logic.demand_preview(game)["Water"] == {
            "price": price, "demand": expected_units, "stock": 20, "will_sell": expected_units,
        }


def test_preview_does_not_change_the_game():
    game = logic.start_game()
    game["price"]["Croissant"] = 3.50
    game["stock"]["Croissant"] = 3
    before = deepcopy(game)

    logic.demand_preview(game)

    assert game == before
