# -*- coding: utf-8 -*-
"""
Słowniki kampanii PL→DE (Hurt Matbud).
BUNDESLAND_CONFIG = województwa PL (alias kompatybilności ze scraperem).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from pl_wojewodztwa import (
    CHAIN_SIMPLE_TERM_TEMPLATES,
    RETAIL_CHAINS_ROTATION,
    SERPER_NEGATIVE_TERMS as _PL_SERPER_NEGATIVE,
    SIMPLE_TERM_TEMPLATES,
    TERM_TEMPLATES,
    WOJEWODZTWO_CONFIG,
    display_wojewodztwo,
    normalize_wojewodztwo_key,
)

_here = Path(__file__).resolve().parent
_ost_kw_path = _here / "de_ost_keywords.py"
if not _ost_kw_path.is_file():
    _ost_kw_path = _here.parent / "Niemcy wschodnie sklepy" / "de_ost_keywords.py"
_spec = importlib.util.spec_from_file_location("_de_ost_keywords", _ost_kw_path)
_ost = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_ost)

GU_ROLE_KEYWORDS = _ost.GU_ROLE_KEYWORDS
RETAIL_CHAIN_KEYWORDS = _ost.RETAIL_CHAIN_KEYWORDS
REQUIRED_RETAIL_CHAIN_KEYWORDS = _ost.REQUIRED_RETAIL_CHAIN_KEYWORDS
RETAIL_BUILD_KEYWORDS = _ost.RETAIL_BUILD_KEYWORDS
RETAIL_TRADE_ACTIVITY_KEYWORDS = _ost.RETAIL_TRADE_ACTIVITY_KEYWORDS
RETAIL_HOCHBAU_CORE_KEYWORDS = _ost.RETAIL_HOCHBAU_CORE_KEYWORDS
RETAIL_REFERENCE_KEYWORDS = _ost.RETAIL_REFERENCE_KEYWORDS
RETAIL_URL_PRIORITY_KEYWORDS = _ost.RETAIL_URL_PRIORITY_KEYWORDS
IMPRESSUM_GUESS_PATHS = _ost.IMPRESSUM_GUESS_PATHS
RETAIL_CONTACT_LINK_KEYWORDS = _ost.RETAIL_CONTACT_LINK_KEYWORDS
SERPER_POSITIVE_TERMS = (
    "niemcy",
    "deutschland",
    "ladenbau",
    "posadzki",
    "wyposażenie sklepów",
    "innenausbau",
    "podwykonawca",
)
SERPER_NEGATIVE_TERMS = tuple(
    dict.fromkeys((*_PL_SERPER_NEGATIVE, *(_ost.SERPER_NEGATIVE_TERMS or ())))
)
LARGE_COMPANY_DOMAINS_EXTRA = _ost.LARGE_COMPANY_DOMAINS_EXTRA
LARGE_COMPANY_NAME_MARKERS_EXTRA = _ost.LARGE_COMPANY_NAME_MARKERS_EXTRA
SMALL_COMPANY_PAGE_MARKERS_EXTRA = _ost.SMALL_COMPANY_PAGE_MARKERS_EXTRA
SMALL_COMPANY_DISCOVERY_TERMS_EXTRA = _ost.SMALL_COMPANY_DISCOVERY_TERMS_EXTRA

DE_OST_PLACE_MARKERS: tuple[str, ...] = ()
DE_OST_REGION_KEYWORDS = (
    "polska",
    "poland",
    "niemcy",
    "deutschland",
)
DE_OST_RURAL_HINTS = _ost.DE_OST_RURAL_HINTS

BUNDESLAND_CONFIG: dict[str, dict] = WOJEWODZTWO_CONFIG
ALL_BUNDESLAENDER: tuple[str, ...] = tuple(BUNDESLAND_CONFIG.keys())
ALL_WOJEWODZTWA = ALL_BUNDESLAENDER
DEFAULT_ACTIVE_BUNDESLAENDER: list[str] = list(ALL_BUNDESLAENDER)
CAMPAIGN_ACTIVE_BUNDESLAENDER: list[str] = list(DEFAULT_ACTIVE_BUNDESLAENDER)
BUNDESWEIT_MAX_DISCOVERY_TERMS = 2400


def default_max_discovery_terms_for(active: list[str] | None = None) -> int:
    n = len(resolve_active_bundeslaender(active))
    if n <= 1:
        return 120
    if n <= 3:
        return 360
    return BUNDESWEIT_MAX_DISCOVERY_TERMS


def _normalize_land_key(name: str) -> str:
    return normalize_wojewodztwo_key(name)


def resolve_active_bundeslaender(names: list[str] | None = None) -> list[str]:
    if not names:
        return list(CAMPAIGN_ACTIVE_BUNDESLAENDER)
    out: list[str] = []
    for raw in names:
        for part in str(raw).replace(";", ",").split(","):
            key = _normalize_land_key(part)
            if key in BUNDESLAND_CONFIG and key not in out:
                out.append(key)
    return out or list(DEFAULT_ACTIVE_BUNDESLAENDER)


resolve_active_wojewodztwa = resolve_active_bundeslaender


def _append_unique_term(terms: list[str], seen: set[str], text: str, *, max_terms: int) -> bool:
    t = (text or "").strip()
    if not t or t in seen:
        return False
    seen.add(t)
    terms.append(t)
    return len(terms) >= max_terms


def _rotating_chain(counter: list[int]) -> str:
    chain = RETAIL_CHAINS_ROTATION[counter[0] % len(RETAIL_CHAINS_ROTATION)]
    counter[0] += 1
    return chain


def _format_chain_term(
    tmpl: str,
    *,
    city: str,
    land: str,
    chain: str,
) -> str:
    display = display_wojewodztwo(land)
    try:
        return tmpl.format(
            city=city,
            land=display,
            wojewodztwo=display,
            chain=chain,
            short=BUNDESLAND_CONFIG.get(land, {}).get("short", ""),
        )
    except KeyError:
        return tmpl.format(city=city, chain=chain)


def build_discovery_terms(
    active: list[str] | None = None, *, max_terms: int | None = None
) -> list[str]:
    lands = resolve_active_bundeslaender(active)
    if max_terms is None:
        max_terms = default_max_discovery_terms_for(lands)
    seen: set[str] = set()
    terms: list[str] = []
    chain_counter = [0]
    all_templates = (*CHAIN_SIMPLE_TERM_TEMPLATES, *TERM_TEMPLATES)
    for land in lands:
        cfg = BUNDESLAND_CONFIG[land]
        cities = cfg["cities"]
        for city in cities:
            for tmpl in all_templates:
                chain = _rotating_chain(chain_counter)
                if _append_unique_term(
                    terms,
                    seen,
                    _format_chain_term(tmpl, city=city, land=land, chain=chain),
                    max_terms=max_terms,
                ):
                    return terms
    if len(lands) >= 10:
        nationwide = (
            "wyposażenie sklepów Polska Niemcy {chain}",
            "posadzki sklepowe Niemcy {chain}",
            "podwykonawca budowa sklepów Deutschland {chain}",
            "Ladenbau Firma Polska {chain}",
            "firma budowlana realizacje Niemcy {chain}",
        )
        for tmpl in nationwide:
            chain = _rotating_chain(chain_counter)
            if _append_unique_term(
                terms,
                seen,
                tmpl.format(chain=chain),
                max_terms=max_terms,
            ):
                return terms
    return terms


def build_landkreis_discovery_terms(active: list[str] | None = None) -> list[str]:
    lands = resolve_active_bundeslaender(active)
    seen: set[str] = set()
    terms: list[str] = []
    chain_counter = [0]
    for land in lands:
        display = display_wojewodztwo(land)
        for city in BUNDESLAND_CONFIG[land]["cities"][:6]:
            for tmpl in (
                "wyposażenie sklepów powiat {city} Niemcy",
                "posadzki {city} {display} Niemcy {chain}",
                "podwykonawca {city} montaż sklepów Niemcy",
            ):
                chain = _rotating_chain(chain_counter)
                _append_unique_term(
                    terms,
                    seen,
                    tmpl.format(city=city, display=display, chain=chain),
                    max_terms=10_000,
                )
    return terms


def build_places_discovery_terms(active: list[str] | None = None) -> list[str]:
    lands = resolve_active_bundeslaender(active)
    seen: set[str] = set()
    terms: list[str] = []
    chain_counter = [0]
    for land in lands:
        for city in BUNDESLAND_CONFIG[land]["cities"][:8]:
            for tmpl in (
                "wyposażenie sklepów {city} Niemcy",
                "Ladenbau {city} Polen",
                "posadzki {city} Niemcy",
                "podwykonawca {city} Deutschland",
            ):
                chain = _rotating_chain(chain_counter)
                _append_unique_term(
                    terms, seen, tmpl.format(city=city, chain=chain), max_terms=10_000
                )
    return terms


def build_broad_discovery_terms(active: list[str] | None = None) -> list[str]:
    lands = resolve_active_bundeslaender(active)
    seen: set[str] = set()
    terms: list[str] = []
    chain_counter = [0]
    for land in lands:
        display = display_wojewodztwo(land)
        short = BUNDESLAND_CONFIG[land]["short"]
        for city in BUNDESLAND_CONFIG[land]["cities"]:
            for tmpl in (
                "firma {city} Niemcy wyposażenie sklepów",
                "posadzki {city} Niemcy",
                "budowlana {city} realizacje Deutschland",
                "Innenausbau {city} Polen",
            ):
                chain = _rotating_chain(chain_counter)
                _append_unique_term(
                    terms, seen, tmpl.format(city=city, chain=chain), max_terms=10_000
                )
        for tmpl in (
            "wyposażenie sklepów {land} Niemcy {chain}",
            "posadzki {land} {chain}",
            "podwykonawca {short} Niemcy {chain}",
            "Ladenbau {land} Polska {chain}",
        ):
            chain = _rotating_chain(chain_counter)
            _append_unique_term(
                terms,
                seen,
                tmpl.format(land=display, short=short, chain=chain),
                max_terms=10_000,
            )
    return terms


def build_fallback_terms(active: list[str] | None = None) -> list[str]:
    lands = resolve_active_bundeslaender(active)
    fb: list[str] = []
    chain_counter = [0]
    for land in lands:
        display = display_wojewodztwo(land)
        short = BUNDESLAND_CONFIG[land]["short"]
        for tmpl in (
            "wyposażenie sklepów {land} Niemcy {chain}",
            "posadzki sklepowe {short} Niemcy {chain}",
            "podwykonawca {land} budowa sklepów",
            "firma {land} Ladenbau Deutschland",
        ):
            chain = _rotating_chain(chain_counter)
            fb.append(tmpl.format(land=display, short=short, chain=chain))
    for tmpl in (
        "wyposażenie sklepów Polska Niemcy {chain}",
        "posadzki żywiczne Niemcy {chain}",
        "podwykonawca budowa sklepów Deutschland {chain}",
        "Innenausbau Polen Deutschland {chain}",
    ):
        chain = _rotating_chain(chain_counter)
        fb.append(tmpl.format(chain=chain))
    seen: set[str] = set()
    out: list[str] = []
    for t in fb:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def build_region_suffix(active: list[str] | None = None) -> str:
    lands = resolve_active_bundeslaender(active)
    if len(lands) <= 1:
        return "Polska Niemcy"
    if len(lands) >= 4:
        return "Polska Niemcy"
    shorts = " ".join(BUNDESLAND_CONFIG[l]["short"] for l in lands[:4])
    return f"Polska Niemcy {shorts}"


def configure_campaign_bundeslaender(
    module,
    names: list[str],
    *,
    max_discovery_terms: int | None = None,
) -> list[str]:
    global CAMPAIGN_ACTIVE_BUNDESLAENDER
    active = resolve_active_bundeslaender(names)
    if max_discovery_terms is None:
        max_discovery_terms = default_max_discovery_terms_for(active)
    CAMPAIGN_ACTIVE_BUNDESLAENDER = active
    module.CAMPAIGN_ACTIVE_BUNDESLAENDER = active
    module.SERPER_DISCOVERY_TERMS = build_discovery_terms(
        active, max_terms=max_discovery_terms
    )
    module.SERPER_DISCOVERY_FALLBACK_TERMS = build_fallback_terms(active)
    module.SERPER_DISCOVERY_BROAD_TERMS = build_broad_discovery_terms(active)
    module.SERPER_DISCOVERY_LANDKREIS_TERMS = build_landkreis_discovery_terms(active)
    module.SERPER_DISCOVERY_PLACES_TERMS = build_places_discovery_terms(active)
    module.SERPER_DISCOVERY_REGION_SUFFIX = build_region_suffix(active)
    return active


configure_campaign_wojewodztwa = configure_campaign_bundeslaender

SERPER_DISCOVERY_TERMS = build_discovery_terms()
SERPER_DISCOVERY_FALLBACK_TERMS = build_fallback_terms()
SERPER_DISCOVERY_BROAD_TERMS = build_broad_discovery_terms()
SERPER_DISCOVERY_LANDKREIS_TERMS = build_landkreis_discovery_terms()
SERPER_DISCOVERY_PLACES_TERMS = build_places_discovery_terms()
SERPER_DISCOVERY_REGION_SUFFIX = build_region_suffix()
