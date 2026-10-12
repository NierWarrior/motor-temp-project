@echo off
REM ---------------------------------------------------------------
REM  Run the whole pipeline. Double-click this file, or from a
REM  terminal use run.py directly for more control:
REM      python run.py --help
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  where py >nul 2>nul
  if errorlevel 1 (
    echo [X] Python is not installed or not on PATH.
    echo     Get it from https://www.python.org/downloads/ and tick
    echo     "Add python.exe to PATH" during install.
    pause & exit /b 1
  )
  set PY=py
) else (
  set PY=python
)

echo Checking environment...
echo.
%PY% run.py --check
if errorlevel 1 (
  echo.
  set /p INSTALL="Install the required packages now? [y/N] "
  if /i "%INSTALL%"=="y" (
    %PY% -m pip install -r requirements.txt
    echo.
    %PY% run.py --check
    if errorlevel 1 (
      echo.
      echo [X] Still not ready - see the messages above.
      echo     Most likely measures_v2.csv is missing; the README says where to get it.
      pause & exit /b 1
    )
  ) else (
    pause & exit /b 1
  )
)

echo.
echo ================================================================
echo  A full run takes roughly 20-30 minutes.
echo  For a 2-minute smoke test instead, run:  python run.py --quick
echo ================================================================
echo.
set /p GO="Run the full pipeline now? [Y/n] "
if /i "%GO%"=="n" (
  echo Cancelled.
  pause & exit /b 0
)

%PY% run.py
echo.
pause
