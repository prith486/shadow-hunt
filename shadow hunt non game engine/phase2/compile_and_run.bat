@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   COMPILING HUNTER ASSASSIN - PHASE 2 (C++ PORT)
echo ============================================================
echo [1/5] Compiling core_graphics.cpp ...
g++ -c core_graphics.cpp -o core_graphics.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [2/5] Compiling cg_math.cpp ...
g++ -c cg_math.cpp -o cg_math.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [3/5] Compiling map_engine.cpp ...
g++ -c map_engine.cpp -o map_engine.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [4/5] Compiling entities.cpp ...
g++ -c entities.cpp -o entities.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [5/5] Compiling main.cpp ...
g++ -c main.cpp -o main.o
if %ERRORLEVEL% NEQ 0 goto :failed

echo [*] Linking hunter_assassin_phase2.exe ...
g++ core_graphics.o cg_math.o map_engine.o entities.o main.o -lbgi -lgdi32 -lcomdlg32 -luuid -loleaut32 -lole32 -o hunter_assassin_phase2.exe
if %ERRORLEVEL% NEQ 0 goto :failed

echo.
echo [SUCCESS] Build succeeded! Created hunter_assassin_phase2.exe
echo Starting game...
echo ============================================================
del /q *.o 2>nul
hunter_assassin_phase2.exe
goto :eof

:failed
echo.
echo [ERROR] Build failed! Check compiler output above.
del /q *.o 2>nul
pause
