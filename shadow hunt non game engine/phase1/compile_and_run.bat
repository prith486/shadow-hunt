@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   COMPILING HUNTER ASSASSIN - PHASE 1 (C++ PORT)
echo ============================================================
echo [1/4] Compiling core_graphics.cpp ...
g++ -c core_graphics.cpp -o core_graphics.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [2/4] Compiling game_map.cpp ...
g++ -c game_map.cpp -o game_map.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [3/4] Compiling main.cpp ...
g++ -c main.cpp -o main.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [4/4] Linking hunter_assassin_phase1.exe ...
g++ core_graphics.o game_map.o main.o -lbgi -lgdi32 -lcomdlg32 -luuid -loleaut32 -lole32 -o hunter_assassin_phase1.exe
if %ERRORLEVEL% NEQ 0 goto :failed

echo.
echo [SUCCESS] Build succeeded! Created hunter_assassin_phase1.exe
echo Starting game...
echo ============================================================
del /q *.o 2>nul
hunter_assassin_phase1.exe
goto :eof

:failed
echo.
echo [ERROR] Build failed! Check compiler output above.
del /q *.o 2>nul
pause
