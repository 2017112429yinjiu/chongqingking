@echo off
setlocal
set "district=%~dp0project\chongqing_godot_v05"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmssfff"') do set "run=play_%%i_%RANDOM%"
set "report=%district%\verification_r24\first_shift\%run%"
mkdir "%report%"
start "" "%~dp0tools\godot-4.6.3\Godot_v4.6.3-stable_win64.exe" --path "%district%" --script "%~dp0scene_r24\road_and_shift\verify_shift.gd" --log-file "%report%\engine.log" -- --day-one-test --qa-dir=res://verification_r24/first_shift/%run%
