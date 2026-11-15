from copy import deepcopy

import pytest

import logic


ANA = "ana@example.com"
BRUNO = "bruno@example.com"
A = "a@example.com"
B = "b@example.com"
C = "c@example.com"


def test_one_player_matches_practice_demand():
    for price, stock, sold in [(4.00, 20, 10), (8.00, 20, 5), (8.01, 20, 0), (4.00, 3, 3)]:
        stands = [{"player": A, "seat": 1, "price": price, "stock": stock}]

        assert logic.market_sales("Café", stands, day=1) == {A: sold}


def test_team_brief_shared_market_example():
    stands = [
        {"player": ANA, "seat": 1, "price": 3.50, "stock": 15},
        {"player": BRUNO, "seat": 2, "price": 6.00, "stock": 10},
    ]

    assert logic.market_sales("Café", stands, day=1) == {ANA: 15, BRUNO: 5}


def test_tied_stands_rotate_the_starting_seat():
    stands = [
        {"player": A, "seat": 1, "price": 4.00, "stock": 20},
        {"player": B, "seat": 2, "price": 4.00, "stock": 20},
        {"player": C, "seat": 3, "price": 9.00, "stock": 20},
    ]

    assert logic.market_sales("Café", stands, day=1) == {A: 16, B: 14, C: 0}
    assert logic.market_sales("Café", stands, day=2) == {A: 14, B: 16, C: 0}
    assert logic.market_sales("Café", stands, day=3) == {A: 16, B: 14, C: 0}


def test_tied_stand_that_runs_out_passes_customers_to_other_stand():
    stands = [
        {"player": A, "seat": 1, "price": 4.00, "stock": 3},
        {"player": B, "seat": 2, "price": 4.00, "stock": 20},
    ]

    assert logic.market_sales("Café", stands, day=1) == {A: 3, B: 17}


def test_empty_cheapest_stand_passes_customers_to_next_cheapest_stand():
    stands = [
        {"player": A, "seat": 1, "price": 3.50, "stock": 0},
        {"player": B, "seat": 2, "price": 4.00, "stock": 20},
    ]

    assert logic.market_sales("Café", stands, day=1) == {A: 0, B: 20}


def test_unknown_product_is_rejected_and_stands_are_unchanged():
    stands = [
        {"player": A, "seat": 1, "price": 6.00, "stock": 10},
        {"player": B, "seat": 2, "price": 3.50, "stock": 15},
    ]
    original_stands = deepcopy(stands)

    logic.market_sales("Café", stands, day=1)
    assert stands == original_stands

    with pytest.raises(ValueError):
        logic.market_sales("Unknown", stands, day=1)

    assert stands == original_stands
