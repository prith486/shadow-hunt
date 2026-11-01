@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   STARTING HUNTER ASSASSIN - PHASE 4 (LIVE POLYGON FILL)
echo ============================================================
echo Python-backed GUI with live 4-Connected Boundary Fill Visualizer
echo Controls:
echo   - [WASD] Move operative (coordinates and raster update live)
echo   - Click ANY colored element on the canvas to inspect its live polygon!
echo   - [1-8 / Tab] Switch target:
echo       1: Player Operative
echo       2: Patrol Guard Body
echo       3: Shielded Enforcer Body
echo       4: Enemy Vision Cone
echo       5: Camera Vision Cone
echo       6: Golden Coin
echo       7: MedKit Plus Symbol
echo       8: Extraction Exit Door Pad
echo   - [F]    Slow-Mo Step-by-Step Boundary Fill Demonstration
echo   - [H]    Toggle Hitbox Overlay
echo   - [R]    Restart
echo ============================================================

py main.py
if %ERRORLEVEL% NEQ 0 (
    python main.py
)
pause
