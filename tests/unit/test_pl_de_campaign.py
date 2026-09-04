# -*- coding: utf-8 -*-
"""Kampania PL→DE: województwa, filtr firm, maile Hurt Matbud, Excel."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


class TestWojewodztwa:
    def test_sixteen_voivodeships(self):
        from pl_wojewodztwa import WOJEWODZTWO_CONFIG

        assert len(WOJEWODZTWO_CONFIG) == 16

    def test_discovery_terms_polish(self):
        from de_gu_keywords import build_discovery_terms

        terms = build_discovery_terms(["Dolnoslaskie"], max_terms=40)
        assert len(terms) >= 8
        blob = " ".join(terms).lower()
        assert "wrocław" in blob or "wroclaw" in blob or "niemcy" in blob
        assert "generalunternehmer filialbau" not in blob
        assert "podwykonawca" in blob or "budowlana" in blob or "wykończenia" in blob

    def test_rotation_order(self):
        from gu_bundesland_rotation import (
            BUNDESLAND_ROTATION_ORDER,
            commit_rotation_after_run,
            load_rotation_state,
            peek_next_bundesland,
            rotation_state_path,
        )

        assert BUNDESLAND_ROTATION_ORDER[0] == "Dolnoslaskie"
        with tempfile.TemporaryDirectory() as tmp:
            path = rotation_state_path(Path(tmp))
            state = load_rotation_state(path)
            land = peek_next_bundesland(state)
            assert land == "Dolnoslaskie"
            nxt = commit_rotation_after_run(path, state, land)
            assert nxt == "Lubuskie"


class TestPolishDeFilter:
    def test_accepts_polish_shopfitter_in_de(self):
        from pl_de_company_filter import is_polish_company_operating_in_germany

        assert is_polish_company_operating_in_germany(
            name="Ergo Store sp. z o.o.",
            url="https://ergostore.pl",
            email="biuro@ergostore.pl",
            text="Meble sklepowe montaż Lidl Niemcy referencje Deutschland",
        )

    def test_accepts_polish_hvac_subcontractor(self):
        from pl_de_company_filter import (
            is_pl_de_serper_discovery_candidate,
            page_mentions_pl_builder_projects,
        )

        assert is_pl_de_serper_discovery_candidate(
            name="Klimat Tech sp. z o.o.",
            url="https://klimat-tech.pl",
            text="Klimatyzacja obiekty handlowe Niemcy",
            search_term="instalacje HVAC sklepy Niemcy Wrocław",
        )
        ok, _, reason = page_mentions_pl_builder_projects(
            "Klimatyzacja i wentylacja sklepy Lidl Niemcy referencje"
        )
        assert ok
        assert "pl_" in reason

    def test_serper_rejects_portal_and_non_trade_even_with_bau_query(self):
        from pl_de_company_filter import is_pl_de_serper_discovery_candidate

        assert not is_pl_de_serper_discovery_candidate(
            name="Krs Pobierz",
            url="https://krs-pobierz.pl",
            text="pobierz odpis KRS firmy",
            search_term="podwykonawca budowlany Niemcy",
        )
        assert not is_pl_de_serper_discovery_candidate(
            name="Przeprowadzki Wrocław",
            url="https://przeprowadzki.pl",
            text="przeprowadzki międzynarodowe",
            search_term="podwykonawca budowlany Wrocław Niemcy",
        )

    def test_rejects_german_gmbh_only(self):
        from pl_de_company_filter import is_polish_company_operating_in_germany

        assert not is_polish_company_operating_in_germany(
            name="Müller Filialbau GmbH",
            url="https://mueller-gu.de",
            email="info@mueller-gu.de",
            text="Generalunternehmer Filialbau NRW Aldi",
        )

    def test_rejects_portal(self):
        from pl_de_company_filter import is_polish_company_operating_in_germany

        assert not is_polish_company_operating_in_germany(
            name="Aleo sp. z o.o.",
            url="https://aleo.com",
            email="kontakt@aleo.pl",
            text="katalog firm Polska Niemcy",
        )

    def test_needs_review_without_de(self):
        from pl_de_company_filter import needs_review_missing_de_evidence

        assert needs_review_missing_de_evidence(
            name="Posadzki-X sp. z o.o.",
            url="https://posadzki-x.pl",
            email="biuro@posadzki-x.pl",
            text="posadzki żywiczne Warszawa",
        )


class TestHurtmatbudEmail:
    def test_greeting_with_first_name(self):
        from hurtmatbud_inquiry_email_pl import greeting_for_contact

        g, used = greeting_for_contact("Jan", "Firma sp. z o.o.")
        assert used
        assert "Panie Janie" in g

    def test_greeting_company_fallback(self):
        from hurtmatbud_inquiry_email_pl import greeting_for_contact

        g, used = greeting_for_contact("", "Firma X sp. z o.o.")
        assert not used
        assert g.startswith("Szanowni Państwo")

    def test_fallback_body_offer(self):
        from hurtmatbud_inquiry_email_pl import (
            build_fallback_email_body,
            build_hurtmatbud_email_prompt,
        )

        subj, _g, body, used = build_fallback_email_body(
            "Ergo Store sp. z o.o.", first_name=""
        )
        assert not used
        assert "Hurt Matbud" in body
        assert "otwarcia" in body.lower() or "lokalizacji" in body.lower()
        assert "generalnych wykonawców" in body.lower() or "generalnych" in body.lower()
        assert "MFG" not in body
        assert "516 513 965" in body or "516513965" in body.replace(" ", "")
        assert "nazywam się" in body.lower() or "piszę z" in body.lower()
        prompt = build_hurtmatbud_email_prompt(
            "Ergo Store sp. z o.o.", first_name="Jan"
        )
        assert "516 513 965" in prompt
        assert "jak człowiek" in prompt.lower() or "ludzki" in prompt.lower()
        assert "Otwarcia" in subj or "otwarcia" in subj.lower()


class TestExcelFourColumns:
    def test_kontakte_columns(self):
        import de_gu_bauunternehmen_scraper as scraper

        row = scraper.row_to_excel_kontakte_columns(
            {
                "nazwa": "Test sp. z o.o.",
                "adres": "Wrocław",
                "telefon": "48 71 111",
                "email_target": "a@b.pl",
                "www": "https://test.pl",
            }
        )
        assert list(row.keys()) == [
            "Nazwa firmy",
            "Adres",
            "Numer Telefonu",
            "E-mail",
        ]
