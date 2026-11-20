@echo off
REM Build script for C++ module on Windows
echo Building C++ fast_math module...

cd cpp
if not exist build mkdir build
cd build

cmake .. -G "Visual Studio 17 2022" -A x64
if %ERRORLEVEL% NEQ 0 (
    echo CMake configuration failed. Trying with default generator...
    cmake ..
)

cmake --build . --config Release
if %ERRORLEVEL% EQU 0 (
    echo Build successful!
    echo Copying module to project root...
    copy Release\fast_math.pyd ..\..\fast_math.pyd 2>nul
    copy Release\fast_math.dll ..\..\fast_math.dll 2>nul
    if exist ..\..\fast_math.pyd (
        echo fast_math.pyd copied successfully!
    ) else if exist ..\..\fast_math.dll (
        echo fast_math.dll copied successfully!
    ) else (
        echo Warning: Could not find built module. Check build directory.
    )
) else (
    echo Build failed!
)

cd ..\..
pause

