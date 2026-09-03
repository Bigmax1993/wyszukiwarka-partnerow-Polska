# -*- coding: utf-8 -*-
"""Testy jednostkowe: de_gu_keywords, rotacja land├│w, mail_transport."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


class TestDeGuKeywords:
    def test_sachsen_discovery_terms(self):
        from de_gu_keywords import build_discovery_terms

        terms = build_discovery_terms(["Dolnoslaskie"], max_terms=96)
        assert len(terms) >= 10
        assert any("Niemcy" in t or "Deutschland" in t or "Wrocław" in t for t in terms)

    def test_all_bundeslaender_count(self):
        from de_gu_keywords import BUNDESLAND_CONFIG

        assert len(BUNDESLAND_CONFIG) == 16


class TestBundeslandRotation:
    def test_peek_and_commit(self):
        from gu_bundesland_rotation import (
            BUNDESLAND_ROTATION_ORDER,
            commit_rotation_after_run,
            load_rotation_state,
            peek_next_bundesland,
            rotation_state_path,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = rotation_state_path(Path(tmp))
            state = load_rotation_state(path)
            land = peek_next_bundesland(state)
            assert land in BUNDESLAND_ROTATION_ORDER
            nxt = commit_rotation_after_run(path, state, land)
            assert nxt in BUNDESLAND_ROTATION_ORDER


class TestMailTransportGmail:
    def test_gmail_host_detection(self, monkeypatch):
        from mail_transport import get_smtp_host

        monkeypatch.setenv("MAIL_USER", "test@gmail.com")
        monkeypatch.delenv("SMTP_HOST", raising=False)
        assert get_smtp_host() == "smtp.gmail.com"

    def test_no_homepl_default_without_gmail(self, monkeypatch):
        from mail_transport import get_smtp_host

        monkeypatch.setenv("MAIL_USER", "kontakt@firma.de")
        monkeypatch.delenv("SMTP_HOST", raising=False)
        host = get_smtp_host()
        assert "home.pl" not in host.lower()
