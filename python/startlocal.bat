@echo off

set "PY=python"

where python3 /Q && set "PY=python3"

echo Running main.py using "%PY%"
%PY% main.py