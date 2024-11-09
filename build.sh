#!/bin/bash

#make the exe:
rm -rf dist
rm -rf .venv
rm -rf build
pyinstaller --onefile --add-data "C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-SFM-Project\help;help" BBB_NMS_Save_File_Manipulator.py
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


