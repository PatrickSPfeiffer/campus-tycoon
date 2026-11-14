import copy
import smtplib

import pytest

import db
import logic
import mailer


PLAYER = "ana@example.com"
TEAM_ADDRESS = "team@example.com"
PASSWORD = "fake-password-123"
FINAL = {"final_cash": 112.5, "stock_at_cost": 45.0, "gain": 57.5}


class FakeSMTP:
    def __init__(self, uses, failure=None):
        self.uses = uses
        self.failure = failure
        self.use = None

    def __call__(self, host, port, timeout):
        self.use = {"constructor": (host, port, timeout), "context_manager": False, "logins": [], "messages": []}
        self.uses.append(self.use)
        if self.failure and self.failure[0] == "constructor":
            raise self.failure[1]
        return self

    def __enter__(self):
        self.use["context_manager"] = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def login(self, address, password):
        self.use["logins"].append((address, password))
        if self.failure and self.failure[0] == "login":
            raise self.failure[1]

    def send_message(self, message):
        self.use["messages"].append(message)
        if self.failure and self.failure[0] == "send_message":
            raise self.failure[1]


def factory_for(uses, failure=None):
    fake = FakeSMTP(uses, failure)

    def factory(host, port, timeout):
        return fake(host, port, timeout)

    return factory


@pytest.fixture(autouse=True)
def isolate_email(monkeypatch):
    monkeypatch.delenv("EMAIL_ADDRESS", raising=False)
    monkeypatch.delenv("EMAIL_APP_PASSWORD", raising=False)

    class FakeStreamlit:
        secrets = {}

    monkeypatch.setattr(mailer, "st", FakeStreamlit())

    def block_network(*args, **kwargs):
        raise OSError("network blocked in tests")

    monkeypatch.setattr(smtplib.socket, "create_connection", block_network)


def set_email_environment(monkeypatch):
    monkeypatch.setenv("EMAIL_ADDRESS", TEAM_ADDRESS)
    monkeypatch.setenv("EMAIL_APP_PASSWORD", PASSWORD)


def test_message_subject_and_values():
    message = logic.result_email_message(PLAYER, FINAL)
    assert message["subject"] == "Your Campus Tycoon result"
    assert "€112.50" in message["body"]
    assert "€45.00" in message["body"]
    assert "€57.50" in message["body"]


def test_message_values_are_formatted_with_two_decimals():
    final = {"final_cash": 3, "stock_at_cost": 0, "gain": 7.5}
    body = logic.result_email_message(PLAYER, final)["body"]
    assert "€3.00" in body
    assert "€0.00" in body
    assert "€7.50" in body


@pytest.mark.parametrize("player", [None, "", "   ", 123])
def test_message_rejects_invalid_player(player):
    with pytest.raises(ValueError):
        logic.result_email_message(player, FINAL)


def test_send_sends_one_message_to_the_player(monkeypatch):
    set_email_environment(monkeypatch)
    uses = []
    result = mailer.send_result_email(PLAYER, FINAL, factory_for(uses))
    assert result == "sent"
    assert len(uses) == 1
    use = uses[0]
    assert len(use["messages"]) == 1
    message = use["messages"][0]
    assert message["To"] == PLAYER
    assert message["From"] == TEAM_ADDRESS
    assert message["Subject"] == "Your Campus Tycoon result"
    assert use["logins"] == [(TEAM_ADDRESS, PASSWORD)]
    assert use["constructor"] == ("smtp.gmail.com", 465, 10)
    assert use["context_manager"] is True


def test_send_has_no_cc_or_bcc(monkeypatch):
    set_email_environment(monkeypatch)
    uses = []
    mailer.send_result_email(PLAYER, FINAL, factory_for(uses))
    message = uses[0]["messages"][0]
    assert message["Cc"] is None
    assert message["Bcc"] is None


@pytest.mark.parametrize(
    "address,password",
    [
        (None, None),
        (TEAM_ADDRESS, None),
        (None, PASSWORD),
        ("", PASSWORD),
        (TEAM_ADDRESS, ""),
    ],
    ids=["both-missing", "password-missing", "address-missing", "address-empty", "password-empty"],
)
def test_send_is_skipped_when_a_secret_is_missing_or_empty(monkeypatch, address, password):
    if address is not None:
        monkeypatch.setenv("EMAIL_ADDRESS", address)
    if password is not None:
        monkeypatch.setenv("EMAIL_APP_PASSWORD", password)
    uses = []
    assert mailer.send_result_email(PLAYER, FINAL, factory_for(uses)) == "skipped"
    assert uses == []


