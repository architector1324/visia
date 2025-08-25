#!/bin/bash

mkdir -p build

python -m venv ./build/venv
source ./build/venv/bin/activate

pip install --upgrade pip
pip install pillow ollama pyperclip pyperclipimg pyinstaller

cp ./vision.py -t build/
cd build

pyinstaller --onefile vision.py

mv dist/vision ../vision
