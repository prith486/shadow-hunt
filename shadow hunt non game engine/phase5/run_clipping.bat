@echo off
title Phase 5: Polygon and Line Clipping Visualizer
echo ============================================================
echo   PHASE 5: ADVANCED POLYGON & LINE CLIPPING VISUALIZER
echo   - Sutherland-Hodgman Polygon Clipping
echo   - Cohen-Sutherland Line Clipping & Outcodes
echo   - Interactive Custom Polygon & Window Input
echo ============================================================
echo.
cd /d "%~dp0"
py main_clipping.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Runner encountered an issue.
    pause
)
