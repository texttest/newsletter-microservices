set TEXTTEST_HOME=%~dp0
cd %TEXTTEST_HOME%
if not exist "venv" (
    py -3.9 -m venv venv
)
venv\Scripts\pip install -r requirements.txt
if %ERRORLEVEL% GEQ 1 (
    pause
) else (
    texttestc.exe
)