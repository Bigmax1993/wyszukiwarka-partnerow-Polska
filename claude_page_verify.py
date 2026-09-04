# -*- coding: utf-8 -*-
"""Claude Sonnet: weryfikacja kontekstu strony www (PL podwykonawcy / legacy GU)."""
from __future__ import annotations

from typing import Callable

from claude_client import claude_generate_text
from page_verify import (
    apply_page_verdict,
    build_page_verify_prompt,
    hard_reject_page_context,
    parse_page_verify_response,
)
from retail_store_builder_filter import is_generalunternehmer
from scraper_env import get_anthropic_api_key


def claude_verify_company_page(
    company_name: str,
    website: str,
    page_text: str,
    logger,
    cache: dict | None,
    *,
    cache_key: str = "",
    serper_blob: str = "",
    require_generalunternehmer: bool = True,
    require_small_firm: bool = True,
    on_step: Callable[[str], None] | None = None,
) -> dict | None:
    """Czyta stronę (tekst) i zwraca werdykt JSON; None przy braku API lub błędzie."""
    api_key = get_anthropic_api_key()
    if not api_key:
        return None

    verify_cache = (cache or {}).setdefault("claude_page_verify", {})
    if not verify_cache and cache_key:
        legacy = (cache or {}).get("gemini_page_verify") or {}
        if cache_key in legacy:
            verify_cache[cache_key] = dict(legacy[cache_key])
    if cache_key and cache_key in verify_cache:
        return dict(verify_cache[cache_key])

    hard, hard_reason = hard_reject_page_context(
        url=website,
        name=company_name,
        page_text=page_text,
        require_generalunternehmer=require_generalunternehmer,
    )
    if hard:
        out = {
            "verified": False,
            "verification_reason": hard_reason,
            "retail_chains": [],
            "claude": {},
        }
        if cache_key:
            verify_cache[cache_key] = out
        return out

    pages_crawled = (page_text or "").count("=== http")
    prompt = build_page_verify_prompt(
        company_name,
        website,
        page_text,
        serper_blob=serper_blob,
        pages_crawled=pages_crawled,
    )
    try:
        text, model = claude_generate_text(
            prompt, logger, api_key, cache=cache, model_tier="verify", on_step=on_step
        )
        logger.info("Claude page verify, model=%s", model)
        parsed = parse_page_verify_response(text)
    except Exception as exc:
        logger.warning("Claude page verify: %s", exc)
        return None

    verified, reason, chains = apply_page_verdict(
        parsed,
        page_text=page_text,
        serper_blob=serper_blob,
        require_generalunternehmer=require_generalunternehmer,
        require_small_firm=require_small_firm,
    )
    if require_generalunternehmer:
        gu_ok, gu_marker = is_generalunternehmer(
            " ".join(
                [
                    page_text,
                    serper_blob,
                    " ".join(parsed.get("matched_gu_keywords") or []),
                ]
            )
        )
    else:
        # W kampanii PL is_gu z Claude = polski wykonawca z pracą w DE.
        gu_ok = bool(parsed.get("is_gu")) or verified
        gu_marker = (parsed.get("primary_role") or "").strip()
    out = {
        "verified": verified,
        "verification_reason": reason,
        "retail_chains": chains,
        "is_gu": gu_ok,
        "gu_marker": gu_marker,
        "is_small_firm": bool(parsed.get("is_small_firm")),
        "claude": parsed,
    }
    if cache_key:
        verify_cache[cache_key] = out
    return out
