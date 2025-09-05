@echo off
set LOCALHOST=%COMPUTERNAME%
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 36608)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 41056)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 39812)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 41716)

del /F cleanup-ansys-DESKTOP-OC4QV15-41716.bat