def test_send_reads_secrets_from_streamlit_secrets(monkeypatch):
    monkeypatch.setattr(
        mailer,
        "st",
        type("FakeStreamlit", (), {"secrets": {"EMAIL_ADDRESS": TEAM_ADDRESS, "EMAIL_APP_PASSWORD": PASSWORD}})(),
    )
    uses = []
    assert mailer.send_result_email(PLAYER, FINAL, factory_for(uses)) == "sent"
    assert uses[0]["logins"] == [(TEAM_ADDRESS, PASSWORD)]


def test_environment_has_priority_over_streamlit_secrets(monkeypatch):
    set_email_environment(monkeypatch)
    monkeypatch.setattr(
        mailer,
        "st",
        type(
            "FakeStreamlit",
            (),
            {"secrets": {"EMAIL_ADDRESS": "other@example.com", "EMAIL_APP_PASSWORD": "other-password"}},
        )(),
    )
    uses = []
    mailer.send_result_email(PLAYER, FINAL, factory_for(uses))
    assert uses[0]["logins"] == [(TEAM_ADDRESS, PASSWORD)]


def test_send_is_skipped_when_secrets_file_is_missing(monkeypatch):
    class MissingSecrets:
        def get(self, name, default=""):
            raise FileNotFoundError(name)

    monkeypatch.setattr(mailer, "st", type("FakeStreamlit", (), {"secrets": MissingSecrets()})())
    uses = []
    assert mailer.send_result_email(PLAYER, FINAL, factory_for(uses)) == "skipped"
    assert uses == []


@pytest.mark.parametrize(
    "failure",
    [
        ("constructor", OSError("boom")),
        ("constructor", TimeoutError("boom")),
        ("login", smtplib.SMTPAuthenticationError(535, b"bad credentials")),
        ("send_message", smtplib.SMTPException("bad")),
    ],
    ids=["constructor-oserror", "constructor-timeout", "login-authentication", "send-message"],
)
def test_send_fails_without_raising(monkeypatch, failure):
    set_email_environment(monkeypatch)
    uses = []
    assert mailer.send_result_email(PLAYER, FINAL, factory_for(uses, failure)) == "failed"


def test_password_and_address_never_leak(monkeypatch, capsys, caplog):
    set_email_environment(monkeypatch)
    successful_uses = []
    success = mailer.send_result_email(PLAYER, FINAL, factory_for(successful_uses))

    failed_uses = []
    failure = ("send_message", smtplib.SMTPException(f"delivery failed for {PASSWORD}"))
    failed = mailer.send_result_email(PLAYER, FINAL, factory_for(failed_uses, failure))

    captured = capsys.readouterr()
    for text in (success, failed, captured.out, captured.err, caplog.text):
        assert PASSWORD not in text
        assert TEAM_ADDRESS not in text
    for use in successful_uses + failed_uses:
        for message in use["messages"]:
            assert PASSWORD not in str(message)


@pytest.mark.parametrize("player", ["", None])
def test_invalid_player_gives_failed_and_does_not_connect(player):
    uses = []
    assert mailer.send_result_email(player, FINAL, factory_for(uses)) == "failed"
    assert uses == []


def test_default_factory_with_blocked_network_gives_failed(monkeypatch):
    set_email_environment(monkeypatch)
    assert mailer.send_result_email(PLAYER, FINAL) == "failed"


def test_final_result_is_unchanged_by_the_email(tmp_path, monkeypatch):
    db_path = tmp_path / "game.db"
    logic.new_run(db_path, PLAYER)
    for _ in range(logic.RUN_DAYS):
        logic.trade_day(db_path, PLAYER)

    game = logic.load_game(db_path, PLAYER)
    assert logic.is_run_complete(game)
    final = logic.final_result(game)
    original_game = copy.deepcopy(game)

    outcomes = []
    successful_uses = []
    outcomes.append((lambda: set_email_environment(monkeypatch), factory_for(successful_uses), "sent"))

    def clear_email_environment():
        monkeypatch.delenv("EMAIL_ADDRESS", raising=False)
        monkeypatch.delenv("EMAIL_APP_PASSWORD", raising=False)

    outcomes.append((clear_email_environment, factory_for([]), "skipped"))

    failed_uses = []
    outcomes.append(
        (
            lambda: set_email_environment(monkeypatch),
            factory_for(failed_uses, ("send_message", smtplib.SMTPException("send failed"))),
            "failed",
        )
    )

    for prepare_environment, factory, expected_status in outcomes:
        prepare_environment()
        assert mailer.send_result_email(PLAYER, final, factory) == expected_status
        loaded_game = logic.load_game(db_path, PLAYER)
        assert logic.final_result(loaded_game) == final
        assert loaded_game == original_game
