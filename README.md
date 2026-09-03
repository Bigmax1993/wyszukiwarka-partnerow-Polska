# Wyszukiwarka partnerów — kampania PL→DE (Hurt Matbud)

Repozytorium: [Bigmax1993/Wyszukiwarka-partnerow](https://github.com/Bigmax1993/Wyszukiwarka-partnerow)

Pipeline: **Serper (PL) → strony www → cache/Excel → maile Hurt Matbud**.

**Odbiorcy:** polskie firmy (sp. z o.o. / S.A. / sp. j. / P.H.U. / adres PL / domena `.pl`), które **realnie pracują w Niemczech** — wyposażenie sklepów / Ladenbau, posadzki, budownictwo, podwykonawcy.

**Oferta w mailu:** (1) świeże otwarcia lokalizacji w DE (sklepy, markety, restauracje, drogerie, galerie); (2) baza generalnych wykonawców budujących markety w Niemczech.

| Moduł | Plik |
|-------|------|
| Scraper | `de_gu_bauunternehmen_scraper.py` |
| Województwa + frazy | `pl_wojewodztwa.py`, `de_gu_keywords.py` |
| Rotacja | `gu_bundesland_rotation.py` → `Wyniki/pl_wojewodztwa_rotation.json` |
| Filtr PL+DE | `pl_de_company_filter.py` |
| Mail PL | `hurtmatbud_inquiry_email_pl.py` |

Nadawca B2B: `hurtmatbud2@gmail.com` (hasło aplikacji tylko w env / GitHub Secrets, **nie w git**).
Raport Excel wewnętrzny: `EXCEL_REPORT_TO` (domyślnie `svinchak1993@gmail.com`).
Excel **Kontakte**: dokładnie **Nazwa firmy | Adres | Numer Telefonu | E-mail**. Szczegóły (województwo, www, URL) na arkuszu **Szczegoly**.
Drive: [folder wyników](https://drive.google.com/drive/folders/1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ) — ID `1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ`.

## Szybki start (lokalnie)

```powershell
cd "C:\Users\svinc\Documents\Wyszukiwarka partnerow"
pip install -r requirements.txt
$env:KANBUD_PROJECT_ROOT = "$PWD\libs"

python de_gu_bauunternehmen_scraper.py --test
python de_gu_bauunternehmen_scraper.py --test --wojewodztwo Dolnoslaskie
python de_gu_bauunternehmen_scraper.py --rotation-status
python de_gu_bauunternehmen_scraper.py --dry-run-email --send-emails-only
```

Pełna bateria testów (bez live API):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\RUN_ALL_TESTS.ps1 -SkipApiLive
```

## Rotacja województw

Jeden województwo na cykl discovery (`--rotate-wojewodztwo`; `--rotate-bundesland` to alias).

Kolejność: Dolnośląskie → Lubuskie → Wielkopolskie → Opolskie → Śląskie → Zachodniopomorskie → Łódzkie → Mazowieckie → Pomorskie → Kujawsko-Pomorskie → Małopolskie → Podkarpackie → Lubelskie → Warmińsko-Mazurskie → Świętokrzyskie → Podlaskie.

```powershell
python de_gu_bauunternehmen_scraper.py --rotate-wojewodztwo
python de_gu_bauunternehmen_scraper.py --wojewodztwo Dolnoslaskie
```

Serper: `gl=pl`, `hl=pl`, frazy po polsku ze znacznikiem Niemiec / Deutschland.

## Maile Hurt Matbud

- Język: polski, imienne (`Szanowny Panie Janie` / `Szanowni Państwo` + nazwa firmy)
- Claude Sonnet generuje JSON `{subject, greeting, body, used_first_name}`
- Bez PPTX MFG (`DISABLE_EMAIL_ATTACHMENT=1`)
- Limit pierwszego LIVE: `MAX_SEND_PER_RUN=20` (dzienny `DAILY_EMAIL_LIMIT` zostaje)
- SMTP: `smtp.gmail.com:465` gdy nadawca to `@gmail.com`
- **Nie wysyłaj live**, dopóki dry-run nie jest OK

```powershell
python de_gu_bauunternehmen_scraper.py --dry-run-email --send-emails-only
# LIVE (max 20) — tylko po akceptacji dry-run:
# python de_gu_bauunternehmen_scraper.py --send-emails-only --ignore-send-window
```

## Wyniki

| Plik | Opis |
|------|------|
| `Wyniki/de_gu_bauunternehmen_cache.json` | Cache Serper + kontakty |
| `Wyniki/de_gu_bauunternehmen_kontakte.xlsx` | Excel — arkusz Kontakte (4 kolumny) + Szczegoly + Info |
| `Wyniki/pl_wojewodztwa_rotation.json` | Stan rotacji województw |
| `wyslane/` | Kopie wysłanych maili (.eml) |

Upload Drive (OAuth / service account z env, nie commituj `secrets/`):

```powershell
python scripts\gdrive_upload_wyniki.py --campaign-dir . --dry-run
# prawdziwy upload tylko po Twoim potwierdzeniu (wymaga GDRIVE_OAUTH_* albo service account)
```

## Sekrety (GHA i lokalnie)

| Zmienna | Wymagana | Opis |
|---------|----------|------|
| `SERPER_API_KEY` | discovery | Serper |
| `ANTHROPIC_API_KEY` / `CLAUDE_API_KEY` | verify + maile Claude | Anthropic (proces, `.env` albo PowerShell User) |
| `MAIL_USER` / `MAIL_PASSWORD` | send | Gmail `hurtmatbud2@gmail.com`; hasło: `MAIL_PASSWORD` albo PowerShell User `GMAIL_APP_PASSWORD` |
| `GDRIVE_OAUTH_*` albo `GDRIVE_SERVICE_ACCOUNT_JSON` / `_FILE` | upload Drive | OAuth / konto usługi (proces, `.env` albo PowerShell User) |

`.env` jest w `.gitignore`. Nie wpisuj haseł do plików źródłowych.

Szczegóły: [`docs/GITHUB_ACTIONS.md`](docs/GITHUB_ACTIONS.md), [`docs/GOOGLE_DRIVE.md`](docs/GOOGLE_DRIVE.md), [`schedule/PLAN_5_DNI.md`](schedule/PLAN_5_DNI.md)
