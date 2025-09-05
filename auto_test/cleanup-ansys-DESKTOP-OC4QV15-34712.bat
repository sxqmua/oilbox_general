@echo off
set LOCALHOST=%COMPUTERNAME%
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 41164)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 40108)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 40840)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 34712)

del /F cleanup-ansys-DESKTOP-OC4QV15-34712.bat
