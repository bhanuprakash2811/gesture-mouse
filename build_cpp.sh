#!/bin/bash
# Build script for C++ module on Linux/macOS

echo "Building C++ fast_math module..."

cd cpp
mkdir -p build
cd build

cmake ..
if [ $? -ne 0 ]; then
    echo "CMake configuration failed!"
    exit 1
fi

make
if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Copying module to project root..."
    cp fast_math*.so ../../ 2>/dev/null
    cp fast_math*.dylib ../../ 2>/dev/null
    if [ -f ../../fast_math*.so ] || [ -f ../../fast_math*.dylib ]; then
        echo "Module copied successfully!"
    else
        echo "Warning: Could not find built module. Check build directory."
    fi
else
    echo "Build failed!"
    exit 1
fi

cd ../..

