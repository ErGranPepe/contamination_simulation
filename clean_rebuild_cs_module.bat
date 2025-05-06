@echo off
echo Stopping any running Python processes...
taskkill /IM python.exe /F >nul 2>&1

echo Waiting for file release...
timeout /t 3 /nobreak >nul

echo Cleaning old build files...
if exist "src\modules\cs_module.cp311-win_amd64.pyd" (
    del /F /Q "src\modules\cs_module.cp311-win_amd64.pyd"
) else (
    echo No old cs_module.pyd found.
)

if exist "src\modules\build" (
    rmdir /S /Q "src\modules\build"
) else (
    echo No build directory found.
)

echo Rebuilding cs_module...
python "src\modules\cs_setup.py" build_ext --inplace

echo Copying new module to src\modules...
if exist "src\modules\build\lib.win-amd64-cpython-311\cs_module.cp311-win_amd64.pyd" (
    copy /Y "src\modules\build\lib.win-amd64-cpython-311\cs_module.cp311-win_amd64.pyd" "src\modules\"
) else (
    echo Build output file not found!
)

echo Done. Please restart your Python environment and run the simulation again.
pause
