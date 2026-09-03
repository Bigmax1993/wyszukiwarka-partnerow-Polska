# -*- coding: utf-8 -*-
"""
Wsp├│lne nazwy zmiennych ┼Ťrodowiskowych (identyczne jak w PowerShell User/Machine).

Ustawienie na sta┼ée (PowerShell):
  [System.Environment]::SetEnvironmentVariable("SERPER_API_KEY", "...", "User")
  [System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "...", "User")
  [System.Environment]::SetEnvironmentVariable("GMAIL_APP_PASSWORD", "...", "User")
  [System.Environment]::SetEnvironmentVariable("GDRIVE_OAUTH_CLIENT_ID", "...", "User")
  [System.Environment]::SetEnvironmentVariable("GDRIVE_OAUTH_CLIENT_SECRET", "...", "User")
  [System.Environment]::SetEnvironmentVariable("GDRIVE_OAUTH_REFRESH_TOKEN", "...", "User")
  [System.Environment]::SetEnvironmentVariable("GDRIVE_SERVICE_ACCOUNT_JSON", "...", "User")
  [System.Environment]::SetEnvironmentVariable("GDRIVE_SERVICE_ACCOUNT_FILE", "...", "User")
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

_DOTENV_LOADED = False


def _load_dotenv_file() -> None:
    """Ładuje .env z katalogu repo i z libs/ (nie commituj .env z kluczami)."""
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    _DOTENV_LOADED = True
    here = Path(__file__).resolve().parent
    for env_path in (here.parent / ".env", here / ".env"):
        if not env_path.is_file():
            continue
        try:
            for raw in env_path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and val and key not in os.environ:
                    os.environ[key] = val
        except OSError:
            pass


_load_dotenv_file()

# --- Nazwy 1:1 z PowerShell ([Environment]::SetEnvironmentVariable(..., "User")) ---
ENV_SERPER_API_KEY = "SERPER_API_KEY"
ENV_MAIL_USER = "MAIL_USER"
ENV_MAIL_PASSWORD = "MAIL_PASSWORD"
ENV_MAIL_SENDER_NAME = "MAIL_SENDER_NAME"
ENV_SMTP_HOST = "SMTP_HOST"
ENV_SMTP_PORT = "SMTP_PORT"
ENV_SMTP_SSL = "SMTP_SSL"
ENV_IMAP_HOST = "IMAP_HOST"
ENV_IMAP_PORT = "IMAP_PORT"
ENV_IMAP_SSL = "IMAP_SSL"
ENV_MAIL_BCC = "MAIL_BCC"
ENV_MAIL_CC = "MAIL_CC"
ENV_MAIL_ARCHIVE_IMAP = "MAIL_ARCHIVE_IMAP"
# Kompatybilno┼Ť─ç wsteczna (Gmail lub stare instalacje)
ENV_GMAIL_USER = "GMAIL_USER"
ENV_GMAIL_APP_PASSWORD = "GMAIL_APP_PASSWORD"
ENV_GMAIL_SENDER_NAME = "GMAIL_SENDER_NAME"
ENV_ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
ENV_CLAUDE_API_KEY = "CLAUDE_API_KEY"
ENV_CLAUDE_MODEL = "CLAUDE_MODEL"
ENV_CLAUDE_MODEL_VERIFY = "CLAUDE_MODEL_VERIFY"
ENV_CLAUDE_MODEL_FAST = "CLAUDE_MODEL_FAST"
ENV_KANBUD_DATA_DIR = "KANBUD_DATA_DIR"
ENV_EXCEL_REPORT_TO = "EXCEL_REPORT_TO"
DEFAULT_EXCEL_REPORT_TO = "svinchak1993@gmail.com"
ENV_GDRIVE_OAUTH_CLIENT_ID = "GDRIVE_OAUTH_CLIENT_ID"
ENV_GDRIVE_OAUTH_CLIENT_SECRET = "GDRIVE_OAUTH_CLIENT_SECRET"
ENV_GDRIVE_OAUTH_REFRESH_TOKEN = "GDRIVE_OAUTH_REFRESH_TOKEN"
ENV_GDRIVE_SERVICE_ACCOUNT_JSON = "GDRIVE_SERVICE_ACCOUNT_JSON"
ENV_GDRIVE_SERVICE_ACCOUNT_FILE = "GDRIVE_SERVICE_ACCOUNT_FILE"
ENV_GDRIVE_FOLDER_ID = "GDRIVE_FOLDER_ID"
ENV_GDRIVE_SHARED_DRIVE_ID = "GDRIVE_SHARED_DRIVE_ID"
ENV_GDRIVE_IMPERSONATE_EMAIL = "GDRIVE_IMPERSONATE_EMAIL"
ENV_GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"

# Opcjonalne (tylko niekt├│re skrypty)
ENV_ENABLE_GEO_DISTANCE_PLZ_FILTER = "ENABLE_GEO_DISTANCE_PLZ_FILTER"
ENV_MAX_DISTANCE_KM_FROM_ANCHOR = "MAX_DISTANCE_KM_FROM_ANCHOR"
ENV_SERPER_SHUFFLE_TERMS = "SERPER_SHUFFLE_TERMS"
ENV_EMAIL_MX_CHECK = "EMAIL_MX_CHECK"

REQUIRED_FOR_EMAIL = (ENV_MAIL_USER, ENV_MAIL_PASSWORD)
REQUIRED_FOR_SERPER = (ENV_SERPER_API_KEY,)
REQUIRED_FOR_CLAUDE = (ENV_ANTHROPIC_API_KEY,)

_WINDOWS_ENV_CACHE: dict[str, str] = {}
_ENV_FALLBACKS: dict[str, tuple[str, ...]] = {
    ENV_ANTHROPIC_API_KEY: (ENV_CLAUDE_API_KEY,),
    ENV_CLAUDE_API_KEY: (ENV_ANTHROPIC_API_KEY,),
    ENV_MAIL_USER: (ENV_GMAIL_USER,),
    ENV_MAIL_PASSWORD: (ENV_GMAIL_APP_PASSWORD,),
    ENV_MAIL_SENDER_NAME: (ENV_GMAIL_SENDER_NAME,),
    ENV_GMAIL_USER: (ENV_MAIL_USER,),
    ENV_GMAIL_APP_PASSWORD: (ENV_MAIL_PASSWORD,),
    ENV_GMAIL_SENDER_NAME: (ENV_MAIL_SENDER_NAME,),
    ENV_GDRIVE_SERVICE_ACCOUNT_FILE: (ENV_GOOGLE_APPLICATION_CREDENTIALS,),
    ENV_GOOGLE_APPLICATION_CREDENTIALS: (ENV_GDRIVE_SERVICE_ACCOUNT_FILE,),
}

# Zmienne ładowane z PowerShell User/Machine przy imporcie (Cursor często nie dziedziczy User env).
_POWER_SHELL_HYDRATE_NAMES = (
    ENV_SERPER_API_KEY,
    ENV_ANTHROPIC_API_KEY,
    ENV_CLAUDE_API_KEY,
    ENV_MAIL_USER,
    ENV_MAIL_PASSWORD,
    ENV_MAIL_SENDER_NAME,
    ENV_GMAIL_USER,
    ENV_GMAIL_APP_PASSWORD,
    ENV_GMAIL_SENDER_NAME,
    ENV_SMTP_HOST,
    ENV_SMTP_PORT,
    ENV_SMTP_SSL,
    ENV_IMAP_HOST,
    ENV_IMAP_PORT,
    ENV_IMAP_SSL,
    ENV_EXCEL_REPORT_TO,
    ENV_CLAUDE_MODEL,
    ENV_CLAUDE_MODEL_VERIFY,
    ENV_CLAUDE_MODEL_FAST,
    ENV_GDRIVE_OAUTH_CLIENT_ID,
    ENV_GDRIVE_OAUTH_CLIENT_SECRET,
    ENV_GDRIVE_OAUTH_REFRESH_TOKEN,
    ENV_GDRIVE_SERVICE_ACCOUNT_JSON,
    ENV_GDRIVE_SERVICE_ACCOUNT_FILE,
    ENV_GDRIVE_FOLDER_ID,
    ENV_GDRIVE_SHARED_DRIVE_ID,
    ENV_GDRIVE_IMPERSONATE_EMAIL,
    ENV_GOOGLE_APPLICATION_CREDENTIALS,
)


def _read_windows_environment_variable(name: str, scope: str) -> str:
    """[Environment]::GetEnvironmentVariable(name, User|Machine) — bez logowania wartości."""
    if os.name != "nt" or not name:
        return ""
    cache_key = f"{scope}:{name}"
    if cache_key in _WINDOWS_ENV_CACHE:
        return _WINDOWS_ENV_CACHE[cache_key]
    try:
        cmd = f"[Environment]::GetEnvironmentVariable('{name}','{scope}')"
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", cmd],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        val = (out or "").strip()
        if val:
            _WINDOWS_ENV_CACHE[cache_key] = val
        return val
    except Exception:
        return ""


def _hydrate_from_windows_user_env() -> None:
    """Wstawia zmienne z PowerShell User/Machine do procesu, jeśli sesja ich nie ma."""
    if os.name != "nt":
        return
    for name in _POWER_SHELL_HYDRATE_NAMES:
        if (os.getenv(name) or "").strip():
            continue
        val = _read_windows_environment_variable(name, "User") or _read_windows_environment_variable(
            name, "Machine"
        )
        if val:
            os.environ.setdefault(name, val)
    if not (os.getenv(ENV_ANTHROPIC_API_KEY) or "").strip():
        alias = (os.getenv(ENV_CLAUDE_API_KEY) or "").strip()
        if alias:
            os.environ.setdefault(ENV_ANTHROPIC_API_KEY, alias)
    if not (os.getenv(ENV_MAIL_PASSWORD) or "").strip():
        app_pw = (os.getenv(ENV_GMAIL_APP_PASSWORD) or "").strip()
        if app_pw:
            os.environ.setdefault(ENV_MAIL_PASSWORD, app_pw)
    if not (os.getenv(ENV_MAIL_USER) or "").strip():
        gmail_user = (os.getenv(ENV_GMAIL_USER) or "").strip()
        if gmail_user:
            os.environ.setdefault(ENV_MAIL_USER, gmail_user)
    if not (os.getenv(ENV_GDRIVE_SERVICE_ACCOUNT_FILE) or "").strip():
        gac = (os.getenv(ENV_GOOGLE_APPLICATION_CREDENTIALS) or "").strip()
        if gac:
            os.environ.setdefault(ENV_GDRIVE_SERVICE_ACCOUNT_FILE, gac)


def get_env_value(name: str, default: str = "") -> str:
    """Odczyt: proces → PowerShell User → PowerShell Machine → aliasy (np. CLAUDE_API_KEY)."""
    names = (name,) + _ENV_FALLBACKS.get(name, ())
    for candidate in names:
        val = (os.getenv(candidate) or "").strip()
        if val:
            return val
    if os.name == "nt":
        for candidate in names:
            for scope in ("User", "Machine"):
                val = _read_windows_environment_variable(candidate, scope)
                if val:
                    os.environ.setdefault(candidate, val)
                    if candidate != name:
                        os.environ.setdefault(name, val)
                    return val
    return (default or "").strip()


def get_serper_api_key() -> str:
    return get_env_value(ENV_SERPER_API_KEY)


def get_anthropic_api_key() -> str:
    """Claude/Anthropic: ANTHROPIC_API_KEY albo CLAUDE_API_KEY (proces + PowerShell User)."""
    return get_env_value(ENV_ANTHROPIC_API_KEY) or get_env_value(ENV_CLAUDE_API_KEY)


def get_excel_report_to() -> str:
    return get_env_value(ENV_EXCEL_REPORT_TO) or DEFAULT_EXCEL_REPORT_TO


def get_mail_user() -> str:
    return get_env_value(ENV_MAIL_USER) or get_env_value(ENV_GMAIL_USER)


def get_mail_password() -> str:
    """Hasło SMTP: MAIL_PASSWORD albo GMAIL_APP_PASSWORD (proces + PowerShell User)."""
    return get_env_value(ENV_MAIL_PASSWORD) or get_env_value(ENV_GMAIL_APP_PASSWORD)


def get_mail_sender_name() -> str:
    return get_env_value(ENV_MAIL_SENDER_NAME) or get_env_value(ENV_GMAIL_SENDER_NAME)


def get_gmail_user() -> str:
    return get_mail_user()


def get_gmail_app_password() -> str:
    return get_mail_password()


def get_gmail_sender_name() -> str:
    return get_mail_sender_name()


def check_env_status() -> dict[str, bool]:
    """Kt├│re zmienne s─ů ustawione (bez ujawniania warto┼Ťci)."""
    all_names = (
        ENV_SERPER_API_KEY,
        ENV_MAIL_USER,
        ENV_MAIL_PASSWORD,
        ENV_MAIL_SENDER_NAME,
        ENV_SMTP_HOST,
        ENV_IMAP_HOST,
        ENV_GMAIL_USER,
        ENV_GMAIL_APP_PASSWORD,
        ENV_GMAIL_SENDER_NAME,
        ENV_ANTHROPIC_API_KEY,
        ENV_CLAUDE_API_KEY,
        ENV_CLAUDE_MODEL,
        ENV_CLAUDE_MODEL_VERIFY,
        ENV_CLAUDE_MODEL_FAST,
        ENV_GDRIVE_OAUTH_CLIENT_ID,
        ENV_GDRIVE_OAUTH_CLIENT_SECRET,
        ENV_GDRIVE_OAUTH_REFRESH_TOKEN,
        ENV_GDRIVE_SERVICE_ACCOUNT_JSON,
        ENV_GDRIVE_SERVICE_ACCOUNT_FILE,
        ENV_GDRIVE_FOLDER_ID,
        ENV_GOOGLE_APPLICATION_CREDENTIALS,
    )
    return {n: bool(get_env_value(n)) for n in all_names}


_hydrate_from_windows_user_env()

# UTF-8 / polskie znaki — od razu przy imporcie modułu wspólnego
from polish_text import configure_utf8_environment

configure_utf8_environment()
