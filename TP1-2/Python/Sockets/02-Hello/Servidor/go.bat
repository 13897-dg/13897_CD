@echo off

set Command=python ServidorHello.py --port 12345

echo %Command%
%Command%

pause