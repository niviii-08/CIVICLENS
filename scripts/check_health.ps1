param(
    [string]$Url = "http://127.0.0.1:5000",
    [int]$Timeout = 5,
    [switch]$Json
)

$ErrorActionPreference = "Continue"

# Check if venv python is valid, else fallback to system python
$pythonCmd = "python"
if (Test-Path ".\venv\Scripts\python.exe") {
    try {
        $testOut = & ".\venv\Scripts\python.exe" --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = ".\venv\Scripts\python.exe"
        }
    } catch {}
}

$scriptPath = Join-Path $PSScriptRoot "check_health.py"
$cmdArgs = @($scriptPath, "--url", $Url, "--timeout", $Timeout)
if ($Json) {
    $cmdArgs += "--json"
}

& $pythonCmd $cmdArgs
exit $LASTEXITCODE

