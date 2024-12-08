#!/bin/bash

# Check if $1 is empty
if [ -z "$1" ]; then
  echo "Error: You must include a file name as the first argument. Missing argument. Please provide a value for \$1."
  exit 1
fi

#make the exe:
rm -rf dist
rm -rf .venv
rm -rf build
rm -rf __pycache__.py
rm -rf __pycache__

#pyinstaller --onefile --add-data "C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-SFM-Project\help;help" --hidden-import imports BBB_NMS_Save_File_Manipulator.py
pyinstaller BBB_NMS_Save_File_Manipulator.spec

mv dist/BBB_NMS_Save_File_Manipulator.exe dist/$1.exe

#let's make the zip:
rm -rf build/to_be_zipped
mkdir -p build/to_be_zipped/BBB_NMS_Save_File_Manipulator
cp setup.py MANIFEST.in requirements.txt build/to_be_zipped
cp *.py build/to_be_zipped/BBB_NMS_Save_File_Manipulator
cp *.json build/to_be_zipped/BBB_NMS_Save_File_Manipulator
cp -R help build/to_be_zipped/BBB_NMS_Save_File_Manipulator

cd build/to_be_zipped
7z a ../../build/$1.zip *
cd ../..

mv build/$1.zip dist
rm -rf build

