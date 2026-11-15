import pytest

import db
import logic


ORGANISER = "organiser@example.com"
PLAYER = "player@example.com"


def create_tournament(db_path):
    tournament = logic.create_tournament(db_path, ORGANISER, "Weather Cup")
    logic.join_tournament(db_path, PLAYER, tournament["code"])
    return tournament


def set_product(db_path, tournament_id, product, price, stock):
    with db.open_database(db_path) as conn:
        conn.execute(
            "UPDATE stand_products SET price = ?, stock = ? "
            "WHERE tournament_id = ? AND player = ? AND product = ?",
            (price, stock, tournament_id, PLAYER, product),
        )


def test_read_weather_marks_rain():
    data = {
        "daily": {"precipitation_sum": [3.2], "temperature_2m_max": [18]},
    }

    assert logic.read_weather(data) == {"rain": True, "hot": False}


def test_read_weather_marks_hot():
    data = {
        "daily": {"precipitation_sum": [0], "temperature_2m_max": [27]},
    }

    assert logic.read_weather(data) == {"rain": False, "hot": True}


def test_read_weather_rejects_broken_answer():
    with pytest.raises(ValueError):
        logic.read_weather({"daily": {"precipitation_sum": [3.2]}})


def test_tournament_weather_fetches_and_saves_once_per_day(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    calls = []

    def fetch():
        calls.append(1)
        return {"daily": {"precipitation_sum": [3.2], "temperature_2m_max": [18]}}

    first = logic.tournament_weather(db_path, tournament["id"], fetch)
    second = logic.tournament_weather(db_path, tournament["id"], fetch)

    assert first == second == {"rain": True, "hot": False}
    assert len(calls) == 1
    assert db.get_tournament_weather(db_path, tournament["id"], 1) == first


def test_tournament_weather_fetches_again_on_a_new_day(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    responses = iter(
        [
            {"daily": {"precipitation_sum": [3.2], "temperature_2m_max": [18]}},
            {"daily": {"precipitation_sum": [0], "temperature_2m_max": [27]}},
        ]
    )
    calls = []

    def fetch():
        calls.append(1)
        return next(responses)

    day_one = logic.tournament_weather(db_path, tournament["id"], fetch)
    with db.open_database(db_path) as conn:
        conn.execute("UPDATE tournaments SET day = 2 WHERE id = ?", (tournament["id"],))
    day_two = logic.tournament_weather(db_path, tournament["id"], fetch)

    assert day_one == {"rain": True, "hot": False}
    assert day_two == {"rain": False, "hot": True}
    assert len(calls) == 2


def test_tournament_weather_api_failure_saves_no_effect(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    calls = []

    def fetch():
        calls.append(1)
        raise OSError("API is down")

    first = logic.tournament_weather(db_path, tournament["id"], fetch)
    second = logic.tournament_weather(db_path, tournament["id"], fetch)

    assert first == second == {"rain": False, "hot": False}
    assert len(calls) == 1
    assert db.get_tournament_weather(db_path, tournament["id"], 1) == first


def test_db_tournament_weather_round_trip(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    weather = {"rain": True, "hot": False}

    db.save_tournament_weather(db_path, tournament["id"], 1, weather)

    assert db.get_tournament_weather(db_path, tournament["id"], 1) == weather
    assert db.get_tournament_weather(db_path, tournament["id"], 2) is None


def test_normal_day_cafe_sales_are_five_at_five_euros(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    set_product(db_path, tournament["id"], "Café", 5.00, 20)

    result = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    assert result["by_player"][PLAYER]["Café"]["units_sold"] == 5


def test_rainy_day_cafe_sales_are_ten_at_five_euros(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    set_product(db_path, tournament["id"], "Café", 5.00, 20)
    db.save_tournament_weather(db_path, tournament["id"], 1, {"rain": True, "hot": False})

    result = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    assert result["by_player"][PLAYER]["Café"]["units_sold"] == 10


def test_normal_day_water_sales_are_five_at_one_fifty_euros(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    set_product(db_path, tournament["id"], "Water", 1.50, 20)

    result = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    assert result["by_player"][PLAYER]["Water"]["units_sold"] == 5


def test_hot_day_water_sales_are_ten_at_one_fifty_euros(tmp_path):
    db_path = tmp_path / "weather.db"
    tournament = create_tournament(db_path)
    set_product(db_path, tournament["id"], "Water", 1.50, 20)
    db.save_tournament_weather(db_path, tournament["id"], 1, {"rain": False, "hot": True})

    result = logic.close_tournament_day(db_path, ORGANISER, tournament["id"])

    assert result["by_player"][PLAYER]["Water"]["units_sold"] == 10
