"""Checks for specs/feature-history-charts.md — one test per 'Done when' line."""

import logic

ANA = "ana@example.com"
BRUNO = "bruno@example.com"
KEYS = ["Day", "Café", "Croissant", "Water", "Total"]


def day(number, **gross_profit_by_product):
    # A saved day as logic.get_results returns it, with only the gross profit filled in.
    return {
        "day": number,
        "by_product": {
            name: {"units_sold": 0, "revenue": 0.0, "cogs": 0.0, "gross_profit": value}
            for name, value in gross_profit_by_product.items()
        },
    }


# 1. No history
def test_no_history_gives_empty_lists():
    assert logic.profit_chart_data([]) == {key: [] for key in KEYS}


# 2. Accepted: a real run, read back from the database
def test_two_traded_days_give_gross_profit_per_product_and_total(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.buy(db_path, ANA, "Café", 10)  # €20.00
    logic.buy(db_path, ANA, "Water", 10)  # €5.00
    logic.trade_day(db_path, ANA)  # sells everything at reference prices
    logic.trade_day(db_path, ANA)  # no stock left: sells nothing

    data = logic.profit_chart_data(logic.get_results(db_path, ANA))

    assert data == {
        "Day": [1, 2],
        "Café": [20.0, 0.0],
        "Croissant": [0.0, 0.0],
        "Water": [7.0, 0.0],
        "Total": [27.0, 0.0],
    }
    for key in KEYS[1:]:
        assert all(isinstance(value, float) for value in data[key])


# 3. Order of keys and days
def test_keys_follow_catalogue_and_days_are_sorted():
    results = [
        day(2, **{"Café": 4.0, "Croissant": 1.5, "Water": 0.7}),
        day(1, **{"Café": 2.0, "Croissant": 3.0, "Water": 1.4}),
    ]
    data = logic.profit_chart_data(results)
    assert list(data) == KEYS
    assert data["Day"] == [1, 2]
    assert data["Café"] == [2.0, 4.0]
    assert data["Total"] == [6.4, 6.2]


# 4. Edge case: a product missing from a day counts as 0
def test_missing_product_counts_as_zero():
    data = logic.profit_chart_data([day(1, **{"Café": 8.0})])
    assert data["Croissant"] == [0.0]
    assert data["Water"] == [0.0]
    assert data["Total"] == [8.0]


# 5. Rounding
def test_total_is_rounded_to_two_decimals():
    data = logic.profit_chart_data([day(1, **{"Café": 0.1, "Water": 0.2})])
    assert data["Total"] == [0.3]


# 6. Privacy: another player's results never appear
def test_charts_only_show_the_players_own_results(tmp_path):
    db_path = tmp_path / "game.db"
    logic.load_game(db_path, ANA)
    logic.load_game(db_path, BRUNO)
    logic.buy(db_path, BRUNO, "Café", 10)
    logic.trade_day(db_path, BRUNO)

    assert logic.profit_chart_data(logic.get_results(db_path, ANA)) == {key: [] for key in KEYS}
    assert logic.profit_chart_data(logic.get_results(db_path, BRUNO))["Café"] == [20.0]
