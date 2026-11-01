@echo off
title SHADOW HUNT: Phase 5 - 3-Level Tactical Campaign & Live Clipping
echo ============================================================
echo   SHADOW HUNT - 3-LEVEL TACTICAL CAMPAIGN (PHASE 5)
echo   Live Sutherland-Hodgman & Cohen-Sutherland Clipping GUI
echo ============================================================
echo   - Level 1: Facility Infiltration  (2 Enemies, 1 Camera)
echo   - Level 2: Deep Vault Sweep       (4 Enemies, 2 Cameras)
echo   - Level 3: Cyber Citadel Lockdown (6 Enemies, 3 Cameras)
echo.
echo   Controls:
echo   - [WASD] Move Operative (live coordinates and viewport clipping)
echo   - [SPACE / Click] Shoot Laser Bolt (Cohen-Sutherland Line Clipping)
echo   - Click ANY element on the canvas to inspect its clipping live!
echo   - [1 - 8 / Tab] Switch Target to Clip:
echo       1: Player Laser Bolt (Cohen-Sutherland)
echo       2: Enemy Vision Cone (Sutherland-Hodgman)
echo       3: Security Camera Cone (Sutherland-Hodgman)
echo       4: Guard Body Triangle (Sutherland-Hodgman)
echo       5: Enemy Sniper Laser (Cohen-Sutherland)
echo       6: Obstacle Crate Edge (Cohen-Sutherland)
echo       7: Shield Arc Chord (Cohen-Sutherland)
echo       8: Extraction Exit Pad (Sutherland-Hodgman)
echo   - [C] Toggle Method (Sutherland-Hodgman vs Cohen-Sutherland)
echo   - [F] Slow-Mo 4-Stage Clipping Pipeline Demonstration
echo   - [L] or [1, 2, 3] Switch Tactical Campaign Levels
echo   - [R] Replay Level
echo ============================================================
echo.
cd /d "%~dp0"
py main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Game exited with error code.
    pause
)
