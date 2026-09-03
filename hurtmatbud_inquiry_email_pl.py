# -*- coding: utf-8 -*-
"""Maile B2B Hurt Matbud — polski, imienny, oferta otwarć DE + baza GU."""
from __future__ import annotations

import json
import re
from typing import Any

SENDER_NAME = "Maksym Swinczak"
SENDER_COMPANY = "Hurt Matbud"
SENDER_PHONE = "516 513 965"
SENDER_PHONE_DIGITS = "516513965"
DEFAULT_SUBJECT = "Otwarcia sklepów w Niemczech — krótka sprawa"

_MALE_VOCATIVE = {
    "jan": "Janie",
    "piotr": "Piotrze",
    "paweł": "Pawle",
    "pawel": "Pawle",
    "marek": "Marku",
    "tomasz": "Tomaszu",
    "andrzej": "Andrzeju",
    "krzysztof": "Krzysztofie",
    "michał": "Michale",
    "michal": "Michale",
    "adam": "Adamie",
    "wojciech": "Wojciechu",
    "łukasz": "Łukaszu",
    "lukasz": "Łukaszu",
    "maciej": "Macieju",
    "marcin": "Marcinie",
    "jakub": "Jakubie",
    "grzegorz": "Grzegorzu",
    "robert": "Robercie",
    "dariusz": "Dariuszu",
    "rafał": "Rafale",
    "rafal": "Rafale",
}

_FEMALE_NAMES = frozenset(
    {
        "anna",
        "maria",
        "katarzyna",
        "małgorzata",
        "malgorzata",
        "agnieszka",
        "barbara",
        "ewa",
        "magdalena",
        "elżbieta",
        "elzbieta",
        "krystyna",
        "joanna",
        "aleksandra",
        "monika",
        "paulina",
        "natalia",
        "karolina",
        "iwona",
        "beata",
    }
)


def polish_vocative_first_name(first: str) -> str:
    n = (first or "").strip()
    if not n:
        return ""
    low = n.lower()
    mapped = _MALE_VOCATIVE.get(low)
    if mapped:
        if n[0].isupper():
            return mapped[0].upper() + mapped[1:]
        return mapped
    if low.endswith("a") and low not in ("kuba", "barnaba"):
        return n[:-1] + "o"
    return n


def greeting_for_contact(first_name: str = "", company_name: str = "") -> tuple[str, bool]:
    first = (first_name or "").strip()
    if first and re.match(r"^[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż\-]{2,30}$", first):
        voc = polish_vocative_first_name(first)
        if first.lower() in _FEMALE_NAMES or first.lower().endswith("a"):
            return f"Szanowna Pani {voc},", True
        return f"Szanowny Panie {voc},", True
    return "Szanowni Państwo,", False


def email_signature_block() -> str:
    return (
        f"Z poważaniem\n"
        f"{SENDER_NAME}\n"
        f"{SENDER_COMPANY}\n"
        f"tel. {SENDER_PHONE}"
    )


def ensure_sender_phone_in_body(body: str) -> str:
    digits = re.sub(r"\D", "", body or "")
    if SENDER_PHONE_DIGITS in digits:
        return body
    text = (body or "").rstrip()
    if text:
        return text + "\n\n" + email_signature_block() + "\n"
    return email_signature_block() + "\n"


def build_fallback_email_body(
    company_name: str,
    *,
    first_name: str = "",
    wojewodztwo: str = "",
) -> tuple[str, str, str, bool]:
    greeting, used = greeting_for_contact(first_name, company_name)
    firm = (company_name or "Państwa firmy").strip()
    woj = (wojewodztwo or "").strip()
    woj_note = f" (siedziba: {woj})" if woj else ""
    if used:
        intro = (
            f"nazywam się {SENDER_NAME.split()[0]} i piszę z {SENDER_COMPANY} "
            f"do {firm}{woj_note}."
        )
    else:
        intro = (
            f"piszę z {SENDER_COMPANY} do zespołu {firm}{woj_note} — "
            "chodzi o Wasze realizacje w Niemczech, nie o masową wysyłkę."
        )
    body = f"""{greeting}

{intro}

Widzę, że robicie rzeczy, które w DE naprawdę się przydają (wyposażenie sklepów, posadzki, montaż, podwykonawstwo). Dlatego nie chcę Wam wciskać „bazy 10 tysięcy firm”, tylko konkret.

Ogarniam na bieżąco dwa tematy:
– nowe otwarcia lokalizacji w Niemczech (sklepy, markety, restauracje, drogerie, galerie) — sprawdzam adres, czy obiekt faktycznie startuje, stronę i kontakt ze strony firmy;
– generalnych wykonawców, którzy budują markety po całych Niemczech.

Jak to u Was ma sens, złożę krótką próbkę: 5–10 tropów pod niszę i region. Bez zobowiązań, bez prezentacji na 40 slajdów. Jak wolicie, możemy po prostu pogadać przez telefon.

{email_signature_block()}
"""
    return DEFAULT_SUBJECT, greeting, body.strip() + "\n", used


