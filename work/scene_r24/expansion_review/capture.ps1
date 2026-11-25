param(
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Run,
    [switch]$Sections
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path "$PSScriptRoot/../../..").Path
$game = Join-Path $root 'work/project/chongqing_godot_v05'
$engine = Join-Path $root 'work/tools/godot-4.6.3/Godot_v4.6.3-stable_win64_console.exe'
$folder = Join-Path $root ".cloud-dev/desktop-500/$Run"
if (Test-Path -LiteralPath $folder) { throw "Choose a fresh run name ($folder already exists)" }
New-Item -ItemType Directory -Path $folder | Out-Null
$env:APPDATA = (New-Item -ItemType Directory -Path (Join-Path $folder 'user')).FullName
$script = if ($Sections) { 'edge_profiles.gd' } else { 'fixed_views.gd' }
$render = if ($Sections) { @('--headless') } else { @('--resolution','1152x648','--disable-vsync') }
& $engine @render --path $game --fixed-fps 60 --log-file (Join-Path $folder 'engine.log') --script (Join-Path $PSScriptRoot $script) -- --day-one-test --qa-still-frames "--qa-dir=$($folder.Replace('\','/'))" *> (Join-Path $folder 'console.log')
if ($LASTEXITCODE -ne 0 -or (Select-String -LiteralPath (Join-Path $folder 'engine.log') -Pattern '^(SCRIPT ERROR|SHADER ERROR|ERROR):' -Quiet)) {
    throw "Inspect $folder"
}
Write-Output $folder
