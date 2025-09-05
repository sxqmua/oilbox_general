@echo off
set LOCALHOST=%COMPUTERNAME%
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 34864)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 22696)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 27448)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 38992)

del /F cleanup-ansys-DESKTOP-OC4QV15-38992.bat
