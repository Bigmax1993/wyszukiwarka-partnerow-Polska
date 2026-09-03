# -*- coding: utf-8 -*-
"""
Killer-Prompts für Claude Sonnet — GU/Filialbau-Kampagne DE.
Jeder Prompt: eine Aufgabe, strikt JSON — Portale/PDF/Operatoren ablehnen.
"""
from __future__ import annotations

import re

from campaign_keyword_profile import (
    SERPER_TEMPLATE_PATTERNS,
    gu_required_keywords_sample,
    large_company_markers_sample,
    negative_keywords_sample,
    retail_chain_keywords_sample,
    retail_context_keywords_sample,
    small_company_markers_sample,
)

_REQUIRED_CHAINS = "aldi, rewe, edeka, netto, penny, kaufland, lidl, norma"
PAGE_VERIFY_MAX_CHARS = 18000
CONTACT_EXTRACT_MAX_CHARS = 16000
_CONTACT_EXTRACT_TEXT_PRIORITY = (
    "impressum",
    "kontakt",
    "contact",
    "anschrift",
    "geschäftsführ",
    "datenschutz",
    "mailto",
    "@",
    "tel",
    "telefon",
    "phone",
    "fax",
    "e-mail",
    "email",
)
_PAGE_VERIFY_TEXT_PRIORITY = (
    "referenz",
    "projekt",
    "auftraggeber",
    "netto",
    "rewe",
    "aldi",
    "lidl",
    "kaufland",
    "penny",
    "edeka",
    "einzelhandel",
    "retail",
    "filial",
    "supermarkt",
    "discounter",
    "generalunternehmer",
    "gewerbebau",
    "karriere",
    "stellen",
)


def prioritize_page_text_for_verify(
    page_text: str,
    *,
    max_chars: int = PAGE_VERIFY_MAX_CHARS,
    priority_keywords: tuple[str, ...] | None = None,
) -> str:
    """Wichtige Zeilen zuerst — innerhalb max_chars (Keywords konfigurierbar)."""
    keys = priority_keywords or _PAGE_VERIFY_TEXT_PRIORITY
    raw = (page_text or "").strip()
    if len(raw) <= max_chars:
        return raw
    if "=== http" in raw:
        sections = re.split(r"(?=\n=== https?://)", "\n" + raw)
        sections = [s.strip() for s in sections if s.strip()]
        priority_sec: list[str] = []
        other_sec: list[str] = []
        for sec in sections:
            low = sec.lower()
            if any(k in low for k in keys):
                priority_sec.append(sec)
            else:
                other_sec.append(sec)
        merged = "\n\n".join(priority_sec + other_sec)
    else:
        lines = [ln.strip() for ln in re.split(r"[\n\r]+", raw) if ln.strip()]
        if not lines:
            return raw[:max_chars]
        priority: list[str] = []
        other: list[str] = []
        for ln in lines:
            low = ln.lower()
            if any(k in low for k in keys):
                priority.append(ln)
            else:
                other.append(ln)
        merged = " ".join(priority + other)
    if len(merged) <= max_chars:
        return merged
    return merged[: max_chars - 3] + "..."


