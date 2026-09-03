# GitHub Actions — kampania PL→DE (Hurt Matbud)

Repozytorium: [wyszukiwarka-partnerow-Polska](https://github.com/Bigmax1993/wyszukiwarka-partnerow-Polska)

## Workflowy

| Workflow | Plik | Trigger | Co robi |
|----------|------|---------|---------|
| **Tests** | `tests.yml` | push, PR | pytest unit + integracja + regresja + API live |
| **CI Deploy** | `ci-deploy.yml` | push | smoke + walidacja secretów + dry-run maili |
| **Discovery** | `de_gu_pi.yml` | cron, ręcznie | Discovery pon–pt → `de-gu-wyniki-pi` |
| **Niedziela backfill** | `de_gu_thu.yml` | cron, ręcznie | Backfill + Excel → `de-gu-wyniki-thu` |
| **Poniedziałek prep** | `de_gu_mon.yml` | cron, ręcznie | Rebuild Excel → `de-gu-wyniki-mon` |
| **Poniedziałek excel email** | `de_gu_mon_excel_email.yml` | cron, ręcznie | Excel na Gmail (05:00 PL) |
| **Poniedziałek send** | `de_gu_tue.yml` | cron, ręcznie | Wysyłka Hurt Matbud (max 20) → `de-gu-wyniki-tue` |
| **Wtorek send** | `de_gu_fri.yml` | cron, ręcznie | Kolejna partia (max 20) → `de-gu-wyniki-fri` |
| **Sync Google Drive** | `sync-google-drive.yml` | cron pon 03:00 PL, ręcznie | Upload `Wyniki/` na Drive `1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ` |

## Harmonogram cron (Europe/Warsaw)

`gu-gha-window-guard` zwraca `active=true` (brak martwego okna dat).

| Dzień | Workflow | Cron | Godzina PL |
|-------|----------|------|------------|
| **Pon–pt** | discovery | `0 18 * * 1-5` | **18:00** |
| **Niedziela** | backfill | `0 3 * * 0` | **03:00** |
| **Poniedziałek** | sync Drive | `0 3 * * 1` | **03:00** |
| **Poniedziałek** | prep | `30 4 * * 1` | **04:30** |
| **Poniedziałek** | excel email | `0 5 * * 1` | **05:00** |
| **Poniedziałek** | send 1 | `30 6 * * 1` | **06:30** |
| **Wtorek** | send 2 | `30 6 * * 2` | **06:30** |

Workflowy send: Gmail `smtp.gmail.com:465`, `DISABLE_EMAIL_ATTACHMENT=1`, `MAX_SEND_PER_RUN=20`. Najpierw lokalnie `--dry-run-email`.

## Sekrety (repo GitHub, nie hardcode)

| Secret | Wymagany | Opis |
|--------|----------|------|
| `SERPER_API_KEY` | discovery | API Serper |
| `ANTHROPIC_API_KEY` | discovery + backfill + maile Claude | Anthropic |
| `MAIL_USER` | send | `hurtmatbud2@gmail.com` |
| `MAIL_PASSWORD` | send | hasło aplikacji Gmail (nie zwykłe hasło) |
| `GDRIVE_OAUTH_CLIENT_ID` | sync Drive (My Drive) | OAuth Desktop |
| `GDRIVE_OAUTH_CLIENT_SECRET` | sync Drive | OAuth |
| `GDRIVE_OAUTH_REFRESH_TOKEN` | sync Drive | OAuth |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | sync Drive (Shared Drive) | JSON konta usługi (alternatywa dla OAuth) |

Modele Claude (opcjonalnie env):

| Zadanie | Tier | Domyślny model | Env |
|---------|------|----------------|-----|
| Frazy Serper, cleanup Excel | `fast` | `claude-haiku-4-5` | `CLAUDE_MODEL_FAST` |
| Weryfikacja www, treść maila | `verify` | `claude-sonnet-4-6` | `CLAUDE_MODEL_VERIFY` |

Setup OAuth Drive: `python scripts/gdrive_oauth_setup.py` — [`GOOGLE_DRIVE.md`](GOOGLE_DRIVE.md).

## Artifacty

```
pon→pi | wt→pi | sro→pi | czw→pi | pt→pi → niedziela→thu → sync Drive → pon prep→mon → pon send→tue → wt send→fri
```

**Sync Drive** (pon 03:00 PL) pobiera **`de-gu-wyniki-thu`**. Folder: `1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ`.

Maile **bez** PPTX MFG.

## Ręczne uruchomienie

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_full_pipeline_gha.ps1 -ForceResend
```

```powershell
gh workflow run "GU discovery" -R Bigmax1993/wyszukiwarka-partnerow-Polska
gh workflow run "GU discovery" -R Bigmax1993/wyszukiwarka-partnerow-Polska -f discovery_phase=mon
gh workflow run "GU niedziela backfill" -R Bigmax1993/wyszukiwarka-partnerow-Polska
gh workflow run "Sync wyniki Google Drive" -R Bigmax1993/wyszukiwarka-partnerow-Polska
gh workflow run "GU poniedzialek excel email" -R Bigmax1993/wyszukiwarka-partnerow-Polska -f dry_run=true
gh workflow run "GU poniedzialek send" -R Bigmax1993/wyszukiwarka-partnerow-Polska
```

Kolejność: discovery (pon–pt) → backfill → sync Drive → prep → send. Najpierw dry-run maili lokalnie.
