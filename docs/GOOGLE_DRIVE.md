# Google Drive — wyniki kampanii PL→DE (Hurt Matbud)

Folder w chmurze: [PL firmy w DE](https://drive.google.com/drive/folders/1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ)

ID folderu: `1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ`

## Co trafia na Drive

| Plik / folder | Opis |
|---------------|------|
| `de_gu_bauunternehmen_cache.json` | Cache |
| `de_gu_bauunternehmen_kontakte.xlsx` | Excel (Kontakte: 4 kolumny; Szczegoly; Info) |
| `de_gu_bauunternehmen_scraper.log` | Log |
| `pl_wojewodztwa_rotation.json` | Rotacja województw |
| `wyslane/*.eml` | Kopie wysłanych maili |

Folder może być **pusty** przed pierwszym uruchomieniem scrapera — pliki powstają automatycznie.

## Sposoby uploadu

| Sposób | Kiedy |
|--------|--------|
| **GitHub Actions** | Workflow `Sync wyniki Google Drive` (poniedziałek 03:00 PL / ręcznie) |
| **Lokalnie** | `python scripts/gdrive_upload_wyniki.py --campaign-dir .` (`--dry-run` bez uploadu) |
| **Lokalnie — tylko Excel końcowy** | `python scripts/gdrive_upload_wyniki.py --campaign-dir . --only-final-excel` |
| **PC + Drive for desktop** | Zmienna `KANBUD_GOOGLE_DRIVE_GU_PATH` → zapis na bieżąco |

### Upload z GitHub Actions (OAuth — zalecane przy folderze na „Moim dysku”)

Konto usługowe **nie może** zapisywać plików do zwykłego udostępnionego folderu. Jednorazowo na PC:

```powershell
pip install -r requirements-drive.txt
# OAuth Desktop client JSON → secrets\gdrive-oauth-client.json
python scripts/gdrive_oauth_setup.py
```

Skrypt ustawi secrets `GDRIVE_OAUTH_*` i uruchomi sync. Kolejne runy CI uploadują na folder `1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ`.

## Stała reguła sync (GitHub Actions)

| Reguła | Wartość |
|--------|---------|
| **Kiedy** | **Poniedziałek 03:00** (Europe/Warsaw); ręcznie: `gh workflow run "Sync wyniki Google Drive"` |
| **Cron** | `0 3 * * 1` (Europe/Warsaw) |
| **Źródło danych** | Artefakt **`de-gu-wyniki-thu`** (niedzielny backfill) |
| **Kolejność fallback** | `thu` → `mon` → `tue` → `fri` |
| **Trigger** | Tylko `schedule` + `workflow_dispatch` |

Maile Hurt Matbud **nie** wymagają załącznika PPTX (`DISABLE_EMAIL_ATTACHMENT=1`).

## Tylko finalny Excel

Jeśli chcesz wysyłać na Drive wyłącznie końcowy plik kontaktów:

```powershell
python scripts/gdrive_upload_wyniki.py --campaign-dir . --only-final-excel
```

Skrypt wybiera `Wyniki/de_gu_bauunternehmen_kontakte.xlsx` (fallback: najnowszy `.xlsx` w `Wyniki/`).

## Typowy powód błędu sync w GHA

Jeśli workflow `Sync wyniki Google Drive` pada z `Brak plikow do wyslania (puste Wyniki/)`,
to znaczy, że nie było świeżego artefaktu (`de-gu-wyniki-thu` → `wed` → `mon` → `tue` → `fri`)
i repo na runnerze nie miało lokalnych plików `Wyniki/`.

## Konto usługi Google (jednorazowo)

1. [Google Cloud Console](https://console.cloud.google.com/) → projekt → włącz **Google Drive API**.
2. **Administracja → Konta usługi** → utwórz konto → **Klucze** → **JSON**.
3. **Nie używaj** klucza API (`AIza...`) — potrzebny jest **plik JSON** z `type: service_account`.
4. **GitHub Actions:** konto usługowe **nie ma własnej przestrzeni** na „Moim dysku”.
   - Użyj **OAuth** (`GDRIVE_OAUTH_*`) dla folderu na Moim dysku **albo** Shared Drive + konto usługi.
   - Opcjonalnie: secret **`GDRIVE_SHARED_DRIVE_ID`**.
   - Alternatywa (Workspace): delegacja domeny + secret **`GDRIVE_IMPERSONATE_EMAIL`**.
5. GitHub: secret **`GDRIVE_SERVICE_ACCOUNT_JSON`** = treść JSON **albo** OAuth Desktop.

## Zmienne środowiskowe

| Zmienna | Opis |
|---------|------|
| `GDRIVE_SERVICE_ACCOUNT_JSON` | Treść JSON (GitHub Actions / env) |
| `GDRIVE_SERVICE_ACCOUNT_FILE` | Ścieżka do pliku JSON (lokalnie) |
| `GDRIVE_OAUTH_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` | OAuth Desktop (My Drive) |
| `GDRIVE_FOLDER_ID` | Domyślnie `1LdIQi0t1fgQMlHwNnvMdPn5lyv1zOqIJ` |
| `GDRIVE_SHARED_DRIVE_ID` | ID dysku współdzielonego (opcjonalnie) |
| `GDRIVE_IMPERSONATE_EMAIL` | E-mail użytkownika Workspace (opcjonalnie) |
| `KANBUD_GOOGLE_DRIVE_GU_PATH` | Lokalna ścieżka Drive for desktop |
