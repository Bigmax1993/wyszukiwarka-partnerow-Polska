# -*- coding: utf-8 -*-
"""
Target kampanii Hurt Matbud: polska firma wykonawcza działająca w Niemczech.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from commercial_contact_filter import (
    is_non_commercial_contact,
    is_non_commercial_email,
    is_non_commercial_name,
    is_non_commercial_website,
)

_POLISH_LEGAL_FORM = re.compile(
    r"(?:sp(?:ółka|olka)?\s*z\s*o\.?\s*o\.?|s(?:półka|polka)?\s*z\s*o\.?\s*o\.?"
    r"|s\.?\s*a\.?\b|sp\.\s*j\.?|sp\.\s*k\.?|s\.\s*c\.?|p\.?\s*h\.?\s*u\.?"
    r"|przedsiębiorstwo|przedsiebiorstwo)",
    re.IGNORECASE,
)

_DE_LEGAL_ONLY = re.compile(
    r"(?:GmbH|UG(?:\s*\(haftungsbeschränkt\))?|AG|e\.?\s*K\.?|KG|OHG|PartG|mbH)\b",
    re.IGNORECASE,
)

_PL_ADDRESS_MARKERS = (
    "polska",
    "poland",
    "województwo",
    "wojewodztwo",
    "ul.",
    "ulica",
    " nip ",
    "regon",
    "krs",
    "warszawa",
    "wrocław",
    "wroclaw",
    "poznań",
    "poznan",
    "kraków",
    "krakow",
    "gdańsk",
    "gdansk",
    "katowice",
    "łódź",
    "lodz",
    "szczecin",
    "lublin",
    "bydgoszcz",
    "zielona góra",
    "gorzów",
    "opole",
    "rzeszów",
)

_DE_WORK_MARKERS = (
    "niemcy",
    "deutschland",
    "germany",
    "bundesland",
    "realizacje niemcy",
    "realizacje w niemczech",
    "referenz",
    "referencje niemcy",
    "ladenbau",
    "innenausbau",
    "filialbau",
    "nrw",
    "bayern",
    "sachsen",
    "berlin",
    "hamburg",
    "aldi",
    "lidl",
    "kaufland",
    "edeka",
    "rewe",
    "rossmann",
    "netto",
    "penny",
    "dm-drogerie",
    "dm drogerie",
)

_TRADE_MARKERS = (
    "wyposażenie sklep",
    "wyposazenie sklep",
    "meble sklep",
    "montaż sklep",
    "montaz sklep",
    "posadzk",
    "żywice",
    "zywice",
    "płytk",
    "plytk",
    "wykładzin",
    "wykladzin",
    "ladenbau",
    "shopfitting",
    "innenausbau",
    "fit-out",
    "fit out",
    "podwykonaw",
    "budowl",
    "wykończeni",
    "wykonczeni",
    "klimatyzac",
    "chłodnict",
    "chlodnict",
    "elektry",
    "wentylac",
    "regał",
    "regal sklep",
)

_REJECT_MARKERS = (
    "agencja pracy",
    "praca tymczasowa",
    "zeitarbeit",
    "oferty pracy",
    "deweloper mieszkaniowy",
    "osiedle mieszkaniowe",
    "biedronka",
    "żabka",
    "zabka",
    "olx.pl",
    "aleo",
    "panorama firm",
    "pkt.pl",
    "katalog firm",
    "gov.pl",
    "bip.",
    "urząd",
    "urzad gminy",
    "starostwo",
)


def _normalize_host(url_or_email: str) -> str:
    text = (url_or_email or "").strip().lower()
    if "@" in text and "://" not in text:
        text = text.split("@", 1)[1]
    if "://" in text:
        try:
            text = (urlparse(text).netloc or "").lower()
        except Exception:
            return ""
    if text.startswith("www."):
        text = text[4:]
    return text.split("/", 1)[0].strip()


def has_polish_legal_form(name: str) -> bool:
    return bool(_POLISH_LEGAL_FORM.search(name or ""))


def has_polish_domain(url: str = "", email: str = "") -> bool:
    for raw in (url, email):
        host = _normalize_host(raw)
        if host.endswith(".pl"):
            return True
    return False


def has_polish_address_signal(text: str) -> bool:
    low = f" {text or ''} ".lower()
    return any(m in low for m in _PL_ADDRESS_MARKERS)


def has_germany_work_evidence(text: str) -> bool:
    low = (text or "").lower()
    return any(m in low for m in _DE_WORK_MARKERS)


def has_target_trade(text: str) -> bool:
    low = (text or "").lower()
    return any(m in low for m in _TRADE_MARKERS)


def _blob(*, name: str = "", url: str = "", email: str = "", text: str = "") -> str:
    return " ".join(x for x in (name, url, email, text) if x)


def is_rejected_non_target(name: str = "", url: str = "", email: str = "", text: str = "") -> bool:
    blob = _blob(name=name, url=url, email=email, text=text).lower()
    if any(m in blob for m in _REJECT_MARKERS):
        return True
    if is_non_commercial_contact(email=email, url=url, name=name):
        return True
    if email and is_non_commercial_email(email):
        return True
    if url and is_non_commercial_website(url):
        return True
    if name and is_non_commercial_name(name):
        return True
    return False


def is_german_only_entity(name: str = "", url: str = "", email: str = "", text: str = "") -> bool:
    """Czysto niemiecki podmiot bez polskiego tropu."""
    if has_polish_legal_form(name) or has_polish_domain(url, email) or has_polish_address_signal(
        _blob(name=name, url=url, email=email, text=text)
    ):
        return False
    if _DE_LEGAL_ONLY.search(name or "") and not has_polish_legal_form(name):
        host = _normalize_host(url) or _normalize_host(email)
        if host.endswith(".de") or host.endswith(".eu"):
            return True
    return False


def is_polish_company_operating_in_germany(
    *,
    name: str = "",
    url: str = "",
    email: str = "",
    text: str = "",
    require_de_evidence: bool = True,
) -> bool:
    """
    True = polska firma (forma / .pl / adres PL) z branży wykonawczej
    i (domyślnie) śladem pracy w DE.
    """
    if is_rejected_non_target(name=name, url=url, email=email, text=text):
        return False
    blob = _blob(name=name, url=url, email=email, text=text)
    polish = (
        has_polish_legal_form(name)
        or has_polish_domain(url, email)
        or has_polish_address_signal(blob)
    )
    if not polish:
        return False
    if is_german_only_entity(name=name, url=url, email=email, text=text):
        return False
    if require_de_evidence and not has_germany_work_evidence(blob):
        return False
    if not has_target_trade(blob) and not has_germany_work_evidence(blob):
        return False
    return True


def needs_review_missing_de_evidence(
    *,
    name: str = "",
    url: str = "",
    email: str = "",
    text: str = "",
) -> bool:
    """Polska firma z branży, ale bez twardego śladu DE — Excel Szczegoly, nie mail."""
    if is_rejected_non_target(name=name, url=url, email=email, text=text):
        return False
    blob = _blob(name=name, url=url, email=email, text=text)
    polish = (
        has_polish_legal_form(name)
        or has_polish_domain(url, email)
        or has_polish_address_signal(blob)
    )
    if not polish:
        return False
    return not has_germany_work_evidence(blob)
