@echo off

set Command=python ServidorCalc.py --port 12349 --debug

echo %Command%
%Command%

pause