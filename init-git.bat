@echo off
REM ---------------------------------------------------------------
REM  Initialise this folder as a git repository and make the first
REM  commit. Double-click this file, or run it from a terminal.
REM  Safe to run once; it refuses to re-run on an existing repo.
REM ---------------------------------------------------------------
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [X] git is not installed or not on PATH.
  echo     Install it from https://git-scm.com/download/win and run this again.
  pause & exit /b 1
)

if exist ".git" (
  echo [i] This folder is already a git repository - nothing to do.
  echo.
  git log --oneline -n 5
  pause & exit /b 0
)

echo [1/4] git init...
git init -b main >nul || (echo [X] git init failed & pause & exit /b 1)
git config core.autocrlf false
git config core.filemode false

echo [2/4] staging files...
git add -A

echo [3/4] committing...
> "%TEMP%\_pmsm_msg.txt" (
echo Estimate PMSM stator winding temperature from drive-measurable signals
echo.
echo A virtual sensor that replaces a physical winding thermocouple with a model
echo fed only by quantities a motor drive already measures for field-oriented
echo control ^(i_d, i_q, u_d, u_q, speed, torque, coolant, ambient^).
echo.
echo Approach:
echo - Drop stator_tooth / stator_yoke / pm as target leakage: they are the very
echo   sensors the estimator exists to replace, and sit millimetres from the
echo   winding in the same iron.
echo - Derive features from the lumped-parameter thermal ODE. Its solution is an
echo   exponentially weighted integral of past losses, so the feature set is EWMAs
echo   and EW standard deviations at five thermal time constants ^(30 s .. 3600 s^),
echo   computed per session. 8 raw channels -^> 104 features.
echo - Split profile-wise, holding out entire measurement sessions. At 2 Hz,
echo   consecutive rows are near-duplicates, so a random split leaks.
echo.
echo Results on held-out sessions ^(profiles 65 and 72^):
echo   MLP 2x128 -- RMSE 1.67 C, MAE 1.26 C, R2 0.9959, max error 9.84 C,
echo   81.3 %%%% of samples within +/-2 C.
echo.
echo Validation: an ablation isolating the EWMA contribution ^(R2 0.686 -^> 0.991^)
echo and a leakage study showing random splitting understates RMSE by ~3.8x.
)
git commit -F "%TEMP%\_pmsm_msg.txt" >nul || (echo [X] commit failed & pause & exit /b 1)
del "%TEMP%\_pmsm_msg.txt" >nul 2>nul

echo [4/4] done.
echo.
git log --stat --oneline -n 1
echo.
echo ================================================================
echo  Repository created. To publish it on GitHub:
echo.
echo    1. Create an EMPTY repo at https://github.com/new
echo         name:        pmsm-thermal-virtual-sensor
echo         description: see README
echo         do NOT tick "Add a README" / .gitignore / license
echo.
echo    2. Then run these two lines here:
echo         git remote add origin https://github.com/YOUR-USERNAME/pmsm-thermal-virtual-sensor.git
echo         git push -u origin main
echo.
echo  Note: measures_v2.csv is gitignored on purpose ^(~300 MB,
echo  over GitHub's file limit^). The README says where to get it.
echo ================================================================
echo.
pause
