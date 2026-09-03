#Requires -Version 5.1
<#
Pelna bateria testow: jednostkowe, integracyjne, regresyjne, API live.

  powershell -ExecutionPolicy Bypass -File scripts\RUN_ALL_TESTS.ps1
  powershell -ExecutionPolicy Bypass -File scripts\RUN_ALL_TESTS.ps1 -SkipApiLive
#>
param(
    [switch]$SkipApiLive
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$env:KANBUD_PROJECT_ROOT = Join-Path $Root "libs"
$env:PYTHONUTF8 = "1"
$env:USE_GEMINI_REPLY_INTELLIGENCE = "0"

# Klucze z PowerShell User env (jesli brak w sesji)
foreach ($pair in @(
    @{ Dst = "SERPER_API_KEY"; Src = "SERPER_API_KEY" },
    @{ Dst = "ANTHROPIC_API_KEY"; Src = "ANTHROPIC_API_KEY" },
    @{ Dst = "ANTHROPIC_API_KEY"; Src = "CLAUDE_API_KEY" },
    @{ Dst = "MAIL_USER"; Src = "GMAIL_USER" },
    @{ Dst = "MAIL_PASSWORD"; Src = "GMAIL_APP_PASSWORD" },
    @{ Dst = "GDRIVE_OAUTH_CLIENT_ID"; Src = "GDRIVE_OAUTH_CLIENT_ID" },
    @{ Dst = "GDRIVE_OAUTH_CLIENT_SECRET"; Src = "GDRIVE_OAUTH_CLIENT_SECRET" },
    @{ Dst = "GDRIVE_OAUTH_REFRESH_TOKEN"; Src = "GDRIVE_OAUTH_REFRESH_TOKEN" },
    @{ Dst = "GDRIVE_SERVICE_ACCOUNT_JSON"; Src = "GDRIVE_SERVICE_ACCOUNT_JSON" },
    @{ Dst = "GDRIVE_SERVICE_ACCOUNT_FILE"; Src = "GDRIVE_SERVICE_ACCOUNT_FILE" },
    @{ Dst = "GDRIVE_SERVICE_ACCOUNT_FILE"; Src = "GOOGLE_APPLICATION_CREDENTIALS" }
)) {
    if (-not (Get-Item -Path "Env:$($pair.Dst)" -ErrorAction SilentlyContinue)) {
        $val = [Environment]::GetEnvironmentVariable($pair.Src, "User")
        if ($val) { Set-Item -Path "Env:$($pair.Dst)" -Value $val }
    }
}

$failed = @()
$passed = @()

function Test-Step {
    param([string]$Name, [scriptblock]$Block)
    Write-Host "`n>> $Name" -ForegroundColor Cyan
    try {
        & $Block
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "exit $LASTEXITCODE" }
        $script:passed += $Name
        Write-Host "OK: $Name" -ForegroundColor Green
    } catch {
        $script:failed += "${Name}: $_"
        Write-Host "FAIL: $Name - $_" -ForegroundColor Red
    }
}

Test-Step "py_compile (wszystkie .py)" {
    Get-ChildItem -Recurse -Filter *.py |
        Where-Object { $_.FullName -notmatch '\\\.venv\\' } |
        ForEach-Object {
            python -m py_compile $_.FullName
            if ($LASTEXITCODE -ne 0) { throw $_.FullName }
        }
}

Test-Step "pytest: jednostkowe (unit)" {
    python -m pytest tests/unit -m unit -v --tb=short
}

Test-Step "pytest: integracyjne (bez api_live)" {
    python -m pytest tests/integration -m "integration and not api_live" -v --tb=short
}

Test-Step "regresja discovery GU (unittest)" {
    python -m unittest tests.test_gu_discovery_regression -v
}

Test-Step "regresja Excel append + Gmail (unittest)" {
    python -m unittest tests.test_excel_append tests.test_send_excel_gmail tests.test_claude_prompts -v
}

Test-Step "smoke scraper (--test)" {
    python de_gu_bauunternehmen_scraper.py --test
}

Test-Step "send_excel_gmail --dry-run (jesli jest Excel)" {
    if (Test-Path "Wyniki\de_gu_bauunternehmen_kontakte.xlsx") {
        python scripts/send_excel_gmail.py --dry-run
    } else {
        Write-Host "(pominieto - brak Wyniki\de_gu_bauunternehmen_kontakte.xlsx)" -ForegroundColor Yellow
    }
}

if (-not $SkipApiLive) {
    Test-Step "pytest: API live (Serper + Anthropic)" {
        python -m pytest tests/integration/test_api_keys.py -m api_live -v --tb=short
    }
} else {
    Write-Host "`n>> API live - pominieto (-SkipApiLive)" -ForegroundColor Yellow
}

Write-Host "`n======== PODSUMOWANIE ========" -ForegroundColor Yellow
Write-Host "Passed: $($passed.Count)"
$passed | ForEach-Object { Write-Host "  + $_" }
if ($failed.Count) {
    Write-Host "Failed: $($failed.Count)" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" }
    exit 1
}
Write-Host "Wszystkie testy OK" -ForegroundColor Green
