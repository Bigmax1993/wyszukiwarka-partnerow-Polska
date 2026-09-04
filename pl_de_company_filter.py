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
    "prace w niemczech",
    "budowy w niemczech",
    "montage deutschland",
    "ladenbau",
    "innenausbau",
    "filialbau",
    "gewerbebau",
    "industriebau",
    "hallenbau",
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
    # sklepy / retail fit-out
    "wyposażenie sklep",
    "wyposazenie sklep",
    "meble sklep",
    "montaż sklep",
    "montaz sklep",
    "obiekt handlow",
    "obiekty handlow",
    "centrum handlow",
    "ladenbau",
    "shopfitting",
    "shop fitting",
    "innenausbau",
    "fit-out",
    "fit out",
    "ladeneinrichtung",
    # drogerie / gastro / hotele
    "drogeri",
    "rossmann",
    "restauracj",
    "gastronom",
    "wykończenie restaur",
    "wykonczenie restaur",
    "hotel",
    # hale / przemysł
    "hala przemysł",
    "hala przemysl",
    "hale przemysł",
    "hale magazyn",
    "magazyn",
    "industriebau",
    "gewerbebau",
    "hallenbau",
    "posadzk",
    "żywice",
    "zywice",
    "płytk",
    "plytk",
    "wykładzin",
    "wykladzin",
    "estrich",
    "bodenbelag",
    # ogólne budownictwo / podwykonawstwo
    "podwykonaw",
    "subunternehmer",
    "nachunternehmer",
    "budowl",
    "wykończeni",
    "wykonczeni",
    "remont",
    "zabudow",
    "suche zabudow",
    "trockenbau",
    "płyty gips",
    "plyty gips",
    "elewacj",
    "fassade",
    "klimatyzac",
    "chłodnict",
    "chlodnict",
    "elektry",
    "elektroinstallation",
    "wentylac",
    "lüftung",
    "hvac",
    "sanitar",
    "sanitär",
    "stolarka",
    "witryn",
    "regał",
    "regal sklep",
    "konstrukcj stal",
    "konstrukcje stal",
)

_REJECT_MARKERS = (
    "agencja pracy",
    "praca tymczasowa",
    "zeitarbeit",
    "oferty pracy",
    "portal pracy",
    "portale pracy",
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
    "katalog branżowy",
    "portal branżowy",
    "portale branżowe",
    "branchenportal",
    "fachportal",
    "bauportal",
    "portal budowlany",
    "gov.pl",
    "bip.",
    "urząd",
    "urzad gminy",
    "starostwo",
    "krs-pobierz",
    "pobierz krs",
    "pobierz odpis",
    "odpis krs",
    "monitor sądowy",
    "monitor sadowy",
    "ceidg",
    "przeprowadzk",
    "moving company",
    "umzug",
)

# Domena = katalog / social / praca / urząd — nie strona firmy wykonawczej.
BLOCKED_PUBLIC_PORTAL_HOST_SUFFIXES = (
    # social
    "facebook.com",
    "fb.com",
    "instagram.com",
    "linkedin.com",
    "xing.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "youtube.com",
    "youtu.be",
    "pinterest.com",
    "threads.net",
    "snapchat.com",
    "vk.com",
    # praca
    "pracuj.pl",
    "praca.pl",
    "jobs.pl",
    "indeed.com",
    "indeed.pl",
    "stepstone.de",
    "stepstone.pl",
    "jooble.org",
    "infopraca.pl",
    "gowork.pl",
    "goldenline.pl",
    "nofluffjobs.com",
    "justjoin.it",
    "rocketjobs.pl",
    "monster.de",
    "monster.com",
    "arbeitsagentur.de",
    "olx.pl",
    "olx.de",
    "gratka.pl",
    "gumtree.pl",
    # katalogi / portale publiczne
    "aleo.com",
    "aleo.pl",
    "pkt.pl",
    "panoramafirm.pl",
    "firmy.org.pl",
    "biznesfinder.pl",
    "krs-pobierz.pl",
    "ceidg.gov.pl",
    "gov.pl",
    "wikipedia.org",
    "gelbeseiten.de",
    "11880.com",
    "wlw.de",
    "europages.com",
    "europages.pl",
    "oferteo.pl",
    "fixly.pl",
    "cylex.pl",
    "cylex.de",
    "dasoertliche.de",
    "money.pl",
    "bankier.pl",
    "maps.google.com",
    "maps.google.pl",
    # portale / media branżowe PL+DE
    "muratorplus.pl",
    "murator.pl",
    "rynekinstalacyjny.pl",
    "infobudowa.pl",
    "infobudownictwo.pl",
    "builder.pl",
    "propertydesign.pl",
    "propertynews.pl",
    "urbanity.pl",
    "rynekpierwotny.pl",
    "portalbudowlany.pl",
    "e-budownictwo.pl",
    "ebudownictwo.pl",
    "izolacje.com.pl",
    "oknonet.pl",
    "znanyfachowiec.pl",
    "fachowcy.pl",
    "pzpb.pl",
    "baunetz.de",
    "baulinks.de",
    "bauportal.de",
    "ibau.de",
    "ibau.com",
    "presseportal.de",
    "openpr.de",
    "detail.de",
    "dbz.de",
    "bauindustrie.de",
    "zdb.de",
    "firmenwissen.de",
    "northdata.de",
    "northdata.com",
    "unternehmensregister.de",
    "handelsregister.de",
    "bundesanzeiger.de",
    "kompany.com",
    "architonic.com",
    "hoerbiger.com",
)

