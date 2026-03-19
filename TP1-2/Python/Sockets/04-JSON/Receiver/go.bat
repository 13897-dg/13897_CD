@echo off

set Command=python ReceiverJSON.py --port 12350

echo %Command%
%Command%

pause