def build_page_verify_prompt(
    company_name: str,
    website: str,
    page_text: str,
    *,
    max_chars: int = PAGE_VERIFY_MAX_CHARS,
    serper_blob: str = "",
    pages_crawled: int = 0,
) -> str:
    from claude_page_text import (
        build_automatic_evidence_excerpt,
        build_claude_context_header,
        extract_crawl_section_urls,
    )

    raw = page_text or ""
    priority_urls = extract_crawl_section_urls(raw)
    header = build_claude_context_header(
        company_name,
        website,
        serper_blob=serper_blob,
        pages_crawled=pages_crawled or max(raw.count("=== http"), 1 if raw else 0),
        priority_urls=priority_urls,
    )
    evidence = build_automatic_evidence_excerpt(raw)
    snippet = prioritize_page_text_for_verify(raw, max_chars=max_chars)
    gu_kw = ", ".join(gu_required_keywords_sample())
    retail_kw = ", ".join(retail_context_keywords_sample())
    chain_kw = ", ".join(retail_chain_keywords_sample())
    neg_kw = ", ".join(negative_keywords_sample())
    small_kw = ", ".join(small_company_markers_sample())
    large_kw = ", ".join(large_company_markers_sample())
    return f"""ROLLE
Jesteś analitykiem due-diligence B2B. Target: POLSKA firma wykonawcza / wyposażeniowa,
która REALNIE działa na terenie Niemiec (posadzki, meble sklepowe, Ladenbau, Innenausbau,
budownictwo, podwykonawstwo — elektryka, HVAC, GK, witryny).

Shopfitting / posadzki / wyposażenie sklepów = TAK, to jest cel.
KEIN Ziel: urzędy, portale, agencje pracy, deweloperzy mieszkaniowi, sieci handlowe jako operatorzy,
czysto niemieckie GmbH bez polskiego podmiotu, firmy tylko na PL bez śladu pracy w DE.

AUFGABE
Przeczytaj cały wyciąg strony (podstrony === URL ===). Pasuje do targetu?
Odpowiedz TYLKO JSON — bez Markdown.

NACHWEIS pracy w DE (wymagany do is_gu=true i has_retail_context=true)
• Niemcy / Deutschland / landy / referencje DE / zdjęcia budów w DE
• Lidl, Aldi, Kaufland, Edeka, Rewe, Rossmann, DM, Netto, Penny jako realizacja
• impresum z PL (sp. z o.o., S.A., adres PL, NIP) + oferta DE

SOFORT is_gu=false
• brak polskiego podmiotu (tylko GmbH DE bez PL)
• brak jakiegokolwiek tropu DE
• portal, urząd, agencja pracy, sklep detaliczny (Biedronka/Żabka jako sieć)

ENTSCHEIDUNGSBAUM
1) Portal/urząd/rekrutacja/handel detaliczny → is_gu=false
2) Niemieckie-only GmbH bez PL → is_gu=false
3) Polska firma, ale zero śladu DE → is_gu=false, has_retail_context=false
4) Polska firma + praca w DE w branży wykonawczej → is_gu=true, has_retail_context=true
5) Wielkość → is_small_firm

HANDELSKETTE (pomocniczo, nie obowiązkowa jeśli jest inny ślad DE)
Whitelist: {_REQUIRED_CHAINS}
matched_chains: tylko jeśli sieć WÖRTLICH jako realizacja.

is_small_firm=true: sp. z o.o., firma rodzinna, <250 MA, jedna siedziba PL
is_small_firm=false: Budimex, Strabag, Skanska, giełda, >500 MA, sieć handlowa

KLEIN: {small_kw}
GROSS: {large_kw}

is_gu = polska firma wykonawcza z pracą w DE (TAK: shopfitting, posadzki, podwykonawca).
has_retail_context = ślad obiektów handlowych / DE (markety, drogerie, galerie, gastro).

IM ZWEIFEL: is_gu=false, has_retail_context=false.

HILFS
[role] {gu_kw}
[retail] {retail_kw}
[sieci] {chain_kw}
[odrzuć] {neg_kw}

BEISPIELE
✓ JA: „Montaż sklepów Lidl w Niemczech" + sp. z o.o. Wrocław
✓ JA: posadzki żywiczne, referencje Aldi/Kaufland DE
✓ JA: meble sklepowe, realizacje Rossmann Deutschland
✗ NEIN: samo GmbH z NRW bez polskiego podmiotu
✗ NEIN: agencja pracy / OLX / urząd gminy
✗ NEIN: Biedronka jako sieć handlowa
✗ NEIN: polski deweloper mieszkań bez DE

FELDER JSON (exakt diese Keys)
{{
  "matched_gu_keywords": [],
  "matched_retail_keywords": [],
  "matched_chains": [],
  "matched_negative_keywords": [],
  "is_gu": false,
  "has_retail_context": false,
  "is_small_firm": false,
  "primary_role": "",
  "reason": ""
}}

REGELN
• matched_*: tylko z wyciągu — nic nie wymyślaj
• primary_role: WyposazenieSklepow, Posadzki, Budownictwo, Podwykonawca, Portal, Urzad, AgencjaPracy, SiecHandlowa, …
• reason: max. 2 zdania

KONTEXT
{header}

AUTOMATISCHE DOWODY (Vorauswahl aus Crawl)
{evidence}

WEBSITE-AUSZUG (alle Unterseiten, === URL ===)
{snippet or "(leer)"}
"""


