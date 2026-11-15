"""Checks for specs/feature-security-pass.md — one group of tests per 'Done when' line."""

import math
import tomllib
from pathlib import Path

import pytest

import db
import logic

ROOT = Path(__file__).parent.parent
ORGANISER = "org@example.com"
ANA = "ana@example.com"


def count_tournaments(db_path):
    with db.open_database(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM tournaments").fetchone()[0]


# 1. Names accepted
@pytest.mark.parametrize("name", ["Autumn Cup", "Café Cup", "Nova's Cup (2026)!"])
def test_normal_tournament_names_are_accepted(tmp_path, name):
    tournament = logic.create_tournament(tmp_path / "game.db", ORGANISER, name)
    assert tournament["name"] == name


# 2. Names rejected: Markdown or HTML would be rendered for every player
@pytest.mark.parametrize("name", ["[click](http://x.y)", "<b>hi</b>", "**bold**", "`code`"])
def test_names_with_markup_are_rejected_and_nothing_is_saved(tmp_path, name):
    db_path = tmp_path / "game.db"
    with pytest.raises(ValueError, match="name"):
        logic.create_tournament(db_path, ORGANISER, name)
    assert count_tournaments(db_path) == 0


# 3. Join codes
@pytest.mark.parametrize("code", ["ABC", "A" * 1000, "AB C12", "ABC12!"])
def test_malformed_join_codes_are_rejected(tmp_path, code):
    db_path = tmp_path / "game.db"
    logic.create_tournament(db_path, ORGANISER, "Autumn Cup")
    with pytest.raises(ValueError, match="code"):
        logic.join_tournament(db_path, ANA, code)
    assert logic.get_my_stands(db_path, ANA) == []


def test_well_formed_unknown_code_is_still_not_found(tmp_path):
    db_path = tmp_path / "game.db"
    with pytest.raises(ValueError, match="not found"):
        logic.join_tournament(db_path, ANA, "NOPE99")


def test_lowercase_code_with_spaces_still_joins(tmp_path):
    db_path = tmp_path / "game.db"
    tournament = logic.create_tournament(db_path, ORGANISER, "Autumn Cup")
    joined = logic.join_tournament(db_path, ANA, f"  {tournament['code'].lower()}  ")
    assert joined["seat"] == 1


# 4. Prices: practice
def test_practice_price_of_1000_is_accepted(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.set_price(db_path, ANA, "Café", 1000.0)
    assert game["price"]["Café"] == 1000.0


@pytest.mark.parametrize("price", [1000.01, math.inf, math.nan])
def test_practice_price_too_high_or_not_finite_is_rejected(tmp_path, price):
    db_path = tmp_path / "game.db"
    logic.set_price(db_path, ANA, "Café", 6.0)
    with pytest.raises(ValueError):
        logic.set_price(db_path, ANA, "Café", price)
    assert logic.load_game(db_path, ANA)["price"]["Café"] == 6.0


# 4. Prices: tournament
def setup_stand(db_path):
    tournament = logic.create_tournament(db_path, ORGANISER, "Autumn Cup")
    logic.join_tournament(db_path, ANA, tournament["code"])
    return tournament["id"]


def stand_price(db_path, product):
    stand = logic.get_my_stands(db_path, ANA)[0]
    return next(p["price"] for p in stand["products"] if p["product"] == product)


def test_tournament_price_of_1000_is_accepted(tmp_path):
    db_path = tmp_path / "game.db"
    tournament_id = setup_stand(db_path)
    logic.set_tournament_price(db_path, ANA, tournament_id, "Café", 1000.0)
    assert stand_price(db_path, "Café") == 1000.0


@pytest.mark.parametrize("price", [1000.01, math.inf, math.nan])
def test_tournament_price_too_high_or_not_finite_is_rejected(tmp_path, price):
    db_path = tmp_path / "game.db"
    tournament_id = setup_stand(db_path)
    before = stand_price(db_path, "Café")
    with pytest.raises(ValueError):
        logic.set_tournament_price(db_path, ANA, tournament_id, "Café", price)
    assert stand_price(db_path, "Café") == before


# 5. The public app never shows tracebacks
def test_streamlit_config_hides_error_details():
    config = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text())
    assert config["client"]["showErrorDetails"] == "none"


# 6. Secrets stay out of git
def test_gitignore_keeps_secrets_and_databases_out():
    lines = (ROOT / ".gitignore").read_text().splitlines()
    for entry in [".streamlit/secrets.toml", ".env", "*.db"]:
        assert entry in lines


def test_env_example_has_names_but_no_values():
    values = {}
    for line in (ROOT / ".env.example").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, _, value = line.partition("=")
            values[name.strip()] = value.strip()
    assert values == {"TURSO_DATABASE_URL": "", "TURSO_AUTH_TOKEN": ""}
