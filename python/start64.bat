@echo off
setlocal enabledelayedexpansion

set "PY=python"

where python3 /Q && set "PY=python3"


set "TMPP=%CD:~0,2%\DATA\PortableApp\python3810x64\python.exe"
if exist "%TMPP%" (set "PY=%TMPP%")
echo %TMPP%


echo Running main.py using "%PY%"
%PY% main.py