def build_row_cleanup_prompt(
    *,
    company: str,
    address: str,
    phone: str,
    email: str,
    website: str,
    states: str,
    handelsketten: str = "",
    url: str = "",
) -> str:
    return f"""ROLLE
Du bist Daten-QA-Leiter vor dem Excel-Export. Dein Output landet 1:1 in der Tabelle „Kontakte".
Fehlerhafte Zeilen kosten echte B2B-Mails an falsche Empfänger — sei gnadenlos präzise.

ZIELGRUPPE (nur te firmy mogą mieć nazwę)
Polskie firmy (sp. z o.o., S.A., sp. j., P.H.U.) działające w Niemczech:
wyposażenie sklepów, posadzki, budownictwo, podwykonawstwo.
KEINE urzędy, portale, agencje pracy, sieci handlowe, czysto niemieckie GmbH bez PL.

AUFGABE
Bereinige die Eingabefelder für Excel. Antworte NUR mit einem JSON-Objekt — kein Markdown.

SCHEMA (exakt, alle Keys, leere Strings erlaubt)
{{"company_name_clean":"","address":"","phone":"","website":"","bundesland":"","handelsketten":"","url":""}}

═══ company_name_clean — KILLER-REGELN (höchste Priorität) ═══
ERLAUBT: Offizieller Firmenname + polska forma prawna w JEDNEJ linii.
Forma: sp. z o.o., S.A., sp. j., sp. k., s.c., P.H.U. (GmbH tylko jeśli to polski podmiot z DE).
OK: „Ergo Store sp. z o.o.", „Posadzki-X S.A."
NICHT OK: „Generalunternehmer Leipzig", „ALDI Neubau Borna", urząd gminy, portal OLX
bundesland = województwo polskie siedziby (np. Dolnoslaskie, Wielkopolskie), nie land DE.

SOFORT company_name_clean = "" bei:
• PDF/Dokument: [PDF], Bebauungsplan, Auswirkungsanalyse, „Seite X von Y"
• Software/IT: PDF-XChange, Adobe, Microsoft, Tracker, shop@pdf-*
• Portale/Kataloge: 11880, GelbeSeiten, Wikipedia, Vergabemarktplatz, Nexxt-Change, IHK-Listen, Top-10-Listen
• Nur Ort/Projekt/Headline: „Erfurt", „Penny Neubau", Zeitungstitel ohne Firma
• URL, E-Mail, Emoji, Marketing-Slogan, Doppelpunkt am Ende

Ableitung nur aus Impressum-Kontext erlaubt, wenn Eingabe Müll ist — NIEMALS erfinden.
Unsicher → "".

═══ Excel-Spalten (Formatierung) ═══
• address → „Straße, PLZ Ort" (Deutschland) oder ""
• phone → genau EINE deutsche Nummer (+49 oder 0…), kein Fax, kein „Tel./Fax", kein Doppelwert
• website → https://firmendomain.tld (Root, keine Unterseite, kein Verzeichnis, kein PDF)
• url → identisch zur Basis-URL (https://domain.tld)
• bundesland → GENAU ein Wert aus: [{states}] — sonst ""
• handelsketten → nur Kleinbuchstaben, kommagetrennt: rewe, aldi, edeka, netto, penny, kaufland, lidl, norma — oder ""
• email_nur_info: NICHT in JSON übernehmen — nur zur Plausibilitätsprüfung

NEGATIV-BEISPIELE (alles → leere Felder oder Name "")
Eingabe name=„PDF Bauantrag Stadt Erfurt" → company_name_clean=""
Eingabe name=„REWE Markt Süd" → company_name_clean=""
Eingabe phone=„Tel 0341 123, Fax 0341 456" → phone=„+49 341 123" (nur erste Tel.)

EINGABE
name={company}
address={address}
phone={phone}
website={website}
url={url}
handelsketten={handelsketten}
email_nur_info={email}
"""


def build_contact_extract_prompt(
    company_name: str,
    website: str,
    page_text: str,
) -> str:
    from claude_page_text import build_claude_context_header, extract_crawl_section_urls

    raw = page_text or ""
    header = build_claude_context_header(
        company_name,
        website,
        pages_crawled=max(raw.count("=== http"), 1 if raw else 0),
        priority_urls=extract_crawl_section_urls(raw),
    )
    snippet = prioritize_page_text_for_verify(
        raw,
        max_chars=CONTACT_EXTRACT_MAX_CHARS,
        priority_keywords=_CONTACT_EXTRACT_TEXT_PRIORITY,
    )
    return f"""ROLLE
Szukasz kontaktów B2B polskich firm działających w Niemczech.
Zadanie: e-mail, telefon, imię osoby z impresum — tylko to, co WÖRTLICH jest w tekście.

KONTEXT
{header}

REGELN (streng)
• Nur Daten extrahieren, die WÖRTLICH im Auszug stehen — nichts erfinden, nichts raten.
• Impressum / Kontakt / Dane firmy mają najwyższy priorytet.
• mailto:-Links und sichtbare @-Adressen zählen.
• Telefon: PL (+48) lub DE (+49), bez samego faxu jeśli jest Tel.
• Keine Portale (OLX, Aleo, 11880), keine noreply/no-reply.
• Local-Part (vor @): 1–50 Zeichen.
• contact_first_name: tylko realne imię (Jan, Anna) z impresum/zarządu — bez nazwiska jeśli niepewne.

OUTPUT (nur JSON, kein Markdown)
{{"company_name":"","emails":[],"phones":[],"impressum_emails":[],"contact_first_name":"","reason":""}}

Felder:
• company_name — oficjalna nazwa z impresum, sonst ""
• emails — firmowe maile
• impressum_emails — z impresum/dane firmy
• phones — max. 3
• contact_first_name — imię do zwrotu (np. Jan) albo ""
• reason — max. 1 Satz

WEBSITE-AUSZUG (vollständiger Domain-Crawl)
{snippet or "(leer)"}
"""


