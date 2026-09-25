# Requires PowerShell 5.1+ and Python 3.11+.
$ErrorActionPreference = 'Stop'
$TaskScript = Join-Path $PSScriptRoot 'src/prompt_engineerer/bootstrap.py'
foreach ($TaskCommand in @('py', 'python', 'python3')) {
    if (Get-Command $TaskCommand -ErrorAction SilentlyContinue) {
        $TaskPrefix = @()
        if ($TaskCommand -eq 'py') { $TaskPrefix = @('-3') }
        & $TaskCommand @TaskPrefix -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>$null
        if ($LASTEXITCODE -eq 0) {
            & $TaskCommand @TaskPrefix $TaskScript @args
            exit $LASTEXITCODE
        }
    }
}
Write-Error 'Instale Python 3.11+ (com venv/pip), adicione ao PATH e tente novamente.'
exit 1
