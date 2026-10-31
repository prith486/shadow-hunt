@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%GodotEngine\Godot_v4.7.2-stable_win64.exe" (
    start "" "%SCRIPT_DIR%GodotEngine\Godot_v4.7.2-stable_win64.exe" --path "%SCRIPT_DIR%HunterAssassinGodot"
) else if exist "%SCRIPT_DIR%..\GodotEngine\Godot_v4.7.2-stable_win64.exe" (
    start "" "%SCRIPT_DIR%..\GodotEngine\Godot_v4.7.2-stable_win64.exe" --path "%SCRIPT_DIR%"
) else (
    echo Error: Godot executable not found.
    pause
)
