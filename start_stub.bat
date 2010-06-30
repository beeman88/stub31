echo off

IF "%1"=="" (
echo "usage: start_stub port clear_uuids "
echo "start_stub 8080 y"
GOTO :EOF
)


copy c:\Python31\%1\BBSdata.ini C:\BBSdata.ini
stub.py %1 %2

:EOF