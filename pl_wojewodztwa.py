# -*- coding: utf-8 -*-
"""
Rotacja województw PL + frazy Serper: polskie firmy działające w Niemczech.
Miasto = siedziba w PL, nie plac budowy w DE.
"""
from __future__ import annotations

WOJEWODZTWO_CONFIG: dict[str, dict] = {
    "Dolnoslaskie": {
        "short": "DŚ",
        "cities": (
            "Wrocław",
            "Legnica",
            "Wałbrzych",
            "Jelenia Góra",
            "Lubin",
            "Głogów",
            "Świdnica",
            "Bolesławiec",
        ),
    },
    "Lubuskie": {
        "short": "LB",
        "cities": (
            "Zielona Góra",
            "Gorzów Wielkopolski",
            "Żary",
            "Nowa Sól",
            "Świebodzin",
        ),
    },
    "Wielkopolskie": {
        "short": "WP",
        "cities": (
            "Poznań",
            "Kalisz",
            "Konin",
            "Piła",
            "Leszno",
            "Gniezno",
            "Ostrów Wielkopolski",
        ),
    },
    "Opolskie": {
        "short": "OP",
        "cities": ("Opole", "Kędzierzyn-Koźle", "Nysa", "Brzeg", "Kluczbork"),
    },
    "Slaskie": {
        "short": "ŚL",
        "cities": (
            "Katowice",
            "Gliwice",
            "Zabrze",
            "Bytom",
            "Rybnik",
            "Częstochowa",
            "Bielsko-Biała",
            "Tychy",
        ),
    },
    "Zachodniopomorskie": {
        "short": "ZP",
        "cities": (
            "Szczecin",
            "Koszalin",
            "Stargard",
            "Kołobrzeg",
            "Świnoujście",
        ),
    },
    "Lodzkie": {
        "short": "ŁD",
        "cities": (
            "Łódź",
            "Piotrków Trybunalski",
            "Pabianice",
            "Tomaszów Mazowiecki",
            "Bełchatów",
        ),
    },
    "Mazowieckie": {
        "short": "MZ",
        "cities": (
            "Warszawa",
            "Radom",
            "Płock",
            "Siedlce",
            "Ostrołęka",
            "Pruszków",
        ),
    },
    "Pomorskie": {
        "short": "PM",
        "cities": (
            "Gdańsk",
            "Gdynia",
            "Sopot",
            "Słupsk",
            "Tczew",
            "Starogard Gdański",
        ),
    },
    "Kujawsko-Pomorskie": {
        "short": "KP",
        "cities": (
            "Bydgoszcz",
            "Toruń",
            "Włocławek",
            "Grudziądz",
            "Inowrocław",
        ),
    },
    "Malopolskie": {
        "short": "MP",
        "cities": (
            "Kraków",
            "Tarnów",
            "Nowy Sącz",
            "Oświęcim",
            "Nowy Targ",
        ),
    },
    "Podkarpackie": {
        "short": "PK",
        "cities": (
            "Rzeszów",
            "Przemyśl",
            "Stalowa Wola",
            "Mielec",
            "Krosno",
        ),
    },
    "Lubelskie": {
        "short": "LU",
        "cities": ("Lublin", "Chełm", "Zamość", "Biała Podlaska", "Puławy"),
    },
    "Warminsko-Mazurskie": {
        "short": "WM",
        "cities": ("Olsztyn", "Elbląg", "Ełk", "Ostróda", "Giżycko"),
    },
    "Swietokrzyskie": {
        "short": "ŚK",
        "cities": ("Kielce", "Ostrowiec Świętokrzyski", "Starachowice", "Sandomierz"),
    },
    "Podlaskie": {
        "short": "PD",
        "cities": ("Białystok", "Suwałki", "Łomża", "Augustów"),
    },
}

WOJEWODZTWO_DISPLAY: dict[str, str] = {
    "Dolnoslaskie": "Dolnośląskie",
    "Lubuskie": "Lubuskie",
    "Wielkopolskie": "Wielkopolskie",
    "Opolskie": "Opolskie",
    "Slaskie": "Śląskie",
    "Zachodniopomorskie": "Zachodniopomorskie",
    "Lodzkie": "Łódzkie",
    "Mazowieckie": "Mazowieckie",
    "Pomorskie": "Pomorskie",
    "Kujawsko-Pomorskie": "Kujawsko-Pomorskie",
    "Malopolskie": "Małopolskie",
    "Podkarpackie": "Podkarpackie",
    "Lubelskie": "Lubelskie",
    "Warminsko-Mazurskie": "Warmińsko-Mazurskie",
    "Swietokrzyskie": "Świętokrzyskie",
    "Podlaskie": "Podlaskie",
}

