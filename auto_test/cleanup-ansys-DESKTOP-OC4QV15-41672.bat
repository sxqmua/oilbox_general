@echo off
set LOCALHOST=%COMPUTERNAME%
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 28432)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 40900)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 36844)
if /i "%LOCALHOST%"=="DESKTOP-OC4QV15" (taskkill /f /pid 41672)

del /F cleanup-ansys-DESKTOP-OC4QV15-41672.bat
