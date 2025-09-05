@echo off
set LOCALHOST=%COMPUTERNAME%
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 30176)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 37772)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 24880)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 24864)

del /F cleanup-ansys-DESKTOP-OC4QV15-24864.bat
