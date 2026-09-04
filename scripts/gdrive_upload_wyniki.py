# -*- coding: utf-8 -*-
"""
Upload folderu Wyniki/ (+ opcjonalnie wyslane/) do Google Drive.

Konto usługowe nie ma własnej przestrzeni dyskowej — pliki muszą trafić na
Shared Drive (dysk zespołowy) albo upload w imieniu użytkownika (delegacja DWD).

Zmienne:
  GDRIVE_SERVICE_ACCOUNT_JSON / GDRIVE_SERVICE_ACCOUNT_FILE
  GDRIVE_FOLDER_ID — docelowy folder (domyślnie GU Bauunternehmen)
  GDRIVE_SHARED_DRIVE_ID — opcjonalnie ID dysku współdzielonego (auto-wykrywanie, jeśli puste)
  GDRIVE_IMPERSONATE_EMAIL — opcjonalnie e-mail użytkownika Workspace (domain-wide delegation)
  GDRIVE_VERSION_XLSX — 1 (domyślnie): każdy .xlsx jako nowy plik z datą, bez nadpisywania
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_LIBS = ROOT / "libs"
for _p in (ROOT, _LIBS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from campaign_data_paths import (  # noqa: E402
    GOOGLE_DRIVE_GU_FOLDER_ID,
    resolve_data_root,
    wyniki_dir,
    wyslane_dir,
)
from scraper_env import get_env_value  # noqa: E402

# Pełny dostęp do Drive (wymagany dla Shared Drive i nadpisywania plików).
SCOPES = ("https://www.googleapis.com/auth/drive",)


def _gdrive_env(name: str, default: str = "") -> str:
    """GDRIVE_* z procesu albo PowerShell User/Machine (bez logowania wartości)."""
    return get_env_value(name) or default

_DRIVE_API_OPTS = {
    "supportsAllDrives": True,
    "supportsTeamDrives": True,
}
_LIST_OPTS = {
    **_DRIVE_API_OPTS,
    "includeItemsFromAllDrives": True,
}

_GU_FOLDER_NAME = "GU Bauunternehmen Wyniki"


def _gdrive_version_xlsx_enabled() -> bool:
    raw = (os.environ.get("GDRIVE_VERSION_XLSX") or "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def _upload_stamp() -> str:
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(os.environ.get("SCRAPER_TIMEZONE", "Europe/Warsaw"))
        return datetime.now(tz).strftime("%Y-%m-%d_%H%M")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d_%H%M")


def versioned_xlsx_upload_name(filename: str, *, stamp: str | None = None) -> str:
    """de_gu_bauunternehmen_kontakte.xlsx → de_gu_bauunternehmen_kontakte_2026-06-08_1405.xlsx"""
    path = Path(filename)
    if path.suffix.lower() != ".xlsx":
        return path.name
    tag = stamp or _upload_stamp()
    return f"{path.stem}_{tag}{path.suffix}"


def _load_oauth_credentials():
    refresh = _gdrive_env("GDRIVE_OAUTH_REFRESH_TOKEN")
    if not refresh:
        return None
    client_id = _gdrive_env("GDRIVE_OAUTH_CLIENT_ID")
    client_secret = _gdrive_env("GDRIVE_OAUTH_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit(
            "Ustaw GDRIVE_OAUTH_CLIENT_ID i GDRIVE_OAUTH_CLIENT_SECRET "
            "(uruchom scripts/gdrive_oauth_setup.py)."
        )
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError as e:
        raise SystemExit("pip install google-auth\n" + str(e)) from e

    creds = Credentials(
        token=None,
        refresh_token=refresh,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=list(SCOPES),
    )
    creds.refresh(Request())
    return creds


def _load_service_account_credentials():
    try:
        from google.oauth2 import service_account
    except ImportError as e:
        raise SystemExit(
            "Zainstaluj: pip install google-api-python-client google-auth\n" + str(e)
        ) from e

    raw = _gdrive_env("GDRIVE_SERVICE_ACCOUNT_JSON")
    path = _gdrive_env("GDRIVE_SERVICE_ACCOUNT_FILE")
    if raw:
        if raw.startswith("AIza"):
            raise SystemExit(
                "GDRIVE_SERVICE_ACCOUNT_JSON wyglada na klucz API (AIza...). "
                "Wklej caly plik JSON z Konta uslugi -> Klucze (type=service_account)."
            )
        try:
            info = json.loads(raw)
        except json.JSONDecodeError as e:
            raise SystemExit(
                f"GDRIVE_SERVICE_ACCOUNT_JSON nie jest poprawnym JSON: {e}. "
                "W GitHub Secrets wklej cala tresc pobranego pliku .json."
            ) from e
        if info.get("type") != "service_account" or not info.get("client_email"):
            raise SystemExit(
                "JSON musi byc kluczem konta uslugowego (type=service_account, client_email)."
            )
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    elif path and Path(path).is_file():
        creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    else:
        raise SystemExit(
            "Ustaw GDRIVE_SERVICE_ACCOUNT_JSON (treść) lub GDRIVE_SERVICE_ACCOUNT_FILE (ścieżka)."
        )

    impersonate = _gdrive_env("GDRIVE_IMPERSONATE_EMAIL")
    if impersonate:
        creds = creds.with_subject(impersonate)
        print(f"Delegacja DWD: upload w imieniu {impersonate}")
    return creds


def _load_credentials():
    oauth = _load_oauth_credentials()
    if oauth is not None:
        print("OAuth: upload na Twoj Dysk Google (folder udostepniony uzytkownikowi)")
        return oauth, True
    return _load_service_account_credentials(), False


def _drive_service(creds):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return service, MediaFileUpload


def _folder_metadata(service, folder_id: str) -> dict:
    return (
        service.files()
        .get(
            fileId=folder_id,
            fields="id,name,driveId,mimeType,parents",
            **_DRIVE_API_OPTS,
        )
        .execute()
    )


def _list_shared_drives(service) -> list[dict]:
    drives: list[dict] = []
    page_token = None
    while True:
        res = (
            service.drives()
            .list(pageSize=100, pageToken=page_token, fields="nextPageToken,drives(id,name)")
            .execute()
        )
        drives.extend(res.get("drives") or [])
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return drives


def _find_folder_in_parent(service, parent_id: str, name: str) -> str | None:
    safe_name = name.replace("'", "\\'")
    q = (
        f"'{parent_id}' in parents and name = '{safe_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    res = (
        service.files()
        .list(q=q, fields="files(id)", pageSize=1, corpora="allDrives", **_LIST_OPTS)
        .execute()
    )
    files = res.get("files") or []
    return files[0]["id"] if files else None


def _create_folder(service, parent_id: str, name: str, *, drive_id: str | None = None) -> str:
    meta: dict = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    if drive_id:
        meta["driveId"] = drive_id
    created = service.files().create(body=meta, fields="id", **_DRIVE_API_OPTS).execute()
    return created["id"]


def _resolve_shared_drive_upload_folder(service, preferred_folder_id: str) -> tuple[str, str]:
    """
    Zwraca (folder_id, shared_drive_id) do uploadu na Shared Drive.
    """
    configured_drive = _gdrive_env("GDRIVE_SHARED_DRIVE_ID")
    drives = _list_shared_drives(service)
    if configured_drive:
        drive_ids = {d["id"] for d in drives}
        if configured_drive not in drive_ids and drives:
            print(
                f"Uwaga: GDRIVE_SHARED_DRIVE_ID={configured_drive} niedostepny; "
                f"uzywam {drives[0]['name']}"
            )
            shared_drive_id = drives[0]["id"]
        elif configured_drive in drive_ids or not drives:
            shared_drive_id = configured_drive
        else:
            raise SystemExit(
                "Brak dostepnych Shared Drives dla konta uslugowego. "
                "Dodaj je jako czlonka dysku wspoldzielonego (Content manager)."
            )
    elif drives:
        shared_drive_id = drives[0]["id"]
        print(f"Shared Drive: {drives[0].get('name', shared_drive_id)}")
    else:
        raise SystemExit(
            "Konto uslugowe nie widzi zadnego Shared Drive.\n"
            "Najprosciej: uruchom na PC  python scripts/gdrive_oauth_setup.py\n"
            "(OAuth na Twoj folder — bez Shared Drive).\n"
            "Albo: dysk wspoldzielony + e-mail konta uslugowego jako Content manager."
        )

    try:
        meta = _folder_metadata(service, preferred_folder_id)
        if meta.get("driveId"):
            print(f"Folder docelowy jest na Shared Drive: {meta.get('name', preferred_folder_id)}")
            return preferred_folder_id, meta["driveId"]
    except Exception:
        pass

    existing = _find_folder_in_parent(service, shared_drive_id, _GU_FOLDER_NAME)
    if existing:
        print(f"Uzywam folderu na Shared Drive: {_GU_FOLDER_NAME} ({existing})")
        return existing, shared_drive_id

    created = _create_folder(
        service, shared_drive_id, _GU_FOLDER_NAME, drive_id=shared_drive_id
    )
    print(f"Utworzono folder na Shared Drive: {_GU_FOLDER_NAME} ({created})")
    return created, shared_drive_id


def _resolve_upload_folder(service, folder_id: str, *, use_oauth: bool) -> str:
    """Ustal folder, do którego można uploadować (OAuth / Shared Drive / impersonacja)."""
    if use_oauth:
        print(f"OAuth -> folder {folder_id}")
        return folder_id
    try:
        meta = _folder_metadata(service, folder_id)
        if meta.get("driveId"):
            print(f"Upload na Shared Drive (folder: {meta.get('name', folder_id)})")
            return folder_id
    except Exception as exc:
        print(f"Nie mozna odczytac folderu {folder_id}: {exc}")

    if _gdrive_env("GDRIVE_IMPERSONATE_EMAIL"):
        print(f"Upload przez delegacje do folderu {folder_id}")
        return folder_id

    print(
        "Folder jest na 'Moim dysku' — konto uslugowe nie moze tam zapisywac plikow. "
        "Przelaczam na Shared Drive..."
    )
    upload_id, _drive = _resolve_shared_drive_upload_folder(service, folder_id)
    return upload_id


def _find_or_create_folder(service, parent_id: str, name: str) -> str:
    existing = _find_folder_in_parent(service, parent_id, name)
    if existing:
        return existing
    return _create_folder(service, parent_id, name)


def _upload_file(
    service,
    MediaFileUpload,
    local: Path,
    parent_id: str,
    *,
    version_xlsx: bool | None = None,
) -> str:
    mime, _ = mimetypes.guess_type(str(local))
    media = MediaFileUpload(str(local), mimetype=mime or "application/octet-stream", resumable=True)
    use_version = _gdrive_version_xlsx_enabled() if version_xlsx is None else version_xlsx
    drive_name = (
        versioned_xlsx_upload_name(local.name)
        if use_version and local.suffix.lower() == ".xlsx"
        else local.name
    )
    if use_version and local.suffix.lower() == ".xlsx":
        body = {"name": drive_name, "parents": [parent_id]}
        created = (
            service.files()
            .create(body=body, media_body=media, fields="id", **_DRIVE_API_OPTS)
            .execute()
        )
        return created["id"]

    safe_name = drive_name.replace("'", "\\'")
    q = f"'{parent_id}' in parents and name = '{safe_name}' and trashed = false"
    existing = (
        service.files()
        .list(q=q, fields="files(id)", pageSize=1, corpora="allDrives", **_LIST_OPTS)
        .execute()
        .get("files")
        or []
    )
    body = {"name": drive_name, "parents": [parent_id]}
    if existing:
        fid = existing[0]["id"]
        service.files().update(fileId=fid, media_body=media, **_DRIVE_API_OPTS).execute()
        return fid
    created = service.files().create(body=body, media_body=media, fields="id", **_DRIVE_API_OPTS).execute()
    return created["id"]


def upload_files_flat(service, MediaFileUpload, local_dir: Path, drive_parent_id: str) -> int:
    if not local_dir.is_dir():
        return 0
    count = 0
    for p in sorted(local_dir.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() == ".xlsx" and _gdrive_version_xlsx_enabled():
            dated = versioned_xlsx_upload_name(p.name)
            _upload_file(service, MediaFileUpload, p, drive_parent_id, version_xlsx=True)
            print(f"  OK {dated}")
            _upload_file(service, MediaFileUpload, p, drive_parent_id, version_xlsx=False)
            print(f"  OK {p.name} (aktualny)")
            count += 1
            continue
        _upload_file(service, MediaFileUpload, p, drive_parent_id)
        print(f"  OK {p.name}")
        count += 1
    return count


def upload_folder_named(
    service, MediaFileUpload, local_dir: Path, drive_parent_id: str, drive_name: str
) -> int:
    if not local_dir.is_dir():
        return 0
    sub_id = _find_or_create_folder(service, drive_parent_id, drive_name)
    count = 0
    for p in sorted(local_dir.iterdir()):
        if p.is_file():
            uploaded_as = (
                versioned_xlsx_upload_name(p.name)
                if _gdrive_version_xlsx_enabled() and p.suffix.lower() == ".xlsx"
                else p.name
            )
            _upload_file(service, MediaFileUpload, p, sub_id)
            print(f"  OK {drive_name}/{uploaded_as}")
            count += 1
    return count


def _list_folder_files(service, parent_id: str) -> list[dict]:
    files: list[dict] = []
    page_token = None
    while True:
        res = (
            service.files()
            .list(
                q=f"'{parent_id}' in parents and trashed = false",
                fields="nextPageToken,files(id,name,mimeType,parents)",
                pageSize=100,
                pageToken=page_token,
                corpora="allDrives",
                **_LIST_OPTS,
            )
            .execute()
        )
        files.extend(res.get("files") or [])
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return files


def _search_kontakte_xlsx_anywhere(service) -> list[dict]:
    """Szuka kontakte*.xlsx na całym Drive (gdy plik nie leży w GDRIVE_FOLDER_ID)."""
    q = (
        "trashed = false and mimeType != 'application/vnd.google-apps.folder' "
        "and (name contains 'de_gu_bauunternehmen_kontakte' "
        "or name contains 'bauunternehmen_kontakte')"
    )
    files: list[dict] = []
    page_token = None
    while True:
        res = (
            service.files()
            .list(
                q=q,
                fields="nextPageToken,files(id,name,mimeType,parents)",
                pageSize=100,
                pageToken=page_token,
                corpora="allDrives",
                **_LIST_OPTS,
            )
            .execute()
        )
        files.extend(res.get("files") or [])
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return files


def _is_kontakte_xlsx_name(name: str) -> bool:
    """de_gu_bauunternehmen_kontakte.xlsx oraz wersje z datą (_YYYY-MM-DD_HHMM)."""
    n = (name or "").strip().lower()
    if not n.endswith(".xlsx"):
        return False
    return n == "de_gu_bauunternehmen_kontakte.xlsx" or n.startswith(
        "de_gu_bauunternehmen_kontakte_"
    )


def delete_kontakte_xlsx_from_drive(
    service,
    folder_id: str,
    *,
    dry_run: bool = False,
) -> int:
    """Usuwa z Drive wszystkie de_gu_bauunternehmen_kontakte*.xlsx (do kosza)."""
    deleted = 0
    listed = _list_folder_files(service, folder_id)
    print(f"Pliki w folderze {folder_id} ({len(listed)}):")
    for item in listed:
        name = item.get("name") or ""
        mime = item.get("mimeType") or ""
        print(f"  - {name} [{mime}]")

    candidates = [
        item
        for item in listed
        if item.get("mimeType") != "application/vnd.google-apps.folder"
        and (
            _is_kontakte_xlsx_name(item.get("name") or "")
            or (
                (item.get("name") or "").lower().endswith(".xlsx")
                and (
                    "kontakte" in (item.get("name") or "").lower()
                    or "bauunternehmen" in (item.get("name") or "").lower()
                )
            )
        )
    ]
    if not candidates:
        print("Brak dopasowania w folderze — szukam na całym Drive…")
        found = _search_kontakte_xlsx_anywhere(service)
        print(f"Wyniki wyszukiwania globalnego ({len(found)}):")
        for item in found:
            print(f"  - {item.get('name')} id={item.get('id')} parents={item.get('parents')}")
        candidates = [
            item
            for item in found
            if (item.get("name") or "").lower().endswith(".xlsx")
        ]

    for item in candidates:
        name = item.get("name") or ""
        fid = item["id"]
        if dry_run:
            print(f"  DRY-RUN delete {name} ({fid})")
        else:
            service.files().update(
                fileId=fid, body={"trashed": True}, **_DRIVE_API_OPTS
            ).execute()
            print(f"  DELETED {name} ({fid})")
        deleted += 1
    return deleted


def _pick_final_excel_file(local_dir: Path) -> Path | None:
    """Wybiera końcowy Excel kontaktów (fallback: najnowszy .xlsx)."""
    if not local_dir.is_dir():
        return None
    preferred = local_dir / "de_gu_bauunternehmen_kontakte.xlsx"
    if preferred.is_file():
        return preferred
    xlsx_files = [p for p in local_dir.iterdir() if p.is_file() and p.suffix.lower() == ".xlsx"]
    if not xlsx_files:
        return None
    return max(xlsx_files, key=lambda p: p.stat().st_mtime)


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload Wyniki do Google Drive")
    parser.add_argument(
        "--campaign-dir",
        type=Path,
        default=ROOT,
        help="Katalog kampanii (do resolve_data_root)",
    )
    parser.add_argument(
        "--folder-id",
        default=_gdrive_env("GDRIVE_FOLDER_ID") or GOOGLE_DRIVE_GU_FOLDER_ID,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tylko pokaż folder i pliki, bez uploadu",
    )
    parser.add_argument(
        "--only-final-excel",
        action="store_true",
        help="Wyślij wyłącznie końcowy plik Excel kontaktów z Wyniki/",
    )
    parser.add_argument(
        "--delete-kontakte-xlsx",
        action="store_true",
        help="Usuń z Drive pliki de_gu_bauunternehmen_kontakte*.xlsx (bez uploadu)",
    )
    args = parser.parse_args()

    if args.dry_run and args.delete_kontakte_xlsx:
        creds, use_oauth = _load_credentials()
        service, _ = _drive_service(creds)
        folder_id = _resolve_upload_folder(service, args.folder_id, use_oauth=use_oauth)
        print(f"DRY-RUN delete kontakte xlsx w folderze {folder_id}")
        n = delete_kontakte_xlsx_from_drive(service, folder_id, dry_run=True)
        print(f"Do usunięcia: {n}")
        return 0

    if args.dry_run:
        data_root = resolve_data_root(args.campaign_dir)
        w = wyniki_dir(data_root)
        print(f"DRY-RUN Drive folder={args.folder_id}")
        print(f"DRY-RUN lokalnie Wyniki={w}")
        if args.only_final_excel:
            picked = _pick_final_excel_file(w)
            if picked is None:
                print("  Brak końcowego pliku .xlsx w Wyniki/")
            else:
                print(f"  ONLY-EXCEL {picked.name}")
        elif w.is_dir():
            for p in sorted(w.iterdir()):
                if p.is_file():
                    print(f"  {p.name}")
        return 0

    creds, use_oauth = _load_credentials()
    service, MediaFileUpload = _drive_service(creds)
    data_root = resolve_data_root(args.campaign_dir)
    upload_folder_id = _resolve_upload_folder(service, args.folder_id, use_oauth=use_oauth)

    if args.delete_kontakte_xlsx:
        print(f"Usuwam de_gu_bauunternehmen_kontakte*.xlsx z Drive {upload_folder_id}")
        n = delete_kontakte_xlsx_from_drive(service, upload_folder_id, dry_run=False)
        print(f"Usunięto: {n}")
        return 0 if n >= 0 else 1

    total = 0
    w = wyniki_dir(data_root)
    if args.only_final_excel:
        picked = _pick_final_excel_file(w)
        if picked is None:
            print("Brak końcowego pliku .xlsx do wysłania (Wyniki/).")
            return 1
        print(f"Upload tylko końcowego Excela: {picked} -> Drive {upload_folder_id}")
        _upload_file(
            service,
            MediaFileUpload,
            picked,
            upload_folder_id,
            version_xlsx=False,
        )
        print(f"  OK {picked.name}")
        total = 1
    elif w.is_dir():
        print(f"Upload plikow z {w} -> Drive {upload_folder_id}")
        total += upload_files_flat(service, MediaFileUpload, w, upload_folder_id)
    s = wyslane_dir(data_root)
    if s.is_dir() and not args.only_final_excel:
        print(f"Upload {s} -> Drive/wyslane/")
        total += upload_folder_named(service, MediaFileUpload, s, upload_folder_id, "wyslane")

    if total == 0:
        print(
            "Brak plikow do wyslania (puste Wyniki/). "
            "Uruchom najpierw pipeline discovery/backfill/send."
        )
        return 1

    print(
        f"Zakonczono. Plikow: {total}. Folder: "
        f"https://drive.google.com/drive/folders/{upload_folder_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
