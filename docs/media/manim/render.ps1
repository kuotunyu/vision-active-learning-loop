<#
.SYNOPSIS
Render the README explainer: mp4 (manim) -> GIF (ffmpeg, palette) -> size gate -> copy mp4 to the private evidence root.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Check
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [ValidateSet('h', 'l')][string]$Quality = 'h',
    [ValidateSet('ValLoopShort', 'ValLoopLong')][string]$Scene = 'ValLoopShort',
    [string]$EvidenceMediaDir = '<evidence-root>\media'
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$Project = $PSScriptRoot
$IsLong = ($Scene -eq 'ValLoopLong')
$SceneModule = if ($IsLong) { 'scenes_long' } else { 'scenes_short' }
$OutputStem = if ($IsLong) { 'val-loop-long' } else { 'val-loop-short' }
$SceneFile = Join-Path $Project "val_explainer\$SceneModule.py"
$MediaDir = Join-Path $Project 'media'
$GifOut = Join-Path (Split-Path -Parent $Project) 'val-loop-short.gif'
$MaxGifBytes = 8MB
$MaxSeconds = if ($IsLong) { 130.0 } else { 32.0 }
$env:PYTHONDONTWRITEBYTECODE = '1'

Push-Location $Project
try {
    if ($Check) {
        & uv run python -m manim --dry_run -ql --media_dir $MediaDir $SceneFile $Scene
        if ($LASTEXITCODE -ne 0) { throw "dry run failed ($LASTEXITCODE)" }
        Write-Host "check ok ($Scene dry run; nothing written)"
        exit 0
    }

    & uv run python -m manim "-q$Quality" --media_dir $MediaDir $SceneFile $Scene
    if ($LASTEXITCODE -ne 0) { throw "manim failed ($LASTEXITCODE)" }
    $folder = if ($Quality -eq 'h') { '1080p60' } else { '480p15' }
    $Mp4 = Join-Path $MediaDir "videos\$SceneModule\$folder\$Scene.mp4"
    if (-not (Test-Path -LiteralPath $Mp4)) { throw "expected output missing: $Mp4" }

    $duration = [double](& ffprobe -v error -show_entries format=duration -of csv=p=0 $Mp4)
    Write-Host ("duration {0:N1} s" -f $duration)
    if ($duration -gt $MaxSeconds) { throw "clip is $duration s, longer than $MaxSeconds s" }

    if ($IsLong) {
        # portfolio video: mp4 only, no GIF, never committed
        if (-not (Test-Path -LiteralPath $EvidenceMediaDir)) { New-Item -ItemType Directory -Path $EvidenceMediaDir | Out-Null }
        $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmZ')
        $dest = Join-Path $EvidenceMediaDir "$OutputStem-$stamp.mp4"
        Copy-Item -LiteralPath $Mp4 -Destination $dest
        Write-Host "mp4  -> $dest"
        exit 0
    }

    $attempts = @(@{ Width = 960; Fps = 12 }, @{ Width = 800; Fps = 10 })
    $tmpGif = Join-Path $MediaDir 'val-loop-short.tmp.gif'
    $palette = Join-Path $MediaDir 'palette.png'
    $ok = $false
    foreach ($a in $attempts) {
        $filters = "fps=$($a.Fps),scale=$($a.Width):-1:flags=lanczos"
        & ffmpeg -y -v error -i $Mp4 -vf "$filters,palettegen=stats_mode=diff" $palette
        if ($LASTEXITCODE -ne 0) { throw 'palettegen failed' }
        & ffmpeg -y -v error -i $Mp4 -i $palette -lavfi "$filters[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" $tmpGif
        if ($LASTEXITCODE -ne 0) { throw 'paletteuse failed' }
        $size = (Get-Item -LiteralPath $tmpGif).Length
        Write-Host ("gif {0}px wide @{1}fps = {2:N1} MB" -f $a.Width, $a.Fps, ($size / 1MB))
        if ($size -le $MaxGifBytes) { $ok = $true; break }
    }
    if (-not $ok) { throw "GIF exceeds $($MaxGifBytes / 1MB) MB at every setting; existing GIF left untouched" }

    Move-Item -LiteralPath $tmpGif -Destination $GifOut -Force
    Remove-Item -LiteralPath $palette -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path -LiteralPath $EvidenceMediaDir)) { New-Item -ItemType Directory -Path $EvidenceMediaDir | Out-Null }
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmZ')
    Copy-Item -LiteralPath $Mp4 -Destination (Join-Path $EvidenceMediaDir "$OutputStem-$stamp.mp4")
    Write-Host "gif  -> $GifOut"
    Write-Host "mp4  -> $EvidenceMediaDir\$OutputStem-$stamp.mp4"
    exit 0
} finally {
    Pop-Location
}
