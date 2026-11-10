import pytest

import db

FAKE_SETTINGS = {
    "TURSO_DATABASE_URL": "libsql://fake-db.turso.io",
    "TURSO_AUTH_TOKEN": "fake-token",
}


def test_choose_local_file_without_settings_and_turso_with_both(tmp_path):
    # Pure choice: nothing connects, to Turso or to a file.
    assert db.choose_database(db.DEFAULT_PATH, {}) == {
        "kind": "local", "path": db.DEFAULT_PATH,
    }
    assert db.choose_database(db.DEFAULT_PATH, FAKE_SETTINGS) == {
        "kind": "turso", "url": "libsql://fake-db.turso.io", "token": "fake-token",
    }

    # Empty values count as missing: both empty is the same as no settings.
    both_empty = {"TURSO_DATABASE_URL": "", "TURSO_AUTH_TOKEN": ""}
    assert db.choose_database(db.DEFAULT_PATH, both_empty) == {
        "kind": "local", "path": db.DEFAULT_PATH,
    }

    # Only one setting present (or the other one empty): database unavailable.
    only_url = {"TURSO_DATABASE_URL": "libsql://fake-db.turso.io"}
    only_token = {"TURSO_AUTH_TOKEN": "fake-token"}
    empty_token = {"TURSO_DATABASE_URL": "libsql://fake-db.turso.io", "TURSO_AUTH_TOKEN": ""}
    for settings in [only_url, only_token, empty_token]:
        with pytest.raises(db.DatabaseUnavailable) as error:
            db.choose_database(db.DEFAULT_PATH, settings)
        assert "database unavailable" in str(error.value).lower()

    # A test's own database file stays local, even with both settings.
    test_path = tmp_path / "game.db"
    assert db.choose_database(test_path, FAKE_SETTINGS) == {
        "kind": "local", "path": test_path,
    }


class FakeConnection:
    def execute(self, sql, *args):
        raise Exception("fake: Turso did not answer")


class FakeLibsqlConnectFails:
    def connect(self, *args, **kwargs):
        raise Exception("fake: cannot reach Turso")


class FakeLibsqlQueryFails:
    def connect(self, *args, **kwargs):
        return FakeConnection()


def test_failed_turso_connection_raises_database_unavailable(tmp_path, monkeypatch):
    # Work in an empty folder, so the real data/game.db is never touched.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(db, "read_settings", lambda: FAKE_SETTINGS)

    for fake_libsql in [FakeLibsqlConnectFails(), FakeLibsqlQueryFails()]:
        monkeypatch.setattr(db, "libsql", fake_libsql)
        with pytest.raises(db.DatabaseUnavailable) as error:
            db.connect(db.DEFAULT_PATH)
        assert "database unavailable" in str(error.value).lower()
        assert "libsql://fake-db.turso.io" not in str(error.value)
        assert "fake-token" not in str(error.value)


class FakeStreamlit:
    secrets = {
        "TURSO_DATABASE_URL": "libsql://secrets-db.turso.io",
        "TURSO_AUTH_TOKEN": "secrets-token",
    }


def test_environment_variables_win_over_streamlit_secrets(monkeypatch):
    # Fake st.secrets, so the real .streamlit/secrets.toml is never read.
    monkeypatch.setattr(db, "st", FakeStreamlit())

    monkeypatch.setenv("TURSO_DATABASE_URL", "libsql://env-db.turso.io")
    monkeypatch.setenv("TURSO_AUTH_TOKEN", "env-token")
    assert db.read_settings() == {
        "TURSO_DATABASE_URL": "libsql://env-db.turso.io",
        "TURSO_AUTH_TOKEN": "env-token",
    }

    # Without environment variables, st.secrets is used.
    monkeypatch.delenv("TURSO_DATABASE_URL")
    monkeypatch.delenv("TURSO_AUTH_TOKEN")
    assert db.read_settings() == {
        "TURSO_DATABASE_URL": "libsql://secrets-db.turso.io",
        "TURSO_AUTH_TOKEN": "secrets-token",
    }