# Fragment hosta — katalog/portal branżowy, nie strona wykonawcy.
_BLOCKED_PUBLIC_PORTAL_HOST_MARKERS = (
    "portalbudowl",
    "portal-budowl",
    "bauportal",
    "branchenportal",
    "fachportal",
    "infobudow",
    "branchenbuch",
    "firmenverzeichnis",
    "katalogfirm",
    "katalog-firm",
    "bizneskatalog",
    "firmendatenbank",
    "ausschreibungsportal",
    "vergabemarktplatz",
)


def _host_has_blocked_suffix(host: str) -> bool:
    h = (host or "").strip().lower()
    if h.startswith("www."):
        h = h[4:]
    if not h:
        return False
    for suffix in BLOCKED_PUBLIC_PORTAL_HOST_SUFFIXES:
        if h == suffix or h.endswith("." + suffix):
            return True
    if any(m in h for m in _BLOCKED_PUBLIC_PORTAL_HOST_MARKERS):
        return True
    return False


def is_blocked_public_portal(
    *,
    url: str = "",
    email: str = "",
    name: str = "",
    text: str = "",
) -> bool:
    """True = social, praca, katalog, portal branżowy, urząd — omijać od razu."""
    for raw in (url, email):
        if _host_has_blocked_suffix(_normalize_host(raw)):
            return True
    low_url = (url or "").lower()
    if "google." in low_url and "/maps" in low_url:
        return True
    blob = _blob(name=name, url=url, email=email, text=text).lower()
    if any(m in blob for m in _REJECT_MARKERS):
        return True
    return False


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


_COMMERCIAL_OBJECT_MARKERS = (
    "sklep",
    "markt",
    "filial",
    "supermarkt",
    "discounter",
    "drogeri",
    "rossmann",
    "restauran",
    "gastronom",
    "hotel",
    "halle",
    "magazyn",
    "lager",
    "gewerbe",
    "industri",
    "obiekt handlow",
    "centrum handlow",
    "einkauf",
    "laden",
    "shop",
)


def has_commercial_or_industrial_object_context(text: str) -> bool:
    low = (text or "").lower()
    return any(m in low for m in _COMMERCIAL_OBJECT_MARKERS)


def mentions_pl_builder_activity(text: str) -> bool:
    """
    Polska firma wykonawcza / podwykonawcza wokół budownictwa i fit-out
    (sklepy, drogerie, gastro, hale) — bez wymogu niemieckiego GU/Filialbau.
    """
    low = (text or "").lower()
    if not has_target_trade(low):
        return False
    # branża wystarczy; kontekst obiektu handlowego/przemysłowego wzmacnia, ale nie jest obowiązkowy
    # gdy fraza już zawiera „budowl/podwykonaw/posadzk/…”
    return True


def is_pl_de_serper_discovery_candidate(
    *,
    email: str = "",
    url: str = "",
    name: str = "",
    text: str = "",
    search_term: str = "",
) -> bool:
    """
    Filtr Serper dla kampanii PL→DE: polski trop + branża w snippecie/nazwie firmy
    + ślad Niemiec (snippet LUB fraza Serper).
    Frazy wyszukiwania NIE udają branży firmy.
    """
    if is_rejected_non_target(name=name, url=url, email=email, text=text):
        return False
    company_blob = _blob(name=name, url=url, email=email, text=text)
    term = (search_term or "").strip().lower()
    company_low = company_blob.lower()

    polish = (
        has_polish_legal_form(name)
        or has_polish_domain(url, email)
        or has_polish_address_signal(company_blob)
        or ".pl" in (url or "").lower()
        or "polska" in company_low
        or "poland" in company_low
        or " polen" in f" {company_low} "
    )
    if not polish and is_german_only_entity(name=name, url=url, email=email, text=text):
        return False
    if not polish:
        # bez polskiego tropu w wyniku — odrzuć (nie ratujemy frazą Serper)
        return False

    # Branża musi być w wyniku Serper (tytuł/snippet/URL), nie w frazie zapytania.
    if not (
        has_target_trade(company_low)
        or has_commercial_or_industrial_object_context(company_low)
    ):
        return False

    de_ok = has_germany_work_evidence(company_low) or any(
        m in term for m in ("niemcy", "deutschland", "germany")
    )
    if not de_ok:
        return False
    return True


def page_mentions_pl_builder_projects(text: str) -> tuple[bool, list[str], str]:
    """Weryfikacja www: branża wykonawcza PL (nie GU Filialbau)."""
    low = (text or "").lower()
    if not mentions_pl_builder_activity(low):
        return False, [], "kein_bau_gewerbe_kontext"
    chains = [
        c
        for c in (
            "aldi",
            "rewe",
            "edeka",
            "netto",
            "penny",
            "kaufland",
            "lidl",
            "rossmann",
            "dm",
        )
        if c in low
    ]
    if has_germany_work_evidence(low) or has_commercial_or_industrial_object_context(low):
        return True, chains, "pl_podwykonawca_bau"
    # Polska strona z branżą budowlaną — pending DE może dojść z Serper; tu akceptujemy kontekst branżowy
    return True, chains, "pl_bau_branża"


def _blob(*, name: str = "", url: str = "", email: str = "", text: str = "") -> str:
    return " ".join(x for x in (name, url, email, text) if x)


def is_rejected_non_target(name: str = "", url: str = "", email: str = "", text: str = "") -> bool:
    blob = _blob(name=name, url=url, email=email, text=text).lower()
    if is_blocked_public_portal(url=url, email=email, name=name, text=text):
        return True
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
