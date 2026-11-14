"""Checks for specs/feature-ai-advisor.md — one test per testable Done when line."""

import copy
import json

import pytest

import advisor
import logic

ANA = "ana@example.com"
FALLBACK_PRICES = {"Café": 8.0, "Croissant": 6.0, "Water": 2.4}


def valid_answer():
    return json.dumps(
        {
            "Café": {"price": 4.5, "reason": "Keeps the price near the reference."},
            "Croissant": {"price": 3.5, "reason": "A small increase is reasonable."},
            "Water": {"price": 1.5, "reason": "Water remains affordable."},
        }
    )


def prices(advice):
    return {product: line["price"] for product, line in advice["prices"].items()}


# 1. Valid answer is returned as AI advice
def test_valid_advice_is_returned_as_ai():
    game = logic.start_game()

    advice_result = logic.get_advice(game, lambda prompt: valid_answer())

    assert advice_result["source"] == "ai"
    assert prices(advice_result) == {"Café": 4.5, "Croissant": 3.5, "Water": 1.5}
    assert all(advice_result["prices"][product]["reason"] for product in logic.PRODUCTS)


# 2. Price zero is rejected
def test_zero_price_answer_uses_fallback():
    answer = json.loads(valid_answer())
    answer["Café"]["price"] = 0

    advice_result = logic.get_advice(logic.start_game(), lambda prompt: json.dumps(answer))

    assert advice_result["source"] == "fallback"
    assert prices(advice_result) == FALLBACK_PRICES


# 3. Non-JSON answer is rejected
def test_non_json_answer_uses_fallback():
    advice_result = logic.get_advice(
        logic.start_game(), lambda prompt: "Try charging more for everything."
    )

    assert advice_result["source"] == "fallback"
    assert prices(advice_result) == FALLBACK_PRICES


# 4. Missing product is rejected
def test_missing_product_uses_fallback():
    answer = json.loads(valid_answer())
    del answer["Water"]

    advice_result = logic.get_advice(logic.start_game(), lambda prompt: json.dumps(answer))

    assert advice_result["source"] == "fallback"
    assert prices(advice_result) == FALLBACK_PRICES


# 5. An ask error uses fallback advice
def test_ask_error_uses_fallback():
    def ask(prompt):
        raise RuntimeError("service unavailable")

    advice_result = logic.get_advice(logic.start_game(), ask)

    assert advice_result["source"] == "fallback"
    assert prices(advice_result) == FALLBACK_PRICES


# 6. Empty API key is rejected before sending anything
def test_empty_api_key_is_rejected_without_sending(monkeypatch):
    def fail_if_called(*args, **kwargs):
        pytest.fail("urllib.request.urlopen must not be called for an empty key")

    monkeypatch.setattr("urllib.request.urlopen", fail_if_called)

    with pytest.raises(ValueError):
        advisor.ask_openrouter("hello", "")


# 7. Fallback uses twice the reference prices
def test_fallback_has_the_reference_prices_doubled():
    advice_result = logic.fallback_advice()

    assert advice_result["source"] == "fallback"
    assert prices(advice_result) == FALLBACK_PRICES
    assert all(advice_result["prices"][product]["reason"] for product in logic.PRODUCTS)


# 8. Advice does not change the saved game
def test_get_advice_does_not_change_the_game(tmp_path):
    db_path = tmp_path / "game.db"
    game = logic.load_game(db_path, ANA)
    before = copy.deepcopy(game)

    logic.get_advice(game, lambda prompt: valid_answer())

    after = logic.load_game(db_path, ANA)
    assert after == before


# 9. A valid answer in code fences is accepted
def test_answer_in_code_fences_is_accepted():
    fenced_answer = "```json\n" + valid_answer() + "\n```"

    advice_result = logic.get_advice(logic.start_game(), lambda prompt: fenced_answer)

    assert advice_result["source"] == "ai"
    assert prices(advice_result) == {"Café": 4.5, "Croissant": 3.5, "Water": 1.5}
