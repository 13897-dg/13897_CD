@echo off

set Command=python ServidorCalc.py --port 12349

echo %Command%
%Command%

pause