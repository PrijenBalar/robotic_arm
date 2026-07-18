@echo off
rem ONE-CLICK ARM STARTUP: hotspot -> backend -> frontend -> browser.
rem Power the Pico before or after running this; it joins the hotspot
rem automatically within ~20 seconds of both being on.
cd /d "%~dp0"

echo =========================================
echo    ARMOBOT - Full System Startup
echo =========================================
echo.

echo [1/4] Starting WiFi hotspot (RoboticArm_PC)...
powershell -ExecutionPolicy Bypass -File "%~dp0start_hotspot.ps1"
if errorlevel 1 (
    echo WARNING: hotspot script failed - check WiFi is connected, then retry.
)

echo.
echo [2/4] Checking port 3000 is free for the backend...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    echo   Port 3000 is used by PID %%p - close that program ^(e.g. GCS dev server^) if the backend fails.
)

echo.
echo [3/4] Starting backend and frontend...
call "%~dp0start_armobot.bat"

echo.
echo [4/4] Waiting for the Pico to appear on the hotspot (up to 30s)...
set FOUND=0
for /l %%i in (1,1,15) do (
    ping -n 1 -w 2000 192.168.137.50 >nul && set FOUND=1 && goto :picodone
)
:picodone
if "%FOUND%"=="1" (
    echo   Pico is ONLINE at 192.168.137.50 - arm ready!
) else (
    echo   Pico not seen yet - make sure it is powered; it can take ~20s more.
)
echo.
echo Dashboard: http://localhost:5173
pause