WOJEWODZTWO_ALIASES: dict[str, str] = {
    "ds": "Dolnoslaskie",
    "dś": "Dolnoslaskie",
    "dolnoslaskie": "Dolnoslaskie",
    "dolnośląskie": "Dolnoslaskie",
    "lb": "Lubuskie",
    "lubuskie": "Lubuskie",
    "wp": "Wielkopolskie",
    "wielkopolskie": "Wielkopolskie",
    "op": "Opolskie",
    "opolskie": "Opolskie",
    "sl": "Slaskie",
    "śl": "Slaskie",
    "slaskie": "Slaskie",
    "śląskie": "Slaskie",
    "zp": "Zachodniopomorskie",
    "zachodniopomorskie": "Zachodniopomorskie",
    "ld": "Lodzkie",
    "łd": "Lodzkie",
    "lodzkie": "Lodzkie",
    "łódzkie": "Lodzkie",
    "mz": "Mazowieckie",
    "mazowieckie": "Mazowieckie",
    "pm": "Pomorskie",
    "pomorskie": "Pomorskie",
    "kp": "Kujawsko-Pomorskie",
    "kujawsko-pomorskie": "Kujawsko-Pomorskie",
    "mp": "Malopolskie",
    "malopolskie": "Malopolskie",
    "małopolskie": "Malopolskie",
    "pk": "Podkarpackie",
    "podkarpackie": "Podkarpackie",
    "lu": "Lubelskie",
    "lubelskie": "Lubelskie",
    "wm": "Warminsko-Mazurskie",
    "warminsko-mazurskie": "Warminsko-Mazurskie",
    "warmińsko-mazurskie": "Warminsko-Mazurskie",
    "sk": "Swietokrzyskie",
    "śk": "Swietokrzyskie",
    "swietokrzyskie": "Swietokrzyskie",
    "świętokrzyskie": "Swietokrzyskie",
    "pd": "Podlaskie",
    "podlaskie": "Podlaskie",
}

RETAIL_CHAINS_ROTATION = (
    "Lidl",
    "Aldi",
    "Kaufland",
    "Rossmann",
    "DM",
    "Edeka",
    "Rewe",
    "Netto",
    "Penny",
)

# Frazy Serper: siedziba w PL + praca / realizacje w DE.
# Warstwa główna: szerokie (miasto + branża + Niemcy) — bez sieci i bez województwa.
# Sieci (Aldi/Lidl/…) tylko w CHAIN_LAYER_* (rzadko), żeby nie generować api_zero.
CHAIN_SIMPLE_TERM_TEMPLATES = (
    "podwykonawca budowlany {city} Niemcy",
    "firma budowlana {city} Deutschland",
    "firma budowlana {city} realizacje Niemcy",
    "wyposażenie sklepów {city} Niemcy",
    "Ladenbau Polen {city}",
    "Innenausbau Polen {city} Deutschland",
    "posadzki przemysłowe {city} Niemcy",
    "posadzki żywiczne {city} Niemcy",
    "wykończenia wnętrz sklepy Niemcy {city}",
    "montaż sklepów {city} Niemcy",
    "hale przemysłowe {city} Niemcy",
    "instalacje elektryczne Niemcy {city}",
    "klimatyzacja wentylacja Niemcy {city}",
    "fit-out sklepy Niemcy {city}",
    "stolarka aluminiowa witryny Niemcy {city}",
    "podwykonawca {city} budownictwo Niemcy",
    "obiekty handlowe {city} podwykonawca Niemcy",
)

TERM_TEMPLATES = (
    "podwykonawca {city} {wojewodztwo} Niemcy",
    "firma budowlana {wojewodztwo} realizacje Deutschland",
    "wyposażenie sklepów {wojewodztwo} Niemcy",
    "wykończenia restauracje hotele Niemcy {city}",
    "posadzki żywiczne hale magazyny Niemcy {city}",
    "instalacje HVAC sklepy Niemcy {city}",
    "suche zabudowy GK {city} Niemcy",
)

# Osobna, rzadka warstwa z sieciami handlowymi DE.
CHAIN_LAYER_TERM_TEMPLATES = (
    "montaż sklepów {chain} Niemcy {city}",
    "wyposażenie sklepów {city} Niemcy {chain}",
    "posadzki sklepowe {city} {chain}",
)

SIMPLE_TERM_TEMPLATES = CHAIN_SIMPLE_TERM_TEMPLATES

SERPER_NEGATIVE_TERMS = (
    "urząd",
    "urzad",
    "gmina",
    "starostwo",
    "ihk",
    "handwerkskammer",
    "olx",
    "aleo",
    "panorama firm",
    "pkt.pl",
    "firmy.org",
    "biznesfinder",
    "agencja pracy",
    "praca tymczasowa",
    "zeitarbeit",
    "deweloper mieszkaniowy",
    "biedronka",
    "żabka",
    "zabka",
    "lidl polska praca",
    "oferty pracy",
    "przetarg",
    "bip.gov.pl",
    "gov.pl",
    "generalunternehmer",
    "generalübernehmer",
    "facebook",
    "linkedin",
    "instagram",
    "tiktok",
    "pracuj.pl",
    "indeed",
    "stepstone",
    "gowork",
    "katalog firm",
    "portal pracy",
    "portal branżowy",
    "muratorplus",
    "baunetz",
    "baulinks",
    "ibau",
)

POLISH_LEGAL_FORM_MARKERS = (
    "sp. z o.o.",
    "sp. z o.o",
    "spółka z o.o.",
    "spolka z o.o.",
    "s.a.",
    "sa ",
    "sp. j.",
    "sp.j.",
    "sp. k.",
    "sp.k.",
    "s.c.",
    "p.h.u.",
    "phu ",
)


def normalize_wojewodztwo_key(name: str) -> str:
    n = (name or "").strip()
    if not n:
        return n
    low = n.lower().replace("ł", "l").replace("ą", "a").replace("ę", "e")
    low = low.replace("ś", "s").replace("ć", "c").replace("ń", "n").replace("ó", "o").replace("ż", "z").replace("ź", "z")
    if n in WOJEWODZTWO_CONFIG:
        return n
    alias = WOJEWODZTWO_ALIASES.get(n.lower()) or WOJEWODZTWO_ALIASES.get(low)
    if alias:
        return alias
    for key, display in WOJEWODZTWO_DISPLAY.items():
        if display.lower() == n.lower() or key.lower() == n.lower():
            return key
    return n


def display_wojewodztwo(key: str) -> str:
    k = normalize_wojewodztwo_key(key)
    return WOJEWODZTWO_DISPLAY.get(k, key or "")
