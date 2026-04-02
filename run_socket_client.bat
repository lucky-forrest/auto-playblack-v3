@echo off
chcp 65001 > nul
cd /d "%~dp0socket_client"
python main.py %*