def build_hurtmatbud_email_prompt(
    company_name: str,
    *,
    first_name: str = "",
    wojewodztwo: str = "",
    website: str = "",
    trade_hint: str = "",
) -> str:
    greeting, used = greeting_for_contact(first_name, company_name)
    return f"""ROLLE
Piszesz jeden mail B2B po polsku, jak człowiek do człowieka — nie jak agencja, nie jak CRM.
Nadawca: {SENDER_NAME} z firmy {SENDER_COMPANY}. Mówi o sobie „ja”.
Ton: spokojny, konkretny, trochę bezpośredni. Można „Wy/Wasz”. Bez korpo-lania.

TO NIE JEST
sprzedaż bazy, cold spam, „lead magnet”, mailing z szablonu na 500 firm.

TO JEST
krótka propozycja: mam świeże tropy z Niemiec i mogę pokazać próbkę, jeśli to u Was realnie gra.

ODBIORCA
Firma: {company_name or "(brak nazwy)"}
Imię z impresum (użyj TYLKO jeśli niepuste): {first_name or "(brak)"}
Województwo siedziby: {wojewodztwo or "(nieznane)"}
Strona: {website or "(brak)"}
Branża (jeśli znana): {trade_hint or "wyposażenie sklepów / posadzki / budownictwo / podwykonawstwo w DE"}

ZWROT
Jeśli imię jest podane: pierwsza linia dokładnie: {greeting}
Jeśli imienia brak: "Szanowni Państwo," i w 1. zdaniu nazwa firmy.

JAK PISAĆ (ludzki mail)
• 3–5 krótkich akapitów. Zdania jak w rozmowie, nie jak folder reklamowy.
• Wejście: kim jesteś i dlaczego piszesz akurat do TEJ firmy (branża / DE), bez ściemy.
• Potem dwa fakty, zwyczajnym językiem:
  1) śledzisz nowe otwarcia w Niemczech (sklepy, markety, restauracje, drogerie, galerie) i sam weryfikujesz adres, status, www, kontakt;
  2) masz zestaw generalnych wykonawców, którzy budują markety w całych Niemczech.
• Daj do zrozumienia, że to bieżące tropy, nie archiwum z 2019.
• CTA miękkie: próbka 5–10 tropów albo krótka rozmowa. Zero presji, zero „odpisz do 24h”.
• Na końcu podpis. KONIECZNIE numer telefonu w podpisie, dokładnie: tel. {SENDER_PHONE}
  (można dodać „najłatwiej zadzwonić albo rzucić SMSa”).

ZAKAZY
• ZERO ALL CAPS, zero „DARMOWA BAZA”, zero „10000 FIRM”, zero fałszywych NIP / kontraktów / dat / kwot.
• Nie wymyślaj realizacji odbiorcy, których nie ma w danych powyżej.
• Nie obiecuj wyłączności ani gwarancji kontraktu.
• NIE MFG, NIE Fliesenboden, NIE Moderner Fliesenboden, NIE office@mfg.
• Nie wstawiaj żadnego innego numeru telefonu niż {SENDER_PHONE}.
• Subject po polsku, konkretny, ludzki, bez clickbaitu, max 90 znaków.
  Przykład dobrego: „Otwarcia sklepów w DE — próbka tropów”
  Przykład złego: „PILNE!!! DARMOWA BAZA GU”

OUTPUT — wyłącznie JSON, bez Markdown:
{{"subject":"","greeting":"","body":"","used_first_name": {str(used).lower()}}}

body = pełna treść (zwrot + treść + podpis {SENDER_NAME} / {SENDER_COMPANY} / tel. {SENDER_PHONE}).
"""


def parse_email_json(raw: str, company_name: str = "", first_name: str = "") -> dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            subj, greet, body, used = build_fallback_email_body(
                company_name, first_name=first_name
            )
            return {
                "subject": subj,
                "greeting": greet,
                "body": body,
                "used_first_name": used,
            }
        data = json.loads(m.group(0))
    if not isinstance(data, dict):
        subj, greet, body, used = build_fallback_email_body(
            company_name, first_name=first_name
        )
        return {
            "subject": subj,
            "greeting": greet,
            "body": body,
            "used_first_name": used,
        }
    subject = str(data.get("subject") or DEFAULT_SUBJECT).strip()
    greeting = str(data.get("greeting") or "").strip()
    body = str(data.get("body") or "").strip()
    used = bool(data.get("used_first_name"))
    if not body:
        subj, greet, body, used = build_fallback_email_body(
            company_name, first_name=first_name
        )
        return {
            "subject": subj,
            "greeting": greet,
            "body": body,
            "used_first_name": used,
        }
    return {
        "subject": subject[:90],
        "greeting": greeting,
        "body": body,
        "used_first_name": used,
    }
