@echo off
echo off

set JAVA_HOME=C:\Java\jdk-21

rem call mvn exec:java

call mvn exec:java -Dexec.args="localhost 12345"

pause