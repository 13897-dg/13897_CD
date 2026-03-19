@echo off

set Command=python ClienteHello.py --name localhost --port 12345 --arg "Computacao Distribuida"

echo %Command%
%Command%

pause