def build_discovery_terms_prompt(
    lands: list[str],
    *,
    city_str: str,
    land_str: str,
    terms_requested: int,
    exclude_block: str = "",
    max_term_len: int = 55,
) -> str:
    templates = "\n".join(f"- {t}" for t in SERPER_TEMPLATE_PATTERNS[:10])
    gu_kw = ", ".join(gu_required_keywords_sample(max_items=6))
    retail_kw = ", ".join(retail_context_keywords_sample(max_items=8))
    neg_kw = ", ".join(negative_keywords_sample(max_items=8))
    return f"""ROLLE
Generujesz zapytania Google (Serper) do discovery POLSKICH firm, które pracują w Niemczech
(wyposażenie sklepów, posadzki, budownictwo, podwykonawcy). Miasto = siedziba w PL.

KONTEXT
Województwo: {land_str}
Miasta: {city_str}

VORLAGEN ({{city}} = polskie miasto)
{templates}

PFLICHT pro Zeile
• Branża: wyposażenie sklepów / posadzki / Ladenbau / podwykonawca / budownictwo
• Znacznik Niemiec: Niemcy albo Deutschland
• Opcjonalnie sieć: {_REQUIRED_CHAINS} (rotieren)
• Max {max_term_len} Zeichen
• Polski (ew. Ladenbau/Innenausbau), bez numeracji, bez cudzysłowów

VERBOTEN
• {neg_kw}
• urzędy, OLX, agencje pracy, Biedronka/Żabka jako operator
• czyste „Generalunternehmer Filialbau {{miasto DE}}"
• duplikaty
{exclude_block}

GUTE BEISPIELE
wyposażenie sklepów Wrocław Niemcy
posadzki żywiczne Poznań Lidl
podwykonawca budowa sklepów Katowice Deutschland
Ladenbau Firma Szczecin Polen

SCHLECHTE BEISPIELE
Generalunternehmer Filialbau Hannover Aldi markt
urząd gminy Wrocław
praca Niemcy agencja Bydgoszcz

OUTPUT
Genau {terms_requested} Zeilen — eine Anfrage pro Zeile, sonst NICHTS (kein JSON, kein Kommentar).
"""


def build_custom_email_prompt_de(
    draft: str,
    company_name: str,
    *,
    city_name: str = "",
    delivery_address: str = "",
) -> str:
    ctx_city = f"Projektstadt: {city_name}. " if city_name else ""
    ctx_addr = f"Lieferadresse (unverändert): {delivery_address}. " if delivery_address else ""
    return f"""ROLLE
Du bist B2B-Texter für formelle Preisanfragen auf Deutsch. Minimal anpassen, nicht umschreiben.

EMPFÄNGER
{company_name}
{ctx_city}{ctx_addr}

AUFGABE
Passe die Nutzervorlage minimal an (1–2 Sätze Kontext zur Firma/Region).
Verbessere Lesbarkeit. ALLE Fakten exakt beibehalten: Mengen, Daten, Adressen, Fraktionen, Telefon, Signatur.

VERBOTEN
• Preise erfinden
• Wörter: kostenlos, Sonderangebot, dringend, jetzt zuschlagen
• Signatur inhaltlich ändern (Person, Firma, Telefon identisch)

OUTPUT (nur JSON)
{{"subject":"...","body":"..."}}
subject: max 78 Zeichen, konkret, ohne Re:/Erinnerung
body: vollständige sendefertige E-Mail, Plain Text

VORLAGE
{draft}
"""


def build_custom_email_prompt_pl(
    draft: str,
    company_name: str,
    *,
    city_name: str = "",
    delivery_address: str = "",
) -> str:
    ctx_city = f"Miasto/inwestycja: {city_name}. " if city_name else ""
    ctx_addr = f"Adres dostawy (bez zmian): {delivery_address}. " if delivery_address else ""
    return f"""ROLLE
Jesteś redaktorem B2B dla oficjalnych zapytań ofertowych po polsku. Minimalna personalizacja.

ADRESAT
{company_name}
{ctx_city}{ctx_addr}

ZADANIE
Dostosuj szablon (1–2 zdania kontekstu). Popraw styl. ZACHOWAJ wszystkie fakty: ilości, daty, adresy, frakcje, telefony, podpis.

ZAKAZ
• Wymyślanie cen
• Słowa: gratis, promocja, pilne, kliknij
• Zmiana treści podpisu

OUTPUT (tylko JSON)
{{"subject":"...","body":"..."}}
subject: max 78 znaków, bez Re:/Przypomnienie
body: pełny mail gotowy do wysyłki, plain text

SZABLON
{draft}
"""
