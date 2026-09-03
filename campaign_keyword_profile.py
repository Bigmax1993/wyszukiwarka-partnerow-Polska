# -*- coding: utf-8 -*-
"""
Wspólny słownik kampanii GU / Filialbau — używany przez Serper, regex i Claude.
"""
from __future__ import annotations

from de_gu_keywords import (
    RETAIL_CHAIN_KEYWORDS,
    SERPER_NEGATIVE_TERMS,
    SIMPLE_TERM_TEMPLATES,
    TERM_TEMPLATES,
)
from retail_store_builder_filter import (
    FILIALBAU_SPECIALIST_MARKERS,
    NON_GU_ROLE_EXCLUSION_MARKERS,
    REQUIRED_RETAIL_CHAIN_KEYWORDS,
    RETAIL_STORE_BUILD_MARKERS,
    RETAIL_STORE_UMBAU_MARKERS,
    STRICT_GU_MARKERS,
)

# Role odrzucane w werdykcie LLM (primary_role)
REJECT_PRIMARY_ROLES = frozenset(
    {
        "Betreiber",
        "Händler",
        "Medienportal",
        "Architekturbüro",
        "Planungsbüro",
        "Urzad",
        "Portal",
        "AgencjaPracy",
        "SiecHandlowa",
        "DeweloperMieszkaniowy",
        "Sonstiges",
    }
)

SERPER_TEMPLATE_PATTERNS: tuple[str, ...] = tuple(
    dict.fromkeys((*SIMPLE_TERM_TEMPLATES, *TERM_TEMPLATES))
)


def gu_required_keywords_sample(*, max_items: int = 12) -> list[str]:
    return list(STRICT_GU_MARKERS)[:max_items]


def retail_context_keywords_sample(*, max_items: int = 16) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for group in (
        FILIALBAU_SPECIALIST_MARKERS,
        RETAIL_STORE_BUILD_MARKERS,
        RETAIL_STORE_UMBAU_MARKERS,
    ):
        for item in group:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                out.append(item.strip())
            if len(out) >= max_items:
                return out
    return out


def retail_chain_keywords_sample(*, max_items: int = 12) -> list[str]:
    return list(REQUIRED_RETAIL_CHAIN_KEYWORDS)[:max_items]


def small_company_markers_sample(*, max_items: int = 10) -> list[str]:
    return [
        "firma rodzinna",
        "sp. z o.o.",
        "s.a.",
        "zakład",
        "realizacje niemcy",
        "montaż",
        "podwykonawca",
        "średnie przedsiębiorstwo",
        "siedziba polska",
        "brygady niemcy",
    ][:max_items]


def large_company_markers_sample(*, max_items: int = 14) -> list[str]:
    return [
        "koncern",
        "holding",
        "giełda",
        "budimex",
        "strabag",
        "hochtief",
        "skanska",
        "porr",
        "goldbeck",
        "ponad 500 pracowników",
        "global player",
        "sieć handlowa",
        "biedronka",
        "żabka",
    ][:max_items]


def negative_keywords_sample(*, max_items: int = 14) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in (
        *NON_GU_ROLE_EXCLUSION_MARKERS,
        *SERPER_NEGATIVE_TERMS[:20],
        "agencja pracy",
        "olx",
        "urząd",
        "deweloper mieszkaniowy",
    ):
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
        if len(out) >= max_items:
            break
    return out
