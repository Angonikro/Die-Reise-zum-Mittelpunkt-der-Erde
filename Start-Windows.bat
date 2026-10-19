@echo off
cd /d "%~dp0"
py -3 src\game.py
if errorlevel 1 pause
