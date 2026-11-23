@echo off
chcp 65001 >nul
setlocal
set "taskRoot=%~dp0..\.."
"%taskRoot%\work\tools\godot-4.6.3\Godot_v4.6.3-stable_win64.exe" --path "%taskRoot%\work\project\chongqing_godot_v05" --log-file "%taskRoot%\work\audit\manual_play.log"
if errorlevel 1 pause
endlocal
