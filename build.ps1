param(
    [switch]$Console
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "Python bulunamadi. Python 3.14 kurup terminali yeniden acin."
}
$pythonExe = $pythonCommand.Source

$workDirectory = Join-Path $PSScriptRoot "build\pyinstaller"
$distDirectory = Join-Path $PSScriptRoot "dist"
$publicDirectory = Join-Path $PSScriptRoot "public"
$outputExecutable = Join-Path $distDirectory "SDown.exe"
$windowMode = "--windowed"
if ($Console) {
    $windowMode = "--console"
}

Write-Host "[1/2] Python ve derleme araclari kontrol ediliyor..."

$runningApp = Get-Process -Name SDown -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -eq $outputExecutable }
if ($runningApp) {
    $processIds = ($runningApp.Id -join ", ")
    throw "SDown tarayici kapansa bile arka planda calisiyor. Gorev Yoneticisi > Ayrintilar'da bu PID'leri kapatin: $processIds. PowerShell komutu: Stop-Process -Id $processIds -Force"
}

& $pythonExe -c "import PyInstaller, imageio_ffmpeg, yt_dlp"
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller/yt-dlp/FFmpeg paketleri bu Python ortaminda bulunamadi. Calistirin: $pythonExe -m pip install -r requirements-build.txt"
}
& $pythonExe -m PyInstaller --version
if ($LASTEXITCODE -ne 0) { throw "PyInstaller baslatilamadi." }

Write-Host "[2/2] EXE derleniyor. Bu islem birkac dakika surebilir..."
& $pythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    $windowMode `
    --name SDown `
    --add-data "$publicDirectory;public" `
    --collect-all yt_dlp `
    --collect-all imageio_ffmpeg `
    --paths $PSScriptRoot `
    --specpath (Join-Path $PSScriptRoot "build") `
    --workpath $workDirectory `
    --distpath $distDirectory `
    (Join-Path $PSScriptRoot "launcher.py")
if ($LASTEXITCODE -ne 0) {
    throw "EXE olusturulamadi."
}

if (-not (Test-Path -LiteralPath $outputExecutable)) {
    throw "Derleme tamamlandi bildirildi ancak EXE bulunamadi: $outputExecutable"
}

$result = Get-Item -LiteralPath $outputExecutable
Write-Host "Hazir: $($result.FullName) ($([math]::Round($result.Length / 1MB, 1)) MB)"
