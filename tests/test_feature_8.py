import pytest

import logic

# Fake users shaped like st.user: a mapping with "is_logged_in" and the claims
# Google returns. Nothing here calls Google or Streamlit.
ANA = "ana@example.com"


def test_check_1_signed_in_user_becomes_the_player_by_email():
    # No "email_verified" in the user: accepted.
    user = {"is_logged_in": True, "email": ANA, "name": "Ana"}
    assert logic.player_from_user(user) == ANA


def test_check_1_email_is_trimmed_and_lowercased():
    user = {"is_logged_in": True, "email": "  Ana@Example.com "}
    assert logic.player_from_user(user) == "ana@example.com"


def test_check_1_user_whose_email_is_not_verified_is_rejected():
    user = {"is_logged_in": True, "email": ANA, "email_verified": False}
    with pytest.raises(ValueError):
        logic.player_from_user(user)


def test_check_1_user_who_is_not_signed_in_is_rejected():
    for user in [
        {"is_logged_in": False},
        {},
        # Even with an email, a user who is not signed in is not a player.
        {"is_logged_in": False, "email": ANA},
    ]:
        with pytest.raises(ValueError):
            logic.player_from_user(user)


def test_check_1_signed_in_user_without_email_is_rejected():
    for user in [
        {"is_logged_in": True},
        {"is_logged_in": True, "email": None},
        {"is_logged_in": True, "email": ""},
        {"is_logged_in": True, "email": "   "},
    ]:
        with pytest.raises(ValueError):
            logic.player_from_user(user)
