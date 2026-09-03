# Plan tygodniowy: poniedziałek–piątek discovery → niedziela → poniedziałek → wtorek

Jeden **obrót** na **jedno województwo PL** na tydzień (`--rotate-wojewodztwo`).
Wysyłka B2B: max **20** maili na run (`MAX_SEND_PER_RUN`), Gmail `hurtmatbud2@gmail.com`.
Najpierw zawsze `--dry-run-email --send-emails-only`.

## Cykl tygodniowy

```
Tydzień N (discovery):
  pon–pt 18:00   [de-gu-wyniki-pi]

Tydzień N (przetwarzanie + wysyłka poprzedniej fali):
  nd 03:00 backfill → pon 03:00 sync Drive → pon 04:30 prep → pon 05:00 excel email → pon 06:30 send → wt 06:30 send
```

**Poniedziałek ma dwa tryby:** noc/ranek (03–06:30) kończy poprzednią falę (Drive → wysyłka), wieczorem (18:00) startuje **nowy** tydzień discovery (cache z `fri`).

## Tabela harmonogramu

| Dzień | Godzina (PL) | Skrypt PC | GitHub Actions |
|-------|--------------|-----------|----------------|
| **Poniedziałek** | **18:00** | `run_poniedzialek_discovery.ps1` | `GU discovery` (faza mon) |
| **Wtorek** | **18:00** | `run_wtorek_discovery.ps1` | `GU discovery` (faza tue) |
| **Środa** | **18:00** | `run_sroda_discovery.ps1` | `GU discovery` (faza wed) |
| **Czwartek** | **18:00** | `run_czwartek_discovery.ps1` | `GU discovery` (faza thu) |
| **Piątek** | **18:00** | `run_piatek_discovery.ps1` | `GU discovery` (faza fri) |
| **Niedziela** | **03:00** | `run_czwartek.ps1` | `GU niedziela backfill` |
| **Poniedziałek** | **03:00** | — | `Sync wyniki Google Drive` |
| **Poniedziałek** | **04:30** | `run_poniedzialek_prep.ps1` | `GU poniedzialek prep` |
| **Poniedziałek** | **05:00** | — | `GU poniedzialek excel email` |
| **Poniedziałek** | **06:30** | `run_poniedzialek_send.ps1` | `GU poniedzialek send` (partia 1) |
| **Wtorek** | **06:30** | `run_wtorek.ps1` | `GU wtorek send` (partia 2) |

| Dzień | Co robi |
|-------|---------|
| **Poniedziałek 18:00** | Discovery część 1 — nowy tydzień, cache z `fri` → `de-gu-wyniki-pi` |
| **Wtorek 18:00** | Discovery część 2 — `--respect-cache` |
| **Środa 18:00** | Discovery część 3 — `--respect-cache` |
| **Czwartek 18:00** | Discovery część 4 — `--respect-cache` |
| **Piątek 18:00** | Discovery część 5 — `--respect-cache`, domknięcie tygodnia |
| **Niedziela 03:00** | Verify www + backfill e-maili + Excel (`de-gu-wyniki-thu`) z piątkowego `pi` |
| **Poniedziałek 03:00** | Upload Excel na Drive (artefakt `thu`) |
| **Poniedziałek 04:30** | Rebuild Excel z cache (`de-gu-wyniki-mon`), **bez wysyłki** |
| **Poniedziałek 05:00** | Excel na `svinchak1993@gmail.com` |
| **Poniedziałek 06:30** | Wysyłka Hurt Matbud (max **20** / run, `MAX_SEND_PER_RUN`) |
| **Wtorek 06:30** | Kolejna partia (też max **20** / run), tylko po OK dry-run |

## Task Scheduler (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File "schedule\register_tasks_5_dni.ps1"
```

## GitHub Actions — artefakty

```
pon→pi | wt→pi | sro→pi | czw→pi | pt→pi → niedziela→thu → sync Drive → pon prep→mon → pon send→tue → wt send→fri
```

| Workflow | Plik | Cron (Europe/Warsaw) |
|----------|------|----------------------|
| discovery | `de_gu_pi.yml` | `0 18 * * 1-5` **pon–pt 18:00** |
| backfill | `de_gu_thu.yml` | `0 3 * * 0` → **03:00** niedziela |
| sync Drive | `sync-google-drive.yml` | `0 3 * * 1` → **03:00** poniedziałek |
| prep | `de_gu_mon.yml` | `30 4 * * 1` → **04:30** poniedziałek |
| excel email | `de_gu_mon_excel_email.yml` | `0 5 * * 1` → **05:00** poniedziałek |
| send 1 | `de_gu_tue.yml` | `30 6 * * 1` → **06:30** poniedziałek |
| send 2 | `de_gu_fri.yml` | `30 6 * * 2` → **06:30** wtorek |

**Sync Drive:** pon 03:00 PL, artefakt **`thu`** (backfill); fallback: `mon` → `tue` → `fri`.

**Wznowienie discovery:** `gh workflow run "GU discovery" -R Bigmax1993/wyszukiwarka-partnerow-Polska -f resume_artifact_run_id=RUN_ID`

**Pełny cykl discovery (test):** `-f discovery_phase=mon`, potem `tue`, `wed`, `thu`, `fri`.

**Pełny pipeline po piątku (GHA):**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_full_pipeline_gha.ps1 -SkipDiscovery
```

**Czekaj na discovery i kontynuuj:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\resume_pipeline_after_pi.ps1 -PiRunId RUN_ID
```
