@echo off
REM Batch file for running Interest Rate Calculator tests on Windows

echo Interest Rate Calculator - Test Runner
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Parse command line arguments
set "COMMAND=smoke"
set "VERBOSE="
set "HEADLESS=--headless"

:parse_args
if "%~1"=="" goto run_tests
if "%~1"=="--setup" set "COMMAND=setup" & shift & goto parse_args
if "%~1"=="--all" set "COMMAND=all" & shift & goto parse_args
if "%~1"=="--unit" set "COMMAND=unit" & shift & goto parse_args
if "%~1"=="--integration" set "COMMAND=integration" & shift & goto parse_args
if "%~1"=="--web" set "COMMAND=web" & shift & goto parse_args
if "%~1"=="--desktop" set "COMMAND=desktop" & shift & goto parse_args
if "%~1"=="--smoke" set "COMMAND=smoke" & shift & goto parse_args
if "%~1"=="--performance" set "COMMAND=performance" & shift & goto parse_args
if "%~1"=="--verbose" set "VERBOSE=--verbose" & shift & goto parse_args
if "%~1"=="-v" set "VERBOSE=--verbose" & shift & goto parse_args
if "%~1"=="--headed" set "HEADLESS=--headed" & shift & goto parse_args
if "%~1"=="--coverage" set "COVERAGE=--coverage" & shift & goto parse_args
if "%~1"=="--watch" goto run_watch
shift
goto parse_args

:run_tests
echo Running %COMMAND% tests...
echo.

if "%COMMAND%"=="setup" (
    echo Installing test dependencies and setting up environment...
    python run_tests.py --setup
    if errorlevel 1 (
        echo Setup failed!
        pause
        exit /b 1
    )
    echo Setup completed successfully!
    pause
    exit /b 0
)

REM Run the specified tests
python run_tests.py --%COMMAND% %VERBOSE% %HEADLESS% %COVERAGE%

if errorlevel 1 (
    echo.
    echo Tests FAILED!
    echo Check the reports directory for detailed results.
) else (
    echo.
    echo Tests PASSED!
    echo Reports available in the reports directory.
)

echo.
pause
exit /b %errorlevel%

:run_watch
echo Starting test watch mode...
echo Press Ctrl+C to stop watching
python test_watch.py
pause
exit /b 0
