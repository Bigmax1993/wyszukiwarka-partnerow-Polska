# -*- coding: utf-8 -*-
"""Odczyt kluczy z PowerShell User env (Claude, Gmail, Drive)."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAnthropicFromPowerShell:
    def test_claude_api_key_alias(self, monkeypatch):
        import scraper_env as env

        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("CLAUDE_API_KEY", "sk-test-from-alias")
        env._WINDOWS_ENV_CACHE.clear()
        assert env.get_anthropic_api_key() == "sk-test-from-alias"

    def test_windows_user_anthropic(self, monkeypatch):
        import scraper_env as env

        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        env._WINDOWS_ENV_CACHE.clear()

        def _fake(name: str, scope: str) -> str:
            if name == "ANTHROPIC_API_KEY" and scope == "User":
                return "sk-test-from-user"
            return ""

        monkeypatch.setattr(env, "_read_windows_environment_variable", _fake)
        monkeypatch.setattr(env.os, "name", "nt")
        assert env.get_anthropic_api_key() == "sk-test-from-user"


class TestMailPasswordFromPowerShell:
    def test_gmail_app_password_alias(self, monkeypatch):
        import scraper_env as env

        monkeypatch.delenv("MAIL_PASSWORD", raising=False)
        monkeypatch.setenv("GMAIL_APP_PASSWORD", "test-app-password")
        env._WINDOWS_ENV_CACHE.clear()
        assert env.get_mail_password() == "test-app-password"

    def test_windows_user_gmail_app_password(self, monkeypatch):
        import scraper_env as env

        monkeypatch.delenv("MAIL_PASSWORD", raising=False)
        monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
        env._WINDOWS_ENV_CACHE.clear()

        def _fake(name: str, scope: str) -> str:
            if name == "GMAIL_APP_PASSWORD" and scope == "User":
                return "test-user-app-password"
            return ""

        monkeypatch.setattr(env, "_read_windows_environment_variable", _fake)
        monkeypatch.setattr(env.os, "name", "nt")
        assert env.get_mail_password() == "test-user-app-password"


class TestGdriveFromPowerShell:
    def test_windows_user_gdrive_oauth(self, monkeypatch):
        import scraper_env as env

        monkeypatch.delenv("GDRIVE_OAUTH_CLIENT_ID", raising=False)
        env._WINDOWS_ENV_CACHE.clear()

        def _fake(name: str, scope: str) -> str:
            if name == "GDRIVE_OAUTH_CLIENT_ID" and scope == "User":
                return "test-client-id"
            return ""

        monkeypatch.setattr(env, "_read_windows_environment_variable", _fake)
        monkeypatch.setattr(env.os, "name", "nt")
        assert env.get_env_value("GDRIVE_OAUTH_CLIENT_ID") == "test-client-id"

    def test_google_application_credentials_alias(self, monkeypatch):
        import scraper_env as env

        monkeypatch.delenv("GDRIVE_SERVICE_ACCOUNT_FILE", raising=False)
        monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", r"C:\sa.json")
        env._WINDOWS_ENV_CACHE.clear()
        assert env.get_env_value("GDRIVE_SERVICE_ACCOUNT_FILE") == r"C:\sa.json"
