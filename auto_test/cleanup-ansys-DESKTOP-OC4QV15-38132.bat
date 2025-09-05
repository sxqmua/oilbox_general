@echo off
set LOCALHOST=%COMPUTERNAME%
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 12436)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 35412)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 44732)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 38132)

del /F cleanup-ansys-DESKTOP-OC4QV15-38132.